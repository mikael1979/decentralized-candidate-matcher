# src/core/sync/managers/sync_manager.py
"""
Synkronoinnin päälogiikka - hallitsee synkronointiprosessia.
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
import click

from core.file_utils import read_json_file, write_json_file


class SyncManager:
    """Synkronoinnin päälogiikka."""
    
    def __init__(self, election_id: str = "Jumaltenvaalit2026"):
        self.election_id = election_id
        self.sync_file = Path(f"data/runtime/{election_id}_sync_list.json")
        self.cid_file = Path(f"data/runtime/{election_id}_sync_list.cid")
    
    def load_sync_list(self, ipfs_manager=None) -> Dict[str, Any]:
        """Lataa synkronointilista."""
        if self.sync_file.exists():
            click.echo("   📁 Ladataan paikallinen synkronointilista")
            data = read_json_file(str(self.sync_file), self.create_default_sync_list())
            latest_cid = data.get('latest_archive_cid', 'Ei arkistoa')
            click.echo(f"   ✅ Synkronointilista ladattu: {latest_cid}")
            return data
        else:
            click.echo("   📝 Luodaan uusi synkronointilista")
            return self.create_default_sync_list()
    
    def save_sync_list(self, sync_list: Dict[str, Any], ipfs_manager=None) -> Optional[str]:
        """Tallenna synkronointilista."""
        # Tallenna paikallisesti
        write_json_file(str(self.sync_file), sync_list)
        click.echo(f"   💾 Tallennettu paikallisesti: {self.sync_file}")
        
        # Lisää IPFS:ään jos manager on annettu
        if ipfs_manager:
            cid = ipfs_manager.add_data(sync_list, f"{self.election_id}_sync_list.json")
            
            # Tallenna CID
            with open(self.cid_file, 'w') as f:
                f.write(cid)
            click.echo(f"   🔗 Tallennettu CID: {self.cid_file}")
            
            return cid
        
        return None
    
    def create_default_sync_list(self) -> Dict[str, Any]:
        """Luo oletussynkronointilista."""
        return {
            "election_id": self.election_id,
            "latest_archive_cid": None,
            "previous_archives": [],
            "sync_schedule": {
                "next_sync": (datetime.now() + timedelta(hours=1)).isoformat(),
                "interval_hours": 1
            },
            "metadata": {
                "created": datetime.now().isoformat(),
                "archive_size_bytes": 0,
                "file_count": 0,
                "ipfs_mode": "MOCK"
            }
        }
    
    def update_sync_list(self, new_archive_cid: str, metadata: Dict[str, Any], 
                         ipfs_manager=None) -> Dict[str, Any]:
        """Päivitä synkronointilista uudella arkistolla."""
        sync_list = self.load_sync_list(ipfs_manager)
        
        # Siirrä vanha arkisto historiaan
        old_cid = sync_list.get("latest_archive_cid")
        if old_cid:
            sync_list.setdefault("previous_archives", []).insert(0, old_cid)
            # Säilytä vain 5 viimeisintä
            sync_list["previous_archives"] = sync_list["previous_archives"][:5]
        
        # Aseta uusi arkisto
        sync_list["latest_archive_cid"] = new_archive_cid
        
        # Päivitä metadata
        sync_list.setdefault("metadata", {})
        sync_list["metadata"].update({
            "timestamp": datetime.now().isoformat(),
            **metadata
        })
        
        return sync_list
    
    def get_sync_status(self, ipfs_manager=None) -> Dict[str, Any]:
        """Hae synkronointitila."""
        sync_list = self.load_sync_list(ipfs_manager)
        
        return {
            "election_id": self.election_id,
            "latest_archive_cid": sync_list.get("latest_archive_cid"),
            "previous_archives_count": len(sync_list.get("previous_archives", [])),
            "metadata": sync_list.get("metadata", {}),
            "sync_schedule": sync_list.get("sync_schedule", {})
        }
