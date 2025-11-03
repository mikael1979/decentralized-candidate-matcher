#!/usr/bin/env python3
"""
Metadata Manager - KORJATTU VERSIO
Hallinnoi järjestelmän metatietoja ja koneiden identiteettejä
"""

import json
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

class MetadataManager:
    """Hallinnoi järjestelmän metatietoja"""
    
    def __init__(self, runtime_dir: str = "runtime"):
        self.runtime_dir = Path(runtime_dir)
        self.runtime_dir.mkdir(exist_ok=True)
        self.machine_id = self._get_or_create_machine_id()
    
    def _get_or_create_machine_id(self) -> str:
        """Hae tai luo koneen yksilöllinen ID"""
        machine_id_file = self.runtime_dir / "machine_id.json"
        
        if machine_id_file.exists():
            try:
                with open(machine_id_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return data.get('machine_id', self._generate_machine_id())
            except:
                return self._generate_machine_id()
        else:
            return self._generate_machine_id()
    
    def _generate_machine_id(self) -> str:
        """Luo uusi kone-ID"""
        machine_id = f"machine_{uuid.uuid4().hex[:16]}"
        
        # Tallenna kone-ID
        machine_id_file = self.runtime_dir / "machine_id.json"
        with open(machine_id_file, 'w', encoding='utf-8') as f:
            json.dump({
                'machine_id': machine_id,
                'created': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        return machine_id
    
    def initialize_system_metadata(self, election_id: str, first_install: bool = False) -> Dict[str, Any]:
        """Alusta järjestelmän metadata"""
        
        # Luo system_metadata.json
        system_metadata = {
            "election_specific": {
                "election_id": election_id,
                "machine_id": self.machine_id,
                "installed_at": datetime.now().isoformat(),
                "first_install": first_install
            },
            "node_info": {
                "node_id": self.machine_id,
                "role": "master" if first_install else "worker",
                "capabilities": ["comparisons", "voting", "sync"],
                "ipfs_available": False
            },
            "version": "1.0.0",
            "metadata": {
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
        }
        
        with open(self.runtime_dir / "system_metadata.json", 'w', encoding='utf-8') as f:
            json.dump(system_metadata, f, indent=2, ensure_ascii=False)
        
        return system_metadata
    
    def get_machine_info(self) -> Dict[str, Any]:
        """Hae koneen tiedot"""
        system_metadata_file = self.runtime_dir / "system_metadata.json"
        
        if system_metadata_file.exists():
            try:
                with open(system_metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                election_id = data.get('election_specific', {}).get('election_id', 'unknown')
                first_install = data.get('election_specific', {}).get('first_install', False)
                
                return {
                    'machine_id': self.machine_id,
                    'election_id': election_id,
                    'first_install': first_install,
                    'is_master': first_install,
                    'node_role': 'master' if first_install else 'worker'
                }
            except:
                pass
        
        # Fallback, jos metadataa ei ole
        return {
            'machine_id': self.machine_id,
            'election_id': 'unknown',
            'first_install': False,
            'is_master': False,
            'node_role': 'unknown'
        }
    
    def create_election_registry(self, election: Dict[str, Any]) -> Dict[str, Any]:
        """Luo vaalirekisterin ensimmäiselle asennukselle"""
        
        registry = {
            "election_registry": {
                "election_id": election["election_id"],
                "election_name": election["name"]["fi"],
                "master_machine_id": self.machine_id,
                "created_at": datetime.now().isoformat(),
                "worker_nodes": [],
                "config_hash": self._calculate_config_hash(election)
            },
            "metadata": {
                "version": "1.0.0",
                "registry_type": "election_master"
            }
        }
        
        return registry
    
    def _calculate_config_hash(self, election: Dict[str, Any]) -> str:
        """Laske vaalikonfiguraation hash"""
        config_string = json.dumps(election, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(config_string.encode('utf-8')).hexdigest()
    
    def register_worker_node(self, worker_machine_id: str, election_id: str) -> bool:
        """Rekisteröi työasema vaalirekisteriin"""
        
        registry_file = self.runtime_dir / "election_registry.json"
        
        if not registry_file.exists():
            print("❌ Vaalirekisteriä ei löydy - oletko master-kone?")
            return False
        
        try:
            with open(registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            
            # Tarkista että oikea vaali
            if registry["election_registry"]["election_id"] != election_id:
                print(f"❌ Väärä vaali rekisterissä: {registry['election_registry']['election_id']}")
                return False
            
            # Lisää työasema
            worker_nodes = registry["election_registry"].get("worker_nodes", [])
            if worker_machine_id not in worker_nodes:
                worker_nodes.append(worker_machine_id)
                registry["election_registry"]["worker_nodes"] = worker_nodes
                registry["election_registry"]["last_updated"] = datetime.now().isoformat()
                
                with open(registry_file, 'w', encoding='utf-8') as f:
                    json.dump(registry, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Työasema rekisteröity: {worker_machine_id}")
                return True
            else:
                print(f"ℹ️  Työasema on jo rekisteröity: {worker_machine_id}")
                return True
                
        except Exception as e:
            print(f"❌ Virhe rekisteröitäessä työasemaa: {e}")
            return False
    
    def get_election_registry(self) -> Optional[Dict[str, Any]]:
        """Hae vaalirekisteri"""
        registry_file = self.runtime_dir / "election_registry.json"
        
        if registry_file.exists():
            try:
                with open(registry_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return None
    
    def update_system_metadata(self, updates: Dict[str, Any]) -> bool:
        """Päivitä järjestelmän metadataa"""
        
        system_metadata_file = self.runtime_dir / "system_metadata.json"
        
        if not system_metadata_file.exists():
            print("❌ System metadataa ei löydy")
            return False
        
        try:
            with open(system_metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Päivitä data
            for key, value in updates.items():
                if key in data:
                    if isinstance(data[key], dict) and isinstance(value, dict):
                        data[key].update(value)
                    else:
                        data[key] = value
                else:
                    data[key] = value
            
            # Päivitä timestamp
            data['metadata']['last_updated'] = datetime.now().isoformat()
            
            with open(system_metadata_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print("✅ System metadata päivitetty")
            return True
            
        except Exception as e:
            print(f"❌ Virhe päivittäessä metadataa: {e}")
            return False

# Singleton instance
_metadata_manager = None

def get_metadata_manager(runtime_dir: str = "runtime") -> MetadataManager:
    """Hae MetadataManager-instanssi"""
    global _metadata_manager
    if _metadata_manager is None:
        _metadata_manager = MetadataManager(runtime_dir)
    return _metadata_manager

# Testaus
if __name__ == "__main__":
    manager = MetadataManager()
    info = manager.get_machine_info()
    
    print("💻 KONEEN TIEDOT:")
    print(f"   Machine ID: {info['machine_id']}")
    print(f"   Vaali ID: {info['election_id']}")
    print(f"   Rooli: {info['node_role']}")
    print(f"   Master: {info['is_master']}")
