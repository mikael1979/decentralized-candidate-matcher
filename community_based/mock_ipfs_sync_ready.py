[file name]: mock_ipfs_sync_ready.py
[file content begin]
"""
Mock-IPFS synkronointivalmiilla rajapinnalla
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional

class MockIPFSSyncReady:
    """
    Mock-IPFS joka tukee synkronointia oikeaan IPFS:ään
    """
    
    def __init__(self, persist_data: bool = True, data_file: str = "mock_ipfs_data.json"):
        self.content_store: Dict[str, Any] = {}
        self.persist_data = persist_data
        self.data_file = data_file
        
        # Lataa aiemmat datat
        if persist_data:
            self._load_mock_data()
    
    def _load_mock_data(self):
        """Lataa aiemmat mock-datat"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.content_store = json.load(f)
            print(f"✅ Mock-IPFS: Ladattu {len(self.content_store)} CID:ä")
        except FileNotFoundError:
            self.content_store = {}
            print("✅ Mock-IPFS: Aloitetaan tyhjästä")
    
    def _save_mock_data(self):
        """Tallentaa mock-datat"""
        if self.persist_data:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.content_store, f, indent=2, ensure_ascii=False)
    
    def upload(self, data: Dict[str, Any]) -> str:
        """Mock IPFS-upload"""
        # Generoi deterministinen CID
        content_string = json.dumps(data, sort_keys=True, ensure_ascii=False)
        content_hash = hashlib.sha256(content_string.encode('utf-8')).hexdigest()
        cid = f"QmMock{content_hash[:40]}"
        
        # Tallenna mock-tietokantaan
        self.content_store[cid] = {
            "data": data,
            "upload_timestamp": datetime.now().isoformat(),
            "size_bytes": len(content_string.encode('utf-8')),
            "access_count": 0,
            "source": "mock"
        }
        
        self._save_mock_data()
        print(f"✅ Mock-IPFS: Upload - CID: {cid}")
        return cid
    
    def download(self, cid: str) -> Optional[Dict[str, Any]]:
        """Mock IPFS-download"""
        if cid in self.content_store:
            # Päivitä tilastot
            self.content_store[cid]["access_count"] += 1
            self.content_store[cid]["last_access"] = datetime.now().isoformat()
            self._save_mock_data()
            
            print(f"✅ Mock-IPFS: Download - CID: {cid}")
            return self.content_store[cid]["data"]
        else:
            print(f"❌ Mock-IPFS: CID:ä ei löydy - {cid}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Palauttaa mock-IPFS tilastot"""
        total_size = sum(item["size_bytes"] for item in self.content_store.values())
        total_access = sum(item.get("access_count", 0) for item in self.content_store.values())
        
        return {
            "total_cids": len(self.content_store),
            "total_size_bytes": total_size,
            "total_access_count": total_access,
            "mock_data_file": self.data_file
        }
    
    def get_all_cids(self) -> List[str]:
        """Palauttaa kaikki CID:t"""
        return list(self.content_store.keys())
    
    def get_cid_info(self, cid: str) -> Optional[Dict[str, Any]]:
        """Palauttaa CID:n tiedot"""
        return self.content_store.get(cid)
    
    def import_from_real_ipfs(self, real_cid: str, data: Dict[str, Any]) -> str:
        """
        Tuo dataa oikeasta IPFS:stä mock-IPFS:ään
        """
        # Käytä oikeaa CID:ä mock-datassa
        self.content_store[real_cid] = {
            "data": data,
            "upload_timestamp": datetime.now().isoformat(),
            "size_bytes": len(json.dumps(data, ensure_ascii=False).encode('utf-8')),
            "access_count": 0,
            "source": "real_ipfs_imported",
            "original_real_cid": real_cid
        }
        
        self._save_mock_data()
        print(f"✅ Tuotu oikeasta IPFS:stä mockiin: {real_cid}")
        return real_cid
    
    def clear_mock_data(self):
        """Tyhjentää mock-datat"""
        self.content_store = {}
        if self.persist_data:
            import os
            try:
                os.remove(self.data_file)
            except FileNotFoundError:
                pass
        print("✅ Mock-IPFS data tyhjennetty")
[file content end]
