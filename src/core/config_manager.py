# src/core/config_manager.py
#!/usr/bin/env python3
"""
Vaalikohtaisen konfiguraation hallinta - PÄIVITETTY TAQ-integroinnilla
Nyt tukee turvallisia config-päivityksiä TAQ-kvoorumin kautta
"""
import json
import os
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

class ConfigManager:
    """Konfiguraatiohallinta TAQ-integroidulla config-päivityksellä"""
    
    def __init__(self, election_id: str = None):
        self.election_id = election_id
        self.base_path = Path("config/elections")
        
    def get_election_config(self, election_id: str = None) -> Optional[Dict]:
        """Hae vaalikohtainen konfiguraatio"""
        target_election = election_id or self.election_id
        if not target_election:
            return None
            
        config_file = self.base_path / target_election / "election_config.json"
        
        if not config_file.exists():
            print(f"⚠️  Config-tiedostoa ei löydy: {config_file}")
            return self._create_default_config(target_election)
            
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                
            # Varmista configin eheys
            if not self._verify_config_integrity(config_data):
                print("⚠️  Config-tiedoston eheys epäilyttävä")
                return None
                
            return config_data
            
        except Exception as e:
            print(f"❌ Config-tiedoston lukuvirhe: {e}")
            return None
    
    def _create_default_config(self, election_id: str) -> Dict:
        """Luo oletuskonfiguraatio jos ei ole olemassa"""
        default_config = {
            "election": {
                "id": election_id,
                "name": {
                    "fi": f"Vaalit {election_id}",
                    "en": f"Election {election_id}",
                    "sv": f"Val {election_id}"
                },
                "max_questions": 20,
                "max_candidates": 50,
                "answer_scale": {
                    "min": -5,
                    "max": 5,
                    "step": 1
                },
                "supported_languages": ["fi", "en", "sv"],
                "timelock_enabled": True,
                "edit_deadline": "2026-02-28T23:59:59"
            },
            "system_info": {
                "system_id": f"system_{election_id}",
                "version": "2.0.0",
                "created": datetime.now().isoformat()
            },
            "security_measures": {
                "rate_limiting": True,
                "max_answers_per_candidate": 100,
                "crypto_requirements": "RSA-2048"
            },
            "network_config": {
                "min_nodes": 3,
                "sync_interval": 3600,
                "ipfs_gateway": "https://ipfs.io/ipfs"
            },
            "ui": {
                "default_theme": "light",
                "supported_themes": ["light", "dark", "blue"],
                "results_public": True
            },
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "config_hash": "",
                "update_history": []
            }
        }
        
        # Laske hash ja tallenna
        default_config["metadata"]["config_hash"] = self._calculate_config_hash(default_config)
        
        # Tallenna tiedosto
        config_dir = self.base_path / election_id
        config_dir.mkdir(parents=True, exist_ok=True)
        
        config_file = config_dir / "election_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
            
        print(f"✅ Luotiin oletusconfig: {config_file}")
        return default_config
    
    def update_config_with_taq(self, changes: Dict, update_type: str, 
                              justification: str, node_id: str, 
                              election_id: str = None) -> Dict:
        """Päivitä config-tiedosto TAQ-kvoorumin kautta - KORJATTU VERSIO"""
        
        target_election = election_id or self.election_id
        if not target_election:
            return {
                "status": "error",
                "error": "Vaalia ei ole määritelty",
                "message": "Config-päivitys epäonnistui"
            }
        
        try:
            # 1. Tarkista nykyinen config
            current_config = self.get_election_config(target_election)
            if not current_config:
                raise ValueError("Nykyistä config-tiedostoa ei löydy")
            
            # 2. Alusta TAQ-config manager
            try:
                from managers.taq_config_manager import TAQConfigManager
                taq_config = TAQConfigManager(target_election)
            except ImportError as e:
                print(f"⚠️  TAQConfigManager ei saatavilla: {e}")
                return {
                    "status": "error", 
                    "error": "TAQ-config-manager ei saatavilla",
                    "message": "Asenna tarvittavat moduulit"
                }
            
            # 3. Tarkista muutosten kelvollisuus
            if not self._validate_config_changes(changes, current_config):
                raise ValueError("Muutokset eivät ole kelvollisia")
            
            # 4. Ehdotta päivitystä - KORJATTU: käytä update_type suoraan
            proposal_id = taq_config.propose_config_update(
                changes, update_type, justification, node_id  # EI config_update_-etuliitettä
            )
            
            # 5. Tarkista eheys ennen tallennusta
            try:
                from managers.enhanced_integrity_manager import EnhancedIntegrityManager
                integrity = EnhancedIntegrityManager(target_election)
                
                proposed_config = taq_config._apply_changes_to_config(current_config, changes)
                if not integrity.verify_config_integrity(proposed_config):
                    raise ValueError("Päivitetty config ei läpäise eheystarkistusta")
            except ImportError as e:
                print(f"⚠️  EnhancedIntegrityManager ei saatavilla, ohitetaan eheystarkistus: {e}")
            
            return {
                "status": "proposed",
                "proposal_id": proposal_id,
                "message": "Config-päivitys on esitetty TAQ-kvoorumille",
                "next_steps": [
                    "Odottaa nodejen äänestystä",
                    f"Tarkista status: python src/cli/manage_config.py status --proposal-id {proposal_id}",
                    "Voit äänestää itse: python src/cli/manage_config.py vote",
                    f"Vaali: {target_election}"
                ],
                "changes": changes,
                "update_type": update_type,
                "proposer_node": node_id
            }
            
        except Exception as e:
            print(f"❌ Config-päivitys epäonnistui: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Config-päivitys epäonnistui"
            }
    
    def apply_approved_config_update(self, proposal_data: Dict, election_id: str = None) -> bool:
        """Toteuta hyväksytty config-päivitys"""
        
        target_election = election_id or self.election_id
        if not target_election:
            return False
        
        try:
            # 1. Hae nykyinen config
            current_config = self.get_election_config(target_election)
            if not current_config:
                return False
            
            # 2. Toteuta muutokset
            changes = proposal_data["changes"]
            updated_config = self._apply_changes_to_config(current_config, changes)
            
            # 3. Päivitä metadata
            updated_config["metadata"]["last_updated"] = datetime.now().isoformat()
            updated_config["metadata"]["config_hash"] = self._calculate_config_hash(updated_config)
            
            # Lisää historiaan
            history_entry = {
                "timestamp": datetime.now().isoformat(),
                "proposal_id": proposal_data["proposal_id"],
                "changes": changes,
                "approved_by": proposal_data.get("approved_by", []),
                "justification": proposal_data.get("justification", "")
            }
            updated_config["metadata"]["update_history"].append(history_entry)
            
            # 4. Tallenna uusi config
            config_file = self.base_path / target_election / "election_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(updated_config, f, indent=2, ensure_ascii=False)
            
            # 5. Varmista eheys tallennuksen jälkeen
            if not self._verify_config_integrity(updated_config):
                print("⚠️  Tallennetun configin eheys epäilyttävä")
                return False
            
            print(f"✅ CONFIG PÄIVITETTY: {proposal_data['proposal_id']}")
            print(f"📁 Tiedosto: {config_file}")
            print(f"📊 Muutokset: {len(changes)} kohdetta")
            
            return True
            
        except Exception as e:
            print(f"❌ Config-päivityksen toteutus epäonnistui: {e}")
            return False
    
    def _validate_config_changes(self, changes: Dict, current_config: Dict) -> bool:
        """Tarkista config-muutosten kelvollisuus"""
        
        for key, new_value in changes.items():
            # Tarkista että avain on olemassa nykyisessä configissa
            current_value = self._get_nested_value(current_config, key)
            if current_value is None:
                print(f"⚠️  Tuntematon config-avain: {key}")
                return False
            
            # Tarkista arvojen kelvollisuus
            if not self._validate_config_value(key, new_value):
                print(f"⚠️  Virheellinen arvo avaimelle {key}: {new_value}")
                return False
        
        return True
    
    def _validate_config_value(self, key: str, value: Any) -> bool:
        """Tarkista yksittäisen config-arvon kelvollisuus"""
        
        validation_rules = {
            "max_questions": lambda v: isinstance(v, int) and 5 <= v <= 100,
            "max_candidates": lambda v: isinstance(v, int) and 10 <= v <= 200,
            "security_measures.rate_limiting": lambda v: isinstance(v, bool),
            "ui.default_theme": lambda v: v in ["light", "dark", "blue"],
            "answer_scale.min": lambda v: isinstance(v, int) and -10 <= v <= 0,
            "answer_scale.max": lambda v: isinstance(v, int) and 0 <= v <= 10
        }
        
        # Etsi sääntö key:lle
        for rule_key, rule_func in validation_rules.items():
            if key == rule_key or key.startswith(rule_key + "."):
                return rule_func(value)
        
        # Oletus: hyväksy kaikki muut arvot
        return True
    
    def _get_nested_value(self, config: Dict, key: str) -> Any:
        """Hae arvo nested-rakenteesta piste-erotellulla avaimella"""
        keys = key.split('.')
        current = config
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
                
        return current
    
    def _apply_changes_to_config(self, config: Dict, changes: Dict) -> Dict:
        """Toteuta muutokset config-objektiin"""
        import copy
        updated_config = copy.deepcopy(config)
        
        for key, new_value in changes.items():
            self._set_nested_value(updated_config, key, new_value)
            
        return updated_config
    
    def _set_nested_value(self, config: Dict, key: str, value: Any):
        """Aseta arvo nested-rakenteeseen piste-erotellulla avaimella"""
        keys = key.split('.')
        current = config
        
        # Navigoi viimeiseen tasoon asti
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # Aseta arvo
        current[keys[-1]] = value
    
    def _verify_config_integrity(self, config_data: Dict) -> bool:
        """Tarkista config-tiedoston eheys"""
        try:
            # Tarkista perusrakenne
            required_sections = ["election", "system_info", "metadata"]
            if not all(section in config_data for section in required_sections):
                return False
            
            # Tarkista hash (jos saatavilla)
            if "config_hash" in config_data.get("metadata", {}):
                expected_hash = config_data["metadata"]["config_hash"]
                actual_hash = self._calculate_config_hash(config_data)
                if expected_hash and expected_hash != actual_hash:
                    print(f"❌ Config-hash ei täsmää: {expected_hash} vs {actual_hash}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ Config-eheystarkistus epäonnistui: {e}")
            return False
    
    def _calculate_config_hash(self, config_data: Dict) -> str:
        """Laske config-tiedoston tiiviste"""
        # Poista dynaamiset kentät ennen hashin laskentaa
        config_copy = config_data.copy()
        metadata = config_copy.get("metadata", {})
        metadata.pop("last_updated", None)
        metadata.pop("config_hash", None)
        
        config_string = json.dumps(config_copy, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(config_string.encode()).hexdigest()
    
    def get_config_update_history(self, election_id: str = None) -> List[Dict]:
        """Hae config-päivityshistoria"""
        target_election = election_id or self.election_id
        if not target_election:
            return []
        
        config = self.get_election_config(target_election)
        if not config:
            return []
        
        return config.get("metadata", {}).get("update_history", [])
    
    def get_config_info(self, election_id: str = None) -> Dict:
        """Hae config-tiedoston perustiedot"""
        target_election = election_id or self.election_id
        if not target_election:
            return {}
        
        config = self.get_election_config(target_election)
        if not config:
            return {}
        
        return {
            "election_id": target_election,
            "config_hash": config.get("metadata", {}).get("config_hash", "unknown"),
            "last_updated": config.get("metadata", {}).get("last_updated", "unknown"),
            "update_count": len(config.get("metadata", {}).get("update_history", [])),
            "max_questions": config.get("election", {}).get("max_questions", 0),
            "max_candidates": config.get("election", {}).get("max_candidates", 0)
        }


# Yleiset apufunktiot
def get_election_id(election_param: str = None) -> str:
    """Hae vaalitunniste parametrista tai configista"""
    if election_param:
        return election_param
    
    # Yritä lukea nykyinen vaali configista
    try:
        config_manager = ConfigManager()
        config = config_manager.get_election_config()
        if config:
            return config.get("election", {}).get("id", "Jumaltenvaalit2026")
    except:
        pass
    
    return "Jumaltenvaalit2026"

def get_data_path(election_id: str = None) -> Path:
    """Hae data-polku vaalille"""
    target_election = election_id or get_election_id()
    return Path(f"data/elections/{target_election}")

def validate_election_config(config_data: Dict) -> bool:
    """Validoi vaalikonfiguraatio (ulkopuolinen käyttö)"""
    manager = ConfigManager()
    return manager._verify_config_integrity(config_data)

