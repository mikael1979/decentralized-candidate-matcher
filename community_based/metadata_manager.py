[file name]: metadata_manager.py
[file content begin]
"""
Metadata hallintamoduuli vaalijärjestelmälle
Käsittelee järjestelmän metadataa, kone-ID:t ja allekirjoitukset
"""

import json
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

class MetadataManager:
    """Hallinnoi järjestelmän metadataa ja konekohtaisia tunnisteita"""
    
    def __init__(self, runtime_dir: str = "runtime"):
        self.runtime_dir = Path(runtime_dir)
        self.metadata_file = self.runtime_dir / "system_metadata.json"
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Varmistaa että tarvittavat hakemistot ovat olemassa"""
        self.runtime_dir.mkdir(exist_ok=True)
    
    def generate_machine_id(self) -> str:
        """
        Generoi yksilöllisen kone-ID:n
        Perustuu UUID:hen ja koneen tietoihin (simuloitu)
        """
        # Käytännössä voitaisiin käyttää koneen MAC-osoitetta tms.
        # Tässä mock-versio
        base_uuid = str(uuid.uuid4())
        machine_specific = f"machine_{base_uuid[:8]}_{datetime.now().timestamp()}"
        
        # Hashaa lopputuloksen
        machine_id = hashlib.sha256(machine_specific.encode()).hexdigest()[:16]
        return f"machine_{machine_id}"
    
    def get_election_signature(self, election_id: str, machine_id: str) -> str:
        """
        Generoi allekirjoituksen vaalikohtaiselle koneelle
        """
        signature_data = f"{election_id}:{machine_id}:{datetime.now().isoformat()}"
        return hashlib.sha256(signature_data.encode()).hexdigest()
    
    def initialize_system_metadata(self, election_id: str, first_install: bool = False) -> Dict[str, Any]:
        """
        Alustaa järjestelmän metadatan
        """
        machine_id = self.generate_machine_id()
        
        metadata = {
            "system_metadata": {
                "machine_id": machine_id,
                "created": datetime.now().isoformat(),
                "first_install": first_install,
                "installation_type": "first" if first_install else "additional"
            },
            "election_specific": {
                "election_id": election_id,
                "election_signature": self.get_election_signature(election_id, machine_id),
                "installed_machines": [machine_id] if first_install else [],
                "master_machine": machine_id if first_install else None
            },
            "sync_metadata": {
                "last_sync": None,
                "sync_count": 0,
                "conflict_count": 0
            }
        }
        
        # Tallenna metadata
        self._save_metadata(metadata)
        
        return metadata
    
    def load_metadata(self) -> Dict[str, Any]:
        """Lataa järjestelmän metadata"""
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _save_metadata(self, metadata: Dict[str, Any]):
        """Tallentaa järjestelmän metadatan"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def update_metadata(self, updates: Dict[str, Any]):
        """Päivittää metadataa osittain"""
        current_metadata = self.load_metadata()
        
        # Syvä merge
        def deep_update(current, update):
            for key, value in update.items():
                if isinstance(value, dict) and key in current and isinstance(current[key], dict):
                    deep_update(current[key], value)
                else:
                    current[key] = value
        
        deep_update(current_metadata, updates)
        self._save_metadata(current_metadata)
    
    def register_new_machine(self, election_id: str, master_signature: str) -> bool:
        """
        Rekisteröi uusi kone olemassa olevaan vaaliin
        """
        metadata = self.load_metadata()
        
        if not metadata:
            return False
        
        # Tarkista että master_signature on validi
        current_master = metadata["election_specific"].get("master_machine")
        if not current_master:
            return False
        
        # Generoi uusi kone-ID
        new_machine_id = self.generate_machine_id()
        
        # Päivitä metadata
        metadata["election_specific"]["installed_machines"].append(new_machine_id)
        metadata["system_metadata"]["machine_id"] = new_machine_id
        metadata["system_metadata"]["first_install"] = False
        metadata["system_metadata"]["installation_type"] = "additional"
        metadata["election_specific"]["election_signature"] = self.get_election_signature(
            election_id, new_machine_id
        )
        
        self._save_metadata(metadata)
        return True
    
    def is_first_installation(self, election_id: str) -> bool:
        """
        Tarkistaa onko kyseessä ensimmäinen asennus tälle vaalille
        """
        metadata = self.load_metadata()
        
        if not metadata:
            return True
        
        # Tarkista että metadata on samalle vaalille
        current_election = metadata["election_specific"].get("election_id")
        if current_election != election_id:
            return True
        
        return metadata["system_metadata"].get("first_install", False)
    
    def get_machine_info(self) -> Dict[str, Any]:
        """Palauttaa koneen tiedot"""
        metadata = self.load_metadata()
        
        if not metadata:
            return {
                "machine_id": "unknown",
                "first_install": True,
                "election_id": "unknown"
            }
        
        return {
            "machine_id": metadata["system_metadata"]["machine_id"],
            "first_install": metadata["system_metadata"]["first_install"],
            "election_id": metadata["election_specific"]["election_id"],
            "is_master": metadata["election_specific"].get("master_machine") == metadata["system_metadata"]["machine_id"]
        }
    
    def create_election_registry(self, election_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Luo vaalirekisterin ensimmäiselle asennukselle
        """
        machine_info = self.get_machine_info()
        
        registry = {
            "election_registry": {
                "election_id": election_data["election_id"],
                "name": election_data["name"],
                "master_machine": machine_info["machine_id"],
                "created": datetime.now().isoformat(),
                "total_machines": 1,
                "machines": [machine_info["machine_id"]],
                "config_hash": self._calculate_config_hash(election_data)
            },
            "installation_metadata": {
                "first_installation": machine_info["first_install"],
                "installation_timestamp": datetime.now().isoformat(),
                "system_version": "1.0.0"
            }
        }
        
        return registry
    
    def _calculate_config_hash(self, election_data: Dict[str, Any]) -> str:
        """Laskee konfiguraation hashin"""
        config_string = json.dumps(election_data, sort_keys=True)
        return hashlib.sha256(config_string.encode()).hexdigest()

# Singleton instance
_metadata_manager = None

def get_metadata_manager(runtime_dir: str = "runtime") -> MetadataManager:
    """Palauttaa MetadataManager-instanssin"""
    global _metadata_manager
    if _metadata_manager is None:
        _metadata_manager = MetadataManager(runtime_dir)
    return _metadata_manager
[file content end]
