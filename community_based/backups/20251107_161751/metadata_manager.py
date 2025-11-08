#!/usr/bin/env python3
"""
Metadata Manager - PÄIVITETTY UUDELLE ARKKITEHTUURILLE
Hallinnoi järjestelmän metatietoja uusilla domain/application/infrastructure -komponenteilla
"""

import json
import uuid
import hashlib
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Dict, Any, Optional, List

# UUSI ARKKITEHTUURI: Käytä uusia moduuleja
from core.dependency_container import get_container
from infrastructure.config.config_manager import ConfigManager
from infrastructure.logging.system_logger import SystemLogger
from domain.entities.election import Election
from domain.value_objects import ElectionId, ElectionName, ElectionType

class ModernMetadataManager:
    """Moderni metadata hallinta uuden arkkitehtuurin päällä"""
    
    def __init__(self, runtime_dir: str = "runtime"):
        self.runtime_dir = Path(runtime_dir)
        self.runtime_dir.mkdir(exist_ok=True)
        
        # UUSI ARKKITEHTUURI: Hae riippuvuudet containerista
        self.container = get_container(runtime_dir)
        self.config_manager = self.container.get_config_manager()
        self.system_logger = self.container.get_system_logger()
        
        # Lataa koneen ID
        self.machine_id = self._get_or_create_machine_id()
        
        print("✅ Modern Metadata Manager alustettu uudella arkkitehtuurilla")
    
    def _get_or_create_machine_id(self) -> str:
        """Hae tai luo koneen yksilöllinen ID - UUSI ARKKITEHTUURI"""
        try:
            # UUSI ARKKITEHTUURI: Käytä config manageria
            machine_info = self.config_manager.get_machine_info()
            return machine_info.get('machine_id', self._generate_machine_id())
        except Exception as e:
            print(f"⚠️  Konetietojen haku epäonnistui: {e}")
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
                'version': '2.0.0',
                'architecture': 'modern'
            }, f, indent=2, ensure_ascii=False)
        
        # UUSI ARKKITEHTUURI: Päivitä config manager
        self.config_manager.update_machine_info({'machine_id': machine_id})
        
        return machine_id
    
    def initialize_system_metadata(self, election_id: str, first_install: bool = False) -> Dict[str, Any]:
        """Alusta järjestelmän metadata - UUSI ARKKITEHTUURI"""
        
        try:
            # UUSI ARKKITEHTUURI: Käytä config manageria
            system_metadata = self.config_manager.initialize_system_metadata(
                election_id=election_id,
                first_install=first_install,
                machine_id=self.machine_id
            )
            
            # Luo vaalikohtainen nimiavaruus
            namespace = system_metadata["election_specific"]["namespace"]
            
            print(f"✅ System metadata alustettu - Nimiavaruus: {namespace}")
            
            # UUSI ARKKITEHTUURI: Kirjaa system logiin
            self.system_logger.log_metadata_event(
                event_type="system_metadata_initialized",
                metadata={
                    "election_id": election_id,
                    "namespace": namespace,
                    "first_install": first_install,
                    "machine_id": self.machine_id
                }
            )
            
            return system_metadata
            
        except Exception as e:
            print(f"❌ System metadatan alustus epäonnistui: {e}")
            raise
    
    def get_machine_info(self) -> Dict[str, Any]:
        """Hae koneen tiedot - UUSI ARKKITEHTUURI"""
        try:
            # UUSI ARKKITEHTUURI: Käytä config manageria
            machine_info = self.config_manager.get_machine_info()
            system_metadata = self.config_manager.get_system_metadata()
            
            election_specific = system_metadata.get('election_specific', {})
            election_id = election_specific.get('election_id', 'unknown')
            namespace = election_specific.get('namespace', 'unknown')
            first_install = election_specific.get('first_install', False)
            node_type = election_specific.get('node_type', 'unknown')
            
            return {
                'machine_id': machine_info.get('machine_id', self.machine_id),
                'election_id': election_id,
                'namespace': namespace,
                'first_install': first_install,
                'is_master': first_install,
                'node_role': 'master' if first_install else 'worker',
                'node_type': node_type,
                'architecture': 'modern'
            }
            
        except Exception as e:
            print(f"⚠️  Konetietojen haku epäonnistui: {e}")
            # Fallback
            return {
                'machine_id': self.machine_id,
                'election_id': 'unknown',
                'namespace': 'unknown',
                'first_install': False,
                'is_master': False,
                'node_role': 'unknown',
                'node_type': 'unknown',
                'architecture': 'modern'
            }
    
    def create_election_registry(self, election_data: Dict[str, Any]) -> Dict[str, Any]:
        """Luo vaalirekisterin ensimmäiselle asennukselle - UUSI ARKKITEHTUURI"""
        
        try:
            election_id = election_data["election_id"]
            election_name = election_data["name"]["fi"]
            
            # Luo nimiavaruus
            namespace = f"election_{election_id}_{datetime.now().strftime('%Y%m%d')}"
            
            # UUSI ARKKITEHTUURI: Käytä domain entityä
            election = Election(
                election_id=ElectionId(election_id),
                name=ElectionName(election_name, election_data["name"]),
                election_type=ElectionType(election_data.get("type", "test")),
                dates=election_data.get("dates", []),
                description=election_data.get("description", {}),
                config_hash=self._calculate_config_hash(election_data)
            )
            
            # Luo rekisteri
            registry = {
                "election_registry": {
                    "election_id": election_id,
                    "election_name": election_name,
                    "master_machine_id": self.machine_id,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "namespace": namespace,
                    "worker_nodes": [],
                    "config_hash": election.config_hash,
                    "ipfs_cid_mapping": {},
                    "status": "active",
                    "domain_entity": election.to_dict()  # UUSI: Sisällytä domain entity
                },
                "metadata": {
                    "version": "2.0.0",
                    "registry_type": "election_master",
                    "namespace_strategy": "election_id_timestamp",
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "architecture": "modern"
                }
            }
            
            # Tallenna rekisteri
            registry_file = self.runtime_dir / "election_registry.json"
            with open(registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)
            
            # UUSI ARKKITEHTUURI: Päivitä config manager
            self.config_manager.update_election_registry(registry)
            
            # UUSI ARKKITEHTUURI: Kirjaa system logiin
            self.system_logger.log_metadata_event(
                event_type="election_registry_created",
                metadata={
                    "election_id": election_id,
                    "election_name": election_name,
                    "namespace": namespace,
                    "master_machine_id": self.machine_id
                }
            )
            
            print(f"✅ Vaalirekisteri luotu - Nimiavaruus: {namespace}")
            return registry
            
        except Exception as e:
            print(f"❌ Vaalirekisterin luonti epäonnistui: {e}")
            raise
    
    def _calculate_config_hash(self, election_data: Dict[str, Any]) -> str:
        """Laske vaalikonfiguraation hash"""
        config_string = json.dumps(election_data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(config_string.encode('utf-8')).hexdigest()
    
    def register_worker_node(self, worker_machine_id: str, election_id: str) -> bool:
        """Rekisteröi työasema vaalirekisteriin - UUSI ARKKITEHTUURI"""
        
        try:
            # UUSI ARKKITEHTUURI: Käytä config manageria
            registry = self.config_manager.get_election_registry()
            
            if not registry:
                print("❌ Vaalirekisteriä ei löydy - oletko master-kone?")
                return False
            
            # Tarkista että oikea vaali
            if registry["election_registry"]["election_id"] != election_id:
                print(f"❌ Väärä vaali rekisterissä: {registry['election_registry']['election_id']}")
                return False
            
            # UUSI ARKKITEHTUURI: Käytä domain entityä
            election_data = registry["election_registry"].get("domain_entity", {})
            election = Election.from_dict(election_data) if election_data else None
            
            # Lisää työasema
            worker_nodes = registry["election_registry"].get("worker_nodes", [])
            
            worker_node_info = {
                "machine_id": worker_machine_id,
                "registered_at": datetime.now(timezone.utc).isoformat(),
                "status": "active",
                "last_seen": datetime.now(timezone.utc).isoformat(),
                "capabilities": ["comparisons", "voting", "modern_architecture"]
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
            
            # Tallenna rekisteri
            with open(self.runtime_dir / "election_registry.json", 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)
            
            # UUSI ARKKITEHTUURI: Päivitä config manager
            self.config_manager.update_election_registry(registry)
            
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
                        "total_workers": len(worker_nodes),
                        "architecture": "modern"
                    }
                )
            except ImportError:
                print("⚠️  System chain ei saatavilla - skipataan kirjaus")
            
            # UUSI ARKKITEHTUURI: Kirjaa system logiin
            self.system_logger.log_metadata_event(
                event_type="worker_node_registered",
                metadata={
                    "election_id": election_id,
                    "worker_machine_id": worker_machine_id,
                    "total_workers": len(worker_nodes)
                }
            )
            
            return True
                
        except Exception as e:
            print(f"❌ Virhe rekisteröitäessä työasemaa: {e}")
            return False
    
    def get_election_registry(self) -> Optional[Dict[str, Any]]:
        """Hae vaalirekisteri - UUSI ARKKITEHTUURI"""
        try:
            # UUSI ARKKITEHTUURI: Käytä config manageria
            return self.config_manager.get_election_registry()
        except Exception as e:
            print(f"⚠️  Vaalirekisterin haku epäonnistui: {e}")
            return None
    
    def update_system_metadata(self, updates: Dict[str, Any]) -> bool:
        """Päivitä järjestelmän metadataa - UUSI ARKKITEHTUURI"""
        try:
            # UUSI ARKKITEHTUURI: Käytä config manageria
            success = self.config_manager.update_system_metadata(updates)
            
            if success:
                print("✅ System metadata päivitetty")
                
                # UUSI ARKKITEHTUURI: Kirjaa system logiin
                self.system_logger.log_metadata_event(
                    event_type="system_metadata_updated",
                    metadata={"updates": updates}
                )
            
            return success
            
        except Exception as e:
            print(f"❌ Virhe päivittäessä metadataa: {e}")
            return False
    
    def get_namespace_info(self) -> Dict[str, str]:
        """Hae nimiavaruuden tiedot - UUSI ARKKITEHTUURI"""
        try:
            # UUSI ARKKITEHTUURI: Käytä config manageria
            namespace_info = self.config_manager.get_namespace_info()
            machine_info = self.get_machine_info()
            
            return {
                **namespace_info,
                "machine_id": machine_info["machine_id"],
                "node_role": machine_info["node_role"],
                "is_master": machine_info["is_master"],
                "architecture": "modern"
            }
            
        except Exception as e:
            print(f"⚠️  Nimiavaruustietojen haku epäonnistui: {e}")
            return {
                "election_id": "unknown",
                "namespace": "unknown",
                "machine_id": self.machine_id,
                "node_role": "unknown",
                "is_master": False,
                "architecture": "modern"
            }
    
    def verify_namespace_integrity(self) -> bool:
        """Tarkista nimiavaruuden eheys - UUSI ARKKITEHTUURI"""
        try:
            # UUSI ARKKITEHTUURI: Käytä config manageria
            integrity_check = self.config_manager.verify_namespace_integrity()
            
            if integrity_check["success"]:
                print(f"✅ Nimiavaruuden eheys varmistettu: {integrity_check['namespace']}")
                
                # UUSI ARKKITEHTUURI: Kirjaa system logiin
                self.system_logger.log_metadata_event(
                    event_type="namespace_integrity_verified",
                    metadata=integrity_check
                )
            else:
                print(f"❌ Nimiavaruuden eheysongelmia: {integrity_check.get('issues', [])}")
            
            return integrity_check["success"]
            
        except Exception as e:
            print(f"⚠️  Nimiavaruuden eheyden tarkistus epäonnistui: {e}")
            return False
    
    def get_election_info(self, election_id: str = None) -> Optional[Dict[str, Any]]:
        """Hae vaalin tiedot - UUSI ARKKITEHTUURI"""
        try:
            # UUSI ARKKITEHTUURI: Käytä config manageria
            if election_id:
                return self.config_manager.get_election_by_id(election_id)
            else:
                return self.config_manager.get_current_election_info()
                
        except Exception as e:
            print(f"⚠️  Vaalitietojen haku epäonnistui: {e}")
            return None
    
    def list_all_elections(self) -> List[Dict[str, Any]]:
        """Listaa kaikki vaalit - UUSI ARKKITEHTUURI"""
        try:
            # UUSI ARKKITEHTUURI: Käytä config manageria
            return self.config_manager.get_all_elections()
        except Exception as e:
            print(f"⚠️  Vaalilistaus epäonnistui: {e}")
            return []
    
    def get_system_health(self) -> Dict[str, Any]:
        """Hae järjestelmän terveystila - UUSI ARKKITEHTUURI"""
        try:
            health_info = {
                "metadata_manager": {
                    "status": "healthy",
                    "machine_id": self.machine_id,
                    "architecture": "modern",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                "config_manager": self.config_manager.get_health_status(),
                "namespace_integrity": self.verify_namespace_integrity(),
                "election_registry": bool(self.get_election_registry())
            }
            
            # Laske kokonaisterveys
            all_healthy = (
                health_info["metadata_manager"]["status"] == "healthy" and
                health_info["config_manager"]["status"] == "healthy" and
                health_info["namespace_integrity"] and
                health_info["election_registry"]
            )
            
            health_info["overall_health"] = "healthy" if all_healthy else "degraded"
            
            return health_info
            
        except Exception as e:
            return {
                "overall_health": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }


# Singleton instance (yhteensopavuuden vuoksi)
_metadata_manager_instance = None

def get_metadata_manager(runtime_dir: str = "runtime") -> ModernMetadataManager:
    """Hae MetadataManager-instanssi - UUSI ARKKITEHTUURI"""
    global _metadata_manager_instance
    if _metadata_manager_instance is None:
        _metadata_manager_instance = ModernMetadataManager(runtime_dir)
    return _metadata_manager_instance

# Legacy API yhteensopavuuden vuoksi
def get_legacy_metadata_manager(runtime_dir: str = "runtime"):
    """Legacy API yhteensopavuuden vuoksi"""
    return get_metadata_manager(runtime_dir)

# Testaus
if __name__ == "__main__":
    # Alusta container ensin
    from core.dependency_container import initialize_container
    initialize_container()
    
    manager = get_metadata_manager()
    info = manager.get_machine_info()
    
    print("💻 MODERN METADATA MANAGER TESTI - UUSI ARKKITEHTUURI")
    print("=" * 50)
    print(f"   Machine ID: {info['machine_id']}")
    print(f"   Vaali ID: {info['election_id']}")
    print(f"   Nimiavaruus: {info['namespace']}")
    print(f"   Rooli: {info['node_role']}")
    print(f"   Master: {info['is_master']}")
    print(f"   Arkkitehtuuri: {info['architecture']}")
    
    # Tarkista nimiavaruus
    namespace_info = manager.get_namespace_info()
    print(f"🔗 Nimiavaruustiedot: {namespace_info}")
    
    # Tarkista terveystila
    health = manager.get_system_health()
    print(f"🏥 Terveystila: {health['overall_health']}")
    
    # Testaa nimiavaruuden eheys
    integrity = manager.verify_namespace_integrity()
    print(f"🔒 Nimiavaruuden eheys: {'✅ OK' if integrity else '❌ ONGELMIA'}")
    
    print("\n🎯 MODERN METADATA MANAGER VALMIS UUDELLE ARKKITEHTUURILLE!")
