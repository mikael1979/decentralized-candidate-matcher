[file name]: installation_engine.py
[file content begin]
"""
Asennusmoottori vaalijärjestelmälle
Käsittelee asennuslogiikan modulaarisesti
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
    
    def load_elections_config(self, config_cid: str) -> Dict[str, Any]:
        """Lataa vaalikonfiguraation IPFS:stä"""
        if not self.ipfs_client:
            raise ValueError("IPFS-asiakas puuttuu")
        
        elections_data = self.ipfs_client.download(config_cid)
        
        if not elections_data:
            raise ValueError(f"Vaalikonfiguraatiota ei löydy CID:llä: {config_cid}")
        
        return elections_data
    
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
        
        print(f"🚀 ASENNETAAN VAILLI: {election['name']['fi']}")
        
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
        
        # Luo asennusmetatiedot
        self._create_installation_meta(election, first_install)
        
        print(f"   ✅ Konfiguraatiotiedostot luotu")
    
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
            }
            # Muut runtime-tiedostot...
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
            ]
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
            "system_metadata.json",
            "installation_meta.json"
        ]
        
        for file_path in required_files:
            if not (self.runtime_dir / file_path).exists():
                return False
        
        # Tarkista että metadata on oikealle vaalille
        machine_info = self.metadata_manager.get_machine_info()
        return machine_info["election_id"] == election_id
[file content end]
