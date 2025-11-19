# src/core/ipfs/sync_orchestrator.py
"""
Synkronointi orkestraattori - hallitsee täydet arkistot ja delta-päivitykset
"""
import json
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

from .archive_manager import ArchiveManager
from .delta_manager import DeltaManager

class SyncOrchestrator:
    """
    Orkestroi koko synkronointiprosessin
    - Ensimmäinen synkronointi: Täysi arkisto
    - Seuraavat synkronointit: Delta-päivitykset
    """
    
    def __init__(self, election_id: str, client):
        self.election_id = election_id
        self.client = client
        
        # Alusta managerit
        self.archive_manager = ArchiveManager(client)
        self.delta_manager = DeltaManager(client)
        
        # Synkronointitila
        self.sync_state_file = Path(f"data/sync_state/{election_id}_orchestrator.json")
        self.sync_state_file.parent.mkdir(parents=True, exist_ok=True)
        self.sync_state = self._load_sync_state()
    
    def sync_data(self, data_files: Dict[str, Dict], force_full_sync: bool = False) -> str:
        """
        Päätä synkronointistrategia ja suorita synkronointi
        
        Args:
            data_files: Synkronoitava data
            force_full_sync: Pakota täysi synkronointi
            
        Returns:
            IPFS CID synkronoidulle datalle
        """
        print(f"🔄 Starting sync for {self.election_id}")
        print(f"   Files: {list(data_files.keys())}")
        
        if force_full_sync or not self.sync_state.get("last_base_cid"):
            # TÄYSI SYNKRONOINTI - ensimmäinen kerta tai pakotettu
            return self._perform_full_sync(data_files)
        else:
            # DELTA SYNKRONOINTI - normaali päivitys
            return self._perform_delta_sync(data_files)
    
    def _perform_full_sync(self, data_files: Dict[str, Dict]) -> str:
        """Suorita täysi synkronointi"""
        print("🎯 Strategy: FULL SYNC")
        
        # Luo täysi arkisto
        base_cid = self.archive_manager.create_full_archive(data_files)
        
        # Päivitä synkronointitila
        self.sync_state.update({
            "last_base_cid": base_cid,
            "base_hashes": self.archive_manager._calculate_file_hashes(data_files),
            "last_full_sync": datetime.now().isoformat(),
            "file_count": len(data_files),
            "sync_count": self.sync_state.get("sync_count", 0) + 1
        })
        
        self._save_sync_state()
        
        print(f"✅ Full sync completed: {base_cid}")
        return base_cid
    
    def _perform_delta_sync(self, data_files: Dict[str, Dict]) -> str:
        """Suorita delta-synkronointi"""
        print("🎯 Strategy: DELTA SYNC")
        
        base_cid = self.sync_state["last_base_cid"]
        base_hashes = self.sync_state["base_hashes"]
        
        # Laske säästöt
        savings = self.delta_manager.calculate_delta_size_saving(data_files, base_hashes)
        print(f"   💰 Size saving: {savings['saving_percent']:.1f}% "
              f"({savings['saving_bytes']} bytes)")
        
        # Luo delta-päivitys
        delta_cid = self.delta_manager.create_delta_update(data_files, base_cid, base_hashes)
        
        # Päivitä synkronointitila
        self.sync_state.update({
            "last_delta_cid": delta_cid,
            "last_sync": datetime.now().isoformat(),
            "delta_count": self.sync_state.get("delta_count", 0) + 1,
            "total_savings_bytes": self.sync_state.get("total_savings_bytes", 0) + savings["saving_bytes"],
            "last_savings": savings
        })
        
        self._save_sync_state()
        
        print(f"✅ Delta sync completed: {delta_cid}")
        return delta_cid
    
    def load_data(self, cid: str) -> Dict[str, Dict]:
        """
        Lataa data IPFS:stä, käsitellen sekä täydet arkistot että deltat
        
        Args:
            cid: IPFS CID (täysi arkisto tai delta)
            
        Returns:
            Purettu data
        """
        print(f"📥 Loading data: {cid}")
        
        data = self.client.get_json(cid)
        metadata = data.get("metadata", {})
        
        if metadata.get("type") == "full_archive":
            # Täysi arkisto - palauta suoraan
            return data.get("files", {})
        
        elif metadata.get("type") == "delta_update":
            # Delta - lataa ensin perusarkisto ja sovi delta
            base_cid = metadata.get("base_cid")
            if not base_cid:
                raise ValueError("Delta missing base_cid")
            
            print(f"   🔗 Loading base archive: {base_cid}")
            base_files = self.load_data(base_cid)  # Rekursiivisesti
            updated_files = self.delta_manager.apply_delta_update(base_files, cid)
            return updated_files
        
        else:
            # Vanha formaatti tai tuntematon - oleta suora data
            print("   ⚠️  Unknown format, assuming direct data")
            return data
    
    def get_sync_statistics(self) -> Dict[str, Any]:
        """Hae synkronointitilastot"""
        stats = self.sync_state.copy()
        stats["election_id"] = self.election_id
        
        # Laska säästöprosentti
        total_syncs = stats.get("sync_count", 0) + stats.get("delta_count", 0)
        if total_syncs > 0:
            stats["efficiency_percent"] = (stats.get("delta_count", 0) / total_syncs) * 100
        else:
            stats["efficiency_percent"] = 0
        
        return stats
    
    def _load_sync_state(self) -> Dict[str, Any]:
        """Lataa synkronointitila"""
        if self.sync_state_file.exists():
            with open(self.sync_state_file, 'r') as f:
                return json.load(f)
        
        # Oletustila
        return {
            "election_id": self.election_id,
            "created": datetime.now().isoformat(),
            "sync_count": 0,
            "delta_count": 0,
            "total_savings_bytes": 0
        }
    
    def _save_sync_state(self):
        """Tallenna synkronointitila"""
        with open(self.sync_state_file, 'w') as f:
            json.dump(self.sync_state, f, indent=2)
    
    def reset_sync_state(self):
        """Nollaa synkronointitila (käytä testauksessa)"""
        self.sync_state = {
            "election_id": self.election_id,
            "created": datetime.now().isoformat(),
            "sync_count": 0,
            "delta_count": 0,
            "total_savings_bytes": 0
        }
        self._save_sync_state()
        print("🔄 Sync state reset")
