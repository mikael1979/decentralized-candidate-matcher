#!/usr/bin/env python3
"""
Asennusmoottori vaalijärjestelmälle - KORJATTU VERSIO
Käsittelee asennuslogiikan modulaarisesti sekä IPFS:n että paikalliset tiedostot
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from metadata_manager import get_metadata_manager

class InstallationEngine:
    """Käsittelee vaalijärjestelmän asennuslogiikan"""
    
    def __init__(self, runtime_dir: str = "runtime"):
        self.runtime_dir = Path(runtime_dir)
        self.metadata_manager = get_metadata_manager(runtime_dir)
        self.ipfs_client = None  # Asetetaan ulkopuolelta
    
    def set_ipfs_client(self, ipfs_client):
        """Asettaa IPFS-asiakkaan"""
        self.ipfs_client = ipfs_client
    
    def load_elections_config(self, config_source: str) -> Dict[str, Any]:
        """Lataa vaalikonfiguraation joko IPFS:stä tai paikallisesta tiedostosta"""
        
        # Tarkista onko lähde paikallinen tiedosto
        if config_source.endswith('.json') and Path(config_source).exists():
            print(f"📁 Ladataan paikallisesta tiedostosta: {config_source}")
            return self._load_from_local_file(config_source)
        
        # Tarkista onko lähde IPFS CID
        elif config_source.startswith('Qm') and self.ipfs_client:
            print(f"🌐 Ladataan IPFS:stä CID:llä: {config_source}")
            return self._load_from_ipfs(config_source)
        
        else:
            raise ValueError(f"Tuntematon konfiguraatiolähde: {config_source}")
    
    def _load_from_local_file(self, file_path: str) -> Dict[str, Any]:
        """Lataa konfiguraatio paikallisesta tiedostosta"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Tarkista tiedoston rakenne
            if 'elections' in data:
                # elections_list.json rakenne
                return data
            elif 'election_data' in data:
                # install_config.base.json rakenne - muunna elections_list muotoon
                return self._convert_install_config_to_elections_list(data)
            else:
                raise ValueError("Tuntematon konfiguraatiotiedoston rakenne")
                
        except Exception as e:
            raise ValueError(f"Virhe ladattaessa tiedostoa {file_path}: {e}")
    
    def _load_from_ipfs(self, cid: str) -> Dict[str, Any]:
        """Lataa konfiguraatio IPFS:stä"""
        if not self.ipfs_client:
            raise ValueError("IPFS-asiakas puuttuu")
        
        elections_data = self.ipfs_client.download(cid)
        
        if not elections_data:
            raise ValueError(f"Vaalikonfiguraatiota ei löydy CID:llä: {cid}")
        
        return elections_data
    
    def _convert_install_config_to_elections_list(self, install_config: Dict[str, Any]) -> Dict[str, Any]:
        """Muuntaa install_config.base.json muotoon elections_list.json"""
        election_data = install_config['election_data']
        
        return {
            "metadata": {
                "version": "1.0.0",
                "created": datetime.now().isoformat(),
                "source": "converted_from_install_config"
            },
            "elections": [
                {
                    "election_id": election_data["id"],
                    "name": election_data["name"],
                    "description": election_data["name"],  # Käytä nimea kuvauksena
                    "dates": [
                        {
                            "phase": 1,
                            "date": election_data["date"],
                            "description": {
                                "fi": "Vaalipäivä",
                                "en": "Election day",
                                "sv": "Valdag"
                            }
                        }
                    ],
                    "type": election_data["type"],
                    "timelock_enabled": election_data["timelock_enabled"],
                    "edit_deadline": election_data["edit_deadline"],
                    "grace_period_hours": election_data["grace_period_hours"],
                    "community_managed": election_data["community_managed"],
                    "phases": 1,
                    "districts": election_data.get("districts", ["koko_maa"]),
                    "status": "upcoming",
                    "config_cid": election_data.get("ipfs_cid", "")
                }
            ]
        }
    
    def list_available_elections(self, elections_data: Dict[str, Any]) -> None:
        """Listaa saatavilla olevat vaalit"""
        print("\n📋 SAATAVILLA OLEVAT VAALIT:")
        print("=" * 70)
        
        for i, election in enumerate(elections_data['elections'], 1):
            status = election.get('status', 'unknown')
            dates = ", ".join([phase['date'] for phase in election['dates']])
            election_id = election['election_id']
            
            # Tarkista asennustila
            machine_info = self.metadata_manager.get_machine_info()
            is_installed = (machine_info['election_id'] == election_id)
            install_status = "✅ ASENNETTU" if is_installed else "🔲 EI ASENNETTU"
            
            print(f"{i}. {election['name']['fi']} {install_status}")
            print(f"   🆔 ID: {election_id}")
            print(f"   📅 Päivät: {dates}")
            print(f"   🏛️  Tyyppi: {election['type']}")
            print(f"   📊 Tila: {status}")
            print(f"   🔗 Konfiguraatio CID: {election.get('config_cid', 'Ei määritelty')}")
            print()
    
    def install_election(self, election_id: str, elections_data: Dict[str, Any], 
                        first_install: bool = False) -> Dict[str, Any]:
        """Asentaa tietyn vaalin"""
        
        # Etsi vaali
        election = self._find_election(election_id, elections_data)
        if not election:
            raise ValueError(f"Vaalia '{election_id}' ei löydy")
        
        print(f"🚀 ASENNETAAN VAALI: {election['name']['fi']}")
        
        # 1. Alusta metadata
        metadata = self.metadata_manager.initialize_system_metadata(election_id, first_install)
        machine_info = self.metadata_manager.get_machine_info()
        
        print(f"   💻 Kone-ID: {machine_info['machine_id']}")
        print(f"   📝 Asennustyyppi: {'Ensimmäinen asennus' if first_install else 'Lisäasennus'}")
        
        # 2. Lataa vaalin spesifinen konfiguraatio jos saatavilla
        election_config = self._load_election_config(election)
        
        # 3. Luo konfiguraatiotiedostot
        self._create_configuration_files(election, election_config, first_install)
        
        # 4. Luo vaalirekisteri ensimmäiselle asennukselle
        if first_install:
            registry = self.metadata_manager.create_election_registry(election)
            self._save_election_registry(registry)
        
        # 5. Päivitä system_chain
        self._update_system_chain(election, machine_info)
        
        return {
            "election": election,
            "metadata": metadata,
            "machine_info": machine_info,
            "installation_time": datetime.now().isoformat()
        }
    
    def _find_election(self, election_id: str, elections_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Etsii vaalin ID:llä"""
        for election in elections_data['elections']:
            if election['election_id'] == election_id:
                return election
        return None
    
    def _load_election_config(self, election: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Lataa vaalin spesifinen konfiguraatio"""
        config_cid = election.get('config_cid')
        if config_cid and self.ipfs_client:
            print(f"   🔍 Ladataan vaalin spesifistä konfiguraatiota...")
            return self.ipfs_client.download(config_cid)
        return None
    
    def _create_configuration_files(self, election: Dict[str, Any], 
                                  election_config: Optional[Dict[str, Any]], 
                                  first_install: bool):
        """Luo konfiguraatiotiedostot"""
        
        # Luo base-templatet
        self._create_base_templates(election, election_config)
        
        # Luo runtime-tiedostot
        self._create_runtime_files(election)
        
        # Luo kriittiset metatiedostot
        self._create_meta_file(election)
        self._create_system_metadata_file(election)
        
        # Luo asennusmetatiedot
        self._create_installation_meta(election, first_install)
        
        print(f"   ✅ Konfiguraatiotiedostot luotu")
    
    def _create_meta_file(self, election: Dict[str, Any]):
        """Luo meta.json-tiedoston vaalin tiedoista."""
        meta_data = {
            "election": {
                "id": election["election_id"],
                "name": election["name"],
                "date": election["dates"][0]["date"],
                "type": election["type"],
                "timelock_enabled": election["timelock_enabled"],
                "edit_deadline": election["edit_deadline"],
                "grace_period_hours": election["grace_period_hours"],
                "governance_model": "community_driven"
            },
            "system_info": {
                "system_id": f"system_{election['election_id']}",
                "created": datetime.now().isoformat(),
                "machine_id": self.metadata_manager.get_machine_info()["machine_id"]
            },
            "version": "1.0.0"
        }
        with open(self.runtime_dir / "meta.json", "w", encoding="utf-8") as f:
            json.dump(meta_data, f, indent=2, ensure_ascii=False)
    
    def _create_system_metadata_file(self, election: Dict[str, Any]):
        """Luo system_metadata.json-tiedoston."""
        system_metadata = {
            "election_specific": {
                "election_id": election["election_id"],
                "election_name": election["name"]["fi"],
                "machine_id": self.metadata_manager.get_machine_info()["machine_id"],
                "installed_at": datetime.now().isoformat(),
                "first_install": self.metadata_manager.get_machine_info()["first_install"]
            },
            "node_info": {
                "node_id": self.metadata_manager.get_machine_info()["machine_id"],
                "role": "master" if self.metadata_manager.get_machine_info()["first_install"] else "worker",
                "capabilities": ["comparisons", "voting", "sync"]
            },
            "version": "1.0.0"
        }
        
        with open(self.runtime_dir / "system_metadata.json", "w", encoding="utf-8") as f:
            json.dump(system_metadata, f, indent=2, ensure_ascii=False)
    
    def _create_base_templates(self, election: Dict[str, Any], election_config: Optional[Dict[str, Any]]):
        """Luo base-template tiedostot"""
        base_dir = self.runtime_dir / "base_templates"
        base_dir.mkdir(exist_ok=True)
        
        # install_config.base.json
        install_config = {
            "election_data": {
                "id": election["election_id"],
                "ipfs_cid": election.get("config_cid", ""),
                "name": election["name"],
                "date": election["dates"][0]["date"],
                "type": election["type"],
                "timelock_enabled": election["timelock_enabled"],
                "edit_deadline": election["edit_deadline"],
                "grace_period_hours": election["grace_period_hours"],
                "community_managed": election["community_managed"],
                "phases": election.get("phases", 1),
                "districts": election.get("districts", [])
            },
            "system_metadata": {
                "machine_id": self.metadata_manager.get_machine_info()["machine_id"],
                "first_install": self.metadata_manager.get_machine_info()["first_install"],
                "installed_at": datetime.now().isoformat()
            }
        }
        
        with open(base_dir / "install_config.base.json", "w", encoding="utf-8") as f:
            json.dump(install_config, f, indent=2, ensure_ascii=False)
    
    def _create_runtime_files(self, election: Dict[str, Any]):
        """Luo runtime-tiedostot"""
        runtime_files = {
            "questions.json": {
                "metadata": {
                    "election_id": election["election_id"],
                    "machine_id": self.metadata_manager.get_machine_info()["machine_id"],
                    "created": datetime.now().isoformat()
                },
                "questions": []
            },
            "candidates.json": {
                "metadata": {
                    "election_id": election["election_id"],
                    "machine_id": self.metadata_manager.get_machine_info()["machine_id"],
                    "created": datetime.now().isoformat()
                },
                "candidates": []
            },
            "new_questions.json": {
                "metadata": {
                    "election_id": election["election_id"],
                    "created": datetime.now().isoformat()
                },
                "questions": []
            },
            "active_questions.json": {
                "metadata": {
                    "election_id": election["election_id"],
                    "created": datetime.now().isoformat()
                },
                "questions": []
            },
            "ipfs_questions.json": {
                "metadata": {
                    "election_id": election["election_id"],
                    "created": datetime.now().isoformat(),
                    "last_sync": None
                },
                "questions": []
            }
        }
        
        for filename, content in runtime_files.items():
            with open(self.runtime_dir / filename, "w", encoding="utf-8") as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
    
    def _create_installation_meta(self, election: Dict[str, Any], first_install: bool):
        """Luo asennusmetatiedot"""
        installation_meta = {
            "installation": {
                "election_id": election["election_id"],
                "election_name": election["name"]["fi"],
                "machine_id": self.metadata_manager.get_machine_info()["machine_id"],
                "first_install": first_install,
                "installed_at": datetime.now().isoformat(),
                "system_version": "1.0.0"
            }
        }
        
        with open(self.runtime_dir / "installation_meta.json", "w", encoding="utf-8") as f:
            json.dump(installation_meta, f, indent=2, ensure_ascii=False)
    
    def _save_election_registry(self, registry: Dict[str, Any]):
        """Tallentaa vaalirekisterin"""
        with open(self.runtime_dir / "election_registry.json", "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
    
    def _update_system_chain(self, election: Dict[str, Any], machine_info: Dict[str, Any]):
        """Päivittää system_chain.json"""
        system_chain = {
            "chain_id": election["election_id"],
            "machine_id": machine_info["machine_id"],
            "created_at": datetime.now().isoformat(),
            "description": f"Vaalijärjestelmä: {election['name']['fi']}",
            "installation_type": "first" if machine_info["first_install"] else "additional",
            "blocks": [
                {
                    "block_id": 0,
                    "timestamp": datetime.now().isoformat(),
                    "description": "Järjestelmän asennus",
                    "machine_id": machine_info["machine_id"],
                    "first_install": machine_info["first_install"]
                }
            ],
            "current_state": {
                "election_id": election["election_id"],
                "installation_time": datetime.now().isoformat(),
                "files_created": [
                    "install_config.base.json",
                    "questions.json", 
                    "candidates.json",
                    "system_chain.json",
                    "installation_meta.json",
                    "meta.json",
                    "system_metadata.json"
                ]
            }
        }
        
        with open(self.runtime_dir / "system_chain.json", "w", encoding="utf-8") as f:
            json.dump(system_chain, f, indent=2, ensure_ascii=False)
    
    def verify_installation(self, election_id: str) -> bool:
        """Tarkistaa asennuksen onnistumisen"""
        required_files = [
            "base_templates/install_config.base.json",
            "questions.json",
            "candidates.json", 
            "system_chain.json",
            "installation_meta.json",
            "new_questions.json",
            "active_questions.json",
            "ipfs_questions.json",
            "meta.json",
            "system_metadata.json"
        ]
        
        for file_path in required_files:
            if not (self.runtime_dir / file_path).exists():
                print(f"❌ Puuttuu: {file_path}")
                return False
        
        # Tarkista että metadata on oikealle vaalille
        machine_info = self.metadata_manager.get_machine_info()
        if machine_info["election_id"] != election_id:
            print(f"❌ Väärä vaali: {machine_info['election_id']} != {election_id}")
            return False
        
        print("✅ Asennus tarkistettu onnistuneesti")
        return True

    def verify_installation(self, election_id: str) -> bool:
        """Tarkista asennuksen onnistuminen"""
        required_files = [
            "base_templates/install_config.base.json",
            "questions.json",
            "candidates.json", 
            "system_chain.json",
            "installation_meta.json",
            "new_questions.json",
            "active_questions.json",
            "ipfs_questions.json",
            "meta.json",
            "system_metadata.json"
        ]
        
        for file_path in required_files:
            if not (self.runtime_dir / file_path).exists():
                print(f"❌ Puuttuu: {file_path}")
                return False
        
        # Tarkista että metadata on oikealle vaalille
        machine_info = self.metadata_manager.get_machine_info()
        if machine_info.get("election_id") != election_id:
            print(f"❌ Väärä vaali: {machine_info.get('election_id')} != {election_id}")
            return False
        
        print("✅ Kaikki tarvittavat tiedostot löytyvät")
        print(f"✅ Oikea vaali: {election_id}")
        print(f"✅ Node rooli: {machine_info.get('node_role')}")
        print(f"✅ Machine ID: {machine_info.get('machine_id')}")
        
        return True

    def _fetch_election_registry(self, master_node: str, election_id: str) -> Dict[str, Any]:
        """Hae vaalirekisteri master-nodelta (simuloi)"""
        # Tässä vaiheessa simuloidaan - todellisessa toteutuksessa
        # tämä yhdistäisi master-noden IPFS:ään tai verkkoon
        print(f"🔗 Haetaan vaalirekisteriä master-nodelta: {master_node}")
        
        # Simuloi rekisterin haku
        return {
            "election_registry": {
                "election_id": election_id,
                "election_name": f"Vaalit {election_id}",
                "master_machine_id": master_node,
                "namespace": f"election_{election_id}",
                "worker_nodes": [],
                "created_at": "2025-01-01T00:00:00Z",
                "status": "active"
            }
        }

    def _sync_from_master(self, master_node: str) -> Dict[str, Any]:
        """Synkronoi data master-nodelta (simuloi)"""
        print(f"🔄 Synkronoidaan dataa master-nodelta: {master_node}")
        
        # Simuloi synkronointi
        return {
            "success": True,
            "synced_items": 15,
            "message": "Data synkronoitu masterilta",
            "master_node": master_node
        }
