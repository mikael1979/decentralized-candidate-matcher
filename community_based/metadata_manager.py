#!/usr/bin/env python3
"""
Metadata Manager - PÄIVITETTY VERSIO
Hallinnoi järjestelmän metatietoja ja koneiden identiteettejä
Nimiavaruuden hallinta eri vaaleille
"""

import json
import uuid
import hashlib
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Dict, Any, Optional

class MetadataManager:
    """Hallinnoi järjestelmän metatietoja - PÄIVITETTY NIMIAVARUUDILLA"""
    
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
                'created': datetime.now(timezone.utc).isoformat(),
                'version': '2.0.0'
            }, f, indent=2, ensure_ascii=False)
        
        return machine_id
    
    def initialize_system_metadata(self, election_id: str, first_install: bool = False) -> Dict[str, Any]:
        """Alusta järjestelmän metadata - PÄIVITETTY NIMIAVARUUDELLA"""
        
        # Luo vaalikohtainen nimiavaruus
        namespace = f"election_{election_id}_{datetime.now().strftime('%Y%m%d')}"
        
        # Luo system_metadata.json
        system_metadata = {
            "election_specific": {
                "election_id": election_id,
                "namespace": namespace,
                "machine_id": self.machine_id,
                "installed_at": datetime.now(timezone.utc).isoformat(),
                "first_install": first_install,
                "node_type": "master" if first_install else "worker"
            },
            "node_info": {
                "node_id": self.machine_id,
                "role": "master" if first_install else "worker",
                "capabilities": ["comparisons", "voting", "sync", "ipfs_blocks"],
                "ipfs_available": False,
                "namespace": namespace
            },
            "version": "2.0.0",
            "metadata": {
                "created": datetime.now(timezone.utc).isoformat(),
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "namespace_strategy": "election_id_timestamp"
            }
        }
        
        with open(self.runtime_dir / "system_metadata.json", 'w', encoding='utf-8') as f:
            json.dump(system_metadata, f, indent=2, ensure_ascii=False)
        
        print(f"✅ System metadata alustettu - Nimiavaruus: {namespace}")
        return system_metadata
    
    def get_machine_info(self) -> Dict[str, Any]:
        """Hae koneen tiedot - PÄIVITETTY"""
        system_metadata_file = self.runtime_dir / "system_metadata.json"
        
        if system_metadata_file.exists():
            try:
                with open(system_metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                election_specific = data.get('election_specific', {})
                election_id = election_specific.get('election_id', 'unknown')
                namespace = election_specific.get('namespace', 'unknown')
                first_install = election_specific.get('first_install', False)
                
                return {
                    'machine_id': self.machine_id,
                    'election_id': election_id,
                    'namespace': namespace,
                    'first_install': first_install,
                    'is_master': first_install,
                    'node_role': 'master' if first_install else 'worker',
                    'node_type': election_specific.get('node_type', 'unknown')
                }
            except:
                pass
        
        # Fallback, jos metadataa ei ole
        return {
            'machine_id': self.machine_id,
            'election_id': 'unknown',
            'namespace': 'unknown',
            'first_install': False,
            'is_master': False,
            'node_role': 'unknown',
            'node_type': 'unknown'
        }
    
    def create_election_registry(self, election: Dict[str, Any]) -> Dict[str, Any]:
        """Luo vaalirekisterin ensimmäiselle asennukselle - PÄIVITETTY"""
        
        namespace = f"election_{election['election_id']}_{datetime.now().strftime('%Y%m%d')}"
        
        registry = {
            "election_registry": {
                "election_id": election["election_id"],
                "election_name": election["name"]["fi"],
                "master_machine_id": self.machine_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "namespace": namespace,
                "worker_nodes": [],
                "config_hash": self._calculate_config_hash(election),
                "ipfs_cid_mapping": {},
                "status": "active"
            },
            "metadata": {
                "version": "2.0.0",
                "registry_type": "election_master",
                "namespace_strategy": "election_id_timestamp",
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        }
        
        # Tallenna rekisteri
        registry_file = self.runtime_dir / "election_registry.json"
        with open(registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Vaalirekisteri luotu - Nimiavaruus: {namespace}")
        return registry
    
    def _calculate_config_hash(self, election: Dict[str, Any]) -> str:
        """Laske vaalikonfiguraation hash"""
        config_string = json.dumps(election, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(config_string.encode('utf-8')).hexdigest()
    
    def register_worker_node(self, worker_machine_id: str, election_id: str) -> bool:
        """Rekisteröi työasema vaalirekisteriin - PÄIVITETTY"""
        
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
            
            worker_node_info = {
                "machine_id": worker_machine_id,
                "registered_at": datetime.now(timezone.utc).isoformat(),
                "status": "active",
                "last_seen": datetime.now(timezone.utc).isoformat(),
                "capabilities": ["comparisons", "voting"]
            }
            
            # Päivitä tai lisää työasema
            existing_index = next((i for i, node in enumerate(worker_nodes) 
                                if node.get('machine_id') == worker_machine_id), -1)
            
            if existing_index >= 0:
                worker_nodes[existing_index] = worker_node_info
                print(f"ℹ️  Työasema päivitetty: {worker_machine_id}")
            else:
                worker_nodes.append(worker_node_info)
                print(f"✅ Työasema rekisteröity: {worker_machine_id}")
            
            registry["election_registry"]["worker_nodes"] = worker_nodes
            registry["election_registry"]["last_updated"] = datetime.now(timezone.utc).isoformat()
            registry["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()
            
            with open(registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)
            
            # Kirjaa system_chainiin
            try:
                from system_chain_manager import log_action
                log_action(
                    "worker_node_registered",
                    f"Työasema rekisteröity: {worker_machine_id}",
                    user_id=worker_machine_id,
                    metadata={
                        "election_id": election_id,
                        "worker_machine_id": worker_machine_id,
                        "master_machine_id": registry["election_registry"]["master_machine_id"],
                        "namespace": registry["election_registry"]["namespace"],
                        "total_workers": len(worker_nodes)
                    }
                )
            except ImportError:
                print("⚠️  System chain ei saatavilla - skipataan kirjaus")
            
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
            data['metadata']['last_updated'] = datetime.now(timezone.utc).isoformat()
            
            with open(system_metadata_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print("✅ System metadata päivitetty")
            return True
            
        except Exception as e:
            print(f"❌ Virhe päivittäessä metadataa: {e}")
            return False
    
    def get_namespace_info(self) -> Dict[str, str]:
        """Hae nimiavaruuden tiedot"""
        machine_info = self.get_machine_info()
        
        return {
            "election_id": machine_info["election_id"],
            "namespace": machine_info["namespace"],
            "machine_id": machine_info["machine_id"],
            "node_role": machine_info["node_role"],
            "is_master": machine_info["is_master"]
        }
    
    def verify_namespace_integrity(self) -> bool:
        """Tarkista nimiavaruuden eheys"""
        try:
            # Tarkista system_metadata
            with open(self.runtime_dir / "system_metadata.json", 'r', encoding='utf-8') as f:
                system_meta = json.load(f)
            
            system_namespace = system_meta.get('election_specific', {}).get('namespace')
            
            # Tarkista election_registry (jos on master)
            registry_file = self.runtime_dir / "election_registry.json"
            if registry_file.exists():
                with open(registry_file, 'r', encoding='utf-8') as f:
                    registry = json.load(f)
                registry_namespace = registry.get('election_registry', {}).get('namespace')
                
                if system_namespace != registry_namespace:
                    print(f"❌ Nimiavaruussopimattomuus: system={system_namespace}, registry={registry_namespace}")
                    return False
            
            # Tarkista meta.json
            with open(self.runtime_dir / "meta.json", 'r', encoding='utf-8') as f:
                meta = json.load(f)
            election_id = meta.get('election', {}).get('id')
            
            expected_namespace_prefix = f"election_{election_id}"
            if not system_namespace.startswith(expected_namespace_prefix):
                print(f"❌ Nimiavaruus ei vastaa vaalia: {system_namespace} vs {expected_namespace_prefix}")
                return False
            
            print(f"✅ Nimiavaruuden eheys varmistettu: {system_namespace}")
            return True
            
        except Exception as e:
            print(f"⚠️  Nimiavaruuden eheyden tarkistus epäonnistui: {e}")
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
    
    print("💻 KONEEN TIEDOT - PÄIVITETTY:")
    print(f"   Machine ID: {info['machine_id']}")
    print(f"   Vaali ID: {info['election_id']}")
    print(f"   Nimiavaruus: {info['namespace']}")
    print(f"   Rooli: {info['node_role']}")
    print(f"   Master: {info['is_master']}")
    
    # Tarkista nimiavaruus
    namespace_info = manager.get_namespace_info()
    print(f"🔗 Nimiavaruustiedot: {namespace_info}")
