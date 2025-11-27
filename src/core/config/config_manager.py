#!/usr/bin/env python3
"""
MODULAARINEN CONFIG-HALLINTA - PÄIVITETTY ISOLATION TUKEELLA
"""
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib
import json

from .persistence.config_loader import ConfigLoader
from .validators.change_validator import ChangeValidator
from .processors.nested_data_handler import NestedDataHandler
from .integration.taq_integrator import TAQIntegrator


class ConfigManager:
    """Modulaarinen konfiguraatiohallinta - parannettu eristyksellä"""
    
    def __init__(self, election_id: str = None):
        self.election_id = election_id
        self.loader = ConfigLoader()
        self.validator = ChangeValidator()
        self.nested_handler = NestedDataHandler()
        self._taq_integrator = None
        self._isolation_manager = None
    
    def _get_isolation_manager(self):
        """Hae ElectionIsolationManager (lazy loading)"""
        if self._isolation_manager is None:
            try:
                from core.election_isolation_manager import ElectionIsolationManager
                self._isolation_manager = ElectionIsolationManager()
            except ImportError:
                self._isolation_manager = None
        return self._isolation_manager
    
    def get_election_config(self, election_id: str = None) -> Optional[Dict]:
        """Hae vaalikohtainen konfiguraatio - parannettu eristyksellä"""
        target_election = election_id or self.election_id
        if not target_election:
            return None
        
        # Tarkista eristys ennen configin hakua
        isolation_mgr = self._get_isolation_manager()
        if isolation_mgr:
            isolation_check = isolation_mgr.validate_election_isolation(target_election, "config_read")
            if not isolation_check["is_safe"]:
                print(f"🚨 VAROITUS: Eristystarkistus epäonnistui vaalille {target_election}")
                for risk in isolation_check["risk_details"]:
                    print(f"   - {risk}")
        
        # Lataa config tiedostosta
        config = self.loader.load_election_config(target_election)
        
        # Jos configia ei ole, luo oletus
        if not config:
            config = self._create_default_config(target_election)
            self.loader.save_election_config(target_election, config)
        
        # Tarkista eheys
        if not self._verify_config_integrity(config):
            print("⚠️  Config-tiedoston eheys epäilyttävä")
            return None
        
        return config
    
    def update_config_with_taq(self, changes: Dict, update_type: str, 
                              justification: str, node_id: str, 
                              election_id: str = None) -> Dict:
        """Päivitä config TAQ-kvoorumin kautta - parannettu eristyksellä"""
        target_election = election_id or self.election_id
        if not target_election:
            return self._error_response("Vaalia ei ole määritelty")
        
        # Hae ja käytä isolation manageriä
        isolation_mgr = self._get_isolation_manager()
        if isolation_mgr:
            # Yritä halua lukko vaalille
            if not isolation_mgr.acquire_election_lock(target_election, "config_update"):
                return self._error_response(f"Vaali {target_election} on jo käytössä toisessa operaatiosaa")
            
            try:
                return self._perform_config_update(target_election, changes, update_type, justification, node_id)
            finally:
                # Vapauta lukko aina
                isolation_mgr.release_election_lock(target_election)
        else:
            # Fallback: suorita ilman lukkoja
            return self._perform_config_update(target_election, changes, update_type, justification, node_id)
    
    def _perform_config_update(self, target_election: str, changes: Dict, update_type: str,
                             justification: str, node_id: str) -> Dict:
        """Suorita config-päivitys (sisäinen metodi)"""
        try:
            # 1. Hae nykyinen config
            current_config = self.get_election_config(target_election)
            if not current_config:
                return self._error_response("Nykyistä config-tiedostoa ei löydy")
            
            # 2. Validoi muutokset
            if not self.validator.validate_changes(changes, current_config):
                errors = self.validator.get_change_errors(changes, current_config)
                return self._error_response(f"Virheelliset muutokset: {', '.join(errors)}")
            
            # 3. Alusta TAQ-integraatio
            taq_integrator = self._get_taq_integrator(target_election)
            if not taq_integrator or not taq_integrator.is_available():
                return self._error_response("TAQ-integrointi ei saatavilla")
            
            # 4. Ehdotta päivitystä
            proposal_id = taq_integrator.propose_config_update(
                changes, update_type, justification, node_id
            )
            
            if not proposal_id:
                return self._error_response("Päivitysehdotuksen luonti epäonnistui")
            
            return {
                "status": "proposed",
                "proposal_id": proposal_id,
                "message": "Config-päivitys on esitetty TAQ-kvoorumille",
                "changes": changes,
                "update_type": update_type,
                "proposer_node": node_id
            }
            
        except Exception as e:
            return self._error_response(f"Config-päivitys epäonnistui: {e}")
    
    def _get_taq_integrator(self, election_id: str):
        """Hae TAQ-integraattori (lazy loading)"""
        if self._taq_integrator is None:
            self._taq_integrator = TAQIntegrator(election_id)
        return self._taq_integrator
    
    def _verify_config_integrity(self, config_data: Dict) -> bool:
        """Tarkista config-tiedoston eheys"""
        try:
            required_sections = ["election", "system_info", "metadata"]
            if not all(section in config_data for section in required_sections):
                return False
            
            # Tarkista hash
            if "config_hash" in config_data.get("metadata", {}):
                expected_hash = config_data["metadata"]["config_hash"]
                actual_hash = self._calculate_config_hash(config_data)
                if expected_hash and expected_hash != actual_hash:
                    return False
            
            return True
        except Exception:
            return False
    
    def _calculate_config_hash(self, config_data: Dict) -> str:
        """Laske config-tiedoston tiiviste"""
        config_copy = config_data.copy()
        metadata = config_copy.get("metadata", {})
        metadata.pop("last_updated", None)
        metadata.pop("config_hash", None)
        
        config_string = json.dumps(config_copy, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(config_string.encode()).hexdigest()
    
    def _create_default_config(self, election_id: str) -> Dict:
        """Luo oletuskonfiguraatio"""
        default_config = {
            "election": {
                "id": election_id,
                "name": {"fi": f"Vaalit {election_id}", "en": f"Election {election_id}", "sv": f"Val {election_id}"},
                "max_questions": 20,
                "max_candidates": 50,
                "answer_scale": {"min": -5, "max": 5, "step": 1},
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
        
        # Laske hash
        default_config["metadata"]["config_hash"] = self._calculate_config_hash(default_config)
        return default_config
    
    def _error_response(self, error_message: str) -> Dict:
        """Luo virheviesti"""
        return {
            "status": "error",
            "error": error_message,
            "message": "Config-päivitys epäonnistui"
        }
    
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
