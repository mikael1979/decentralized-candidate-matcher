#!/usr/bin/env python3
"""
IPFS-synkronoinnin hallinta Jumaltenvaaleille
"""
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# KORJATTU: Käytetään absoluuttisia importteja
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.ipfs_client import IPFSClient

class IPFSSyncManager:
    def __init__(self, election_id: str = "Jumaltenvaalit2026"):
        self.election_id = election_id
        self.ipfs = IPFSClient.get_client(election_id)
        self.sync_file = Path("data/runtime/ipfs_sync.json")
    
    def full_sync(self) -> Dict:
        """Suorita täysi synkronointi IPFS:ään"""
        print("🔄 Synkronoidaan Jumaltenvaalit IPFS:ään...")
        
        # Synkronoi kaikki data
        ipfs_cids = self.ipfs.sync_local_to_ipfs()
        
        # Luo synkronointiraportti
        sync_report = {
            "election_id": self.election_id,
            "sync_type": "full",
            "timestamp": datetime.now().isoformat(),
            "ipfs_cids": ipfs_cids,
            "files_synced": len([cid for cid in ipfs_cids.values() if cid]),
            "status": "completed"
        }
        
        # Tallenna raportti
        self._save_sync_report(sync_report)
        
        print(f"✅ Synkronointi valmis! {sync_report['files_synced']} tiedostoa IPFS:ään")
        return sync_report
    
    def incremental_sync(self) -> Dict:
        """Suorita inkrementaalinen synkronointi"""
        print("🔄 Suoritetaan inkrementaalinen IPFS-synkronointi...")
        
        # Lataa edellinen synkronointitila
        last_sync = self._load_last_sync()
        
        # Tarkista muuttuneet tiedostot
        changed_files = self._get_changed_files(last_sync)
        
        if not changed_files:
            print("✅ Ei muutoksia synkronoitavaksi")
            return {"status": "no_changes"}
        
        # Synkronoi muuttuneet tiedostot
        results = {}
        for file_type in changed_files:
            file_path = f"data/runtime/{file_type}.json"
            if Path(file_path).exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                cid = self.ipfs.publish_election_data(file_type, data)
                results[file_type] = cid
        
        # Päivitä synkronointitila
        sync_report = {
            "election_id": self.election_id,
            "sync_type": "incremental",
            "timestamp": datetime.now().isoformat(),
            "changed_files": changed_files,
            "ipfs_cids": results,
            "status": "completed"
        }
        
        self._save_sync_report(sync_report)
        print(f"✅ Inkrementaalinen synkronointi valmis! {len(results)} tiedostoa päivitetty")
        return sync_report
    
    def verify_sync_integrity(self) -> Dict:
        """Varmista synkronoidun datan eheys"""
        print("🔍 Tarkistetaan IPFS-synkronoinnin eheys...")
        
        last_sync = self._load_last_sync()
        if not last_sync or 'ipfs_cids' not in last_sync:
            return {"status": "no_sync_data"}
        
        verification_results = {}
        
        for file_type, cid in last_sync['ipfs_cids'].items():
            if not cid or cid.startswith('mock_'):
                verification_results[file_type] = "skipped_mock"
                continue
            
            file_path = f"data/runtime/{file_type}.json"
            if Path(file_path).exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    local_data = json.load(f)
                
                is_valid = self.ipfs.verify_data_integrity(local_data, cid)
                verification_results[file_type] = "valid" if is_valid else "invalid"
            else:
                verification_results[file_type] = "file_missing"
        
        valid_count = sum(1 for result in verification_results.values() if result == "valid")
        
        report = {
            "election_id": self.election_id,
            "verification_timestamp": datetime.now().isoformat(),
            "results": verification_results,
            "valid_files": valid_count,
            "total_files": len(verification_results),
            "status": "completed"
        }
        
        print(f"✅ Eheystarkistus valmis! {valid_count}/{len(verification_results)} tiedostoa validi")
        return report
    
    def _get_changed_files(self, last_sync: Optional[Dict]) -> List[str]:
        """Hae muuttuneet tiedostot"""
        if not last_sync or 'ipfs_cids' not in last_sync:
            return ['parties', 'questions', 'candidates', 'meta']
        
        changed = []
        data_files = {
            'parties': 'data/runtime/parties.json',
            'questions': 'data/runtime/questions.json',
            'candidates': 'data/runtime/candidates.json', 
            'meta': 'data/runtime/meta.json'
        }
        
        for file_type, file_path in data_files.items():
            if not Path(file_path).exists():
                continue
            
            # Tarkista onko tiedosto muuttunut
            current_hash = self._calculate_file_hash(file_path)
            last_hash = last_sync.get('file_hashes', {}).get(file_type)
            
            if current_hash != last_hash:
                changed.append(file_type)
        
        return changed
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Laske tiedoston tiiviste"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _load_last_sync(self) -> Optional[Dict]:
        """Lataa edellinen synkronointitila"""
        if self.sync_file.exists():
            with open(self.sync_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def _save_sync_report(self, report: Dict):
        """Tallenna synkronointiraportti"""
        # Lisää tiedostojen tiivisteet
        file_hashes = {}
        data_files = ['parties', 'questions', 'candidates', 'meta']
        
        for file_type in data_files:
            file_path = f"data/runtime/{file_type}.json"
            if Path(file_path).exists():
                file_hashes[file_type] = self._calculate_file_hash(file_path)
        
        report['file_hashes'] = file_hashes
        
        # Tallenna
        with open(self.sync_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
