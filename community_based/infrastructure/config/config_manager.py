#!/usr/bin/env python3
"""
Config Manager - TÄYDELLINEN VERSIO
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from datetime import timezone

class ConfigManager:
    """Hallinnoi järjestelmän konfiguraatiota"""
    
    def __init__(self, runtime_dir: str = "runtime"):
        self.runtime_dir = Path(runtime_dir)
        self.runtime_dir.mkdir(exist_ok=True)
    
    def get_machine_info(self) -> Dict[str, Any]:
        """Hae koneen tiedot"""
        try:
            machine_file = self.runtime_dir / "machine_id.json"
            if machine_file.exists():
                with open(machine_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # Luo uusi machine_id
            return self._generate_machine_id()
        except Exception as e:
            return {
                "machine_id": "error_machine",
                "error": str(e)
            }
    
    def _generate_machine_id(self) -> Dict[str, Any]:
        """Luo uusi kone-ID"""
        import uuid
        machine_id = f"machine_{uuid.uuid4().hex[:16]}"
        
        machine_data = {
            "machine_id": machine_id,
            "created": datetime.now(timezone.utc).isoformat(),
            "version": "2.0.0",
            "architecture": "modern"
        }
        
        # Tallenna
        machine_file = self.runtime_dir / "machine_id.json"
        with open(machine_file, 'w', encoding='utf-8') as f:
            json.dump(machine_data, f, indent=2, ensure_ascii=False)
        
        return machine_data
    
    def update_machine_info(self, updates: Dict[str, Any]) -> bool:
        """Päivitä koneen tietoja"""
        try:
            current_info = self.get_machine_info()
            current_info.update(updates)
            current_info["last_updated"] = datetime.now(timezone.utc).isoformat()
            
            machine_file = self.runtime_dir / "machine_id.json"
            with open(machine_file, 'w', encoding='utf-8') as f:
                json.dump(current_info, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"❌ Virhe päivittäessä koneen tietoja: {e}")
            return False
    
    def get_system_metadata(self) -> Dict[str, Any]:
        """Hae järjestelmän metadata"""
        try:
            meta_file = self.runtime_dir / "system_metadata.json"
            if meta_file.exists():
                with open(meta_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # Luo oletusmetadata
            default_meta = {
                "system_id": "unknown_system",
                "created": datetime.now(timezone.utc).isoformat(),
                "version": "2.0.0"
            }
            
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(default_meta, f, indent=2, ensure_ascii=False)
            
            return default_meta
        except Exception as e:
            return {"error": str(e)}
    
    def update_system_metadata(self, updates: Dict[str, Any]) -> bool:
        """Päivitä järjestelmän metadataa"""
        try:
            current_meta = self.get_system_metadata()
            current_meta.update(updates)
            current_meta["last_updated"] = datetime.now(timezone.utc).isoformat()
            
            meta_file = self.runtime_dir / "system_metadata.json"
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(current_meta, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"❌ Virhe päivittäessä metadataa: {e}")
            return False
    
    def get_sync_config(self) -> Dict[str, Any]:
        """Hae synkronointikonfiguraatio"""
        try:
            sync_file = self.runtime_dir / "sync_config.json"
            if sync_file.exists():
                with open(sync_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # Oletuskonfiguraatio
            default_config = {
                "batch_size": 5,
                "max_batch_size": 20,
                "time_interval_hours": 24,
                "auto_sync_enabled": True
            }
            
            with open(sync_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            
            return default_config
        except Exception as e:
            return {"error": str(e)}
    
    def update_sync_config(self, updates: Dict[str, Any]) -> bool:
        """Päivitä synkronointikonfiguraatiota"""
        try:
            current_config = self.get_sync_config()
            current_config.update(updates)
            
            sync_file = self.runtime_dir / "sync_config.json"
            with open(sync_file, 'w', encoding='utf-8') as f:
                json.dump(current_config, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"❌ Virhe päivittäessä synkronointikonfiguraatiota: {e}")
            return False
    
    def get_election_registry(self) -> Optional[Dict[str, Any]]:
        """Hae vaalirekisteri"""
        try:
            registry_file = self.runtime_dir / "election_registry.json"
            if registry_file.exists():
                with open(registry_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except:
            return None
    
    def update_election_registry(self, registry: Dict[str, Any]) -> bool:
        """Päivitä vaalirekisteri"""
        try:
            registry_file = self.runtime_dir / "election_registry.json"
            with open(registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Virhe päivittäessä vaalirekisteriä: {e}")
            return False
    
    def get_namespace_info(self) -> Dict[str, str]:
        """Hae nimiavaruuden tiedot"""
        try:
            meta = self.get_system_metadata()
            election_specific = meta.get('election_specific', {})
            
            return {
                "election_id": election_specific.get('election_id', 'unknown'),
                "namespace": election_specific.get('namespace', 'unknown'),
                "machine_id": self.get_machine_info().get('machine_id', 'unknown')
            }
        except:
            return {
                "election_id": "unknown",
                "namespace": "unknown", 
                "machine_id": "unknown"
            }
    
    def verify_namespace_integrity(self) -> Dict[str, Any]:
        """Tarkista nimiavaruuden eheys"""
        try:
            namespace_info = self.get_namespace_info()
            machine_info = self.get_machine_info()
            
            # Yksinkertainen eheystarkistus
            issues = []
            
            if namespace_info['election_id'] == 'unknown':
                issues.append("Election ID not set")
            
            if machine_info.get('machine_id') == 'error_machine':
                issues.append("Machine ID error")
            
            return {
                "success": len(issues) == 0,
                "namespace": namespace_info['namespace'],
                "issues": issues,
                "machine_id": machine_info.get('machine_id')
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
