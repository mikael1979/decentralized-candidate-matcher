# mock_ipfs.py
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional

class MockIPFS:
    """
    Mock-IPFS toteutus testausta varten.
    Simuloi IPFS-verkkoa ilman ulkoisia riippuvuuksia.
    """
    
    def __init__(self, persist_data: bool = True, data_file: str = "mock_ipfs_data.json"):
        self.content_store: Dict[str, Any] = {}
        self.cid_counter = 0
        self.persist_data = persist_data
        self.data_file = data_file
        
        # Lataa aiemmat mock-datat jos saatavilla
        if persist_data:
            self._load_mock_data()
    
    def _load_mock_data(self):
        """Lataa aiemmat mock-datat tiedostosta"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.content_store = json.load(f)
                self.cid_counter = len(self.content_store)
            print(f"Mock-IPFS: Ladattu {len(self.content_store)} CID:ä tiedostosta")
        except FileNotFoundError:
            print("Mock-IPFS: Ei aiempaa dataa, aloitetaan tyhjästä")
            self.content_store = {}
    
    def _save_mock_data(self):
        """Tallentaa mock-datat tiedostoon"""
        if self.persist_data:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.content_store, f, indent=2, ensure_ascii=False)
            print(f"Mock-IPFS: Tallennettu {len(self.content_store)} CID:ä tiedostoon")
    
    def upload(self, data: Dict[str, Any]) -> str:
        """
        Mock IPFS-upload: generoi CID ja tallentaa dataan mock-tietokantaan
        """
        # Generoi deterministinen CID datasta
        content_string = json.dumps(data, sort_keys=True, ensure_ascii=False)
        content_hash = hashlib.sha256(content_string.encode('utf-8')).hexdigest()
        cid = f"QmMock{content_hash[:40]}"
        
        # Tallenna data mock-tietokantaan
        self.content_store[cid] = {
            "data": data,
            "upload_timestamp": datetime.now().isoformat(),
            "size_bytes": len(content_string.encode('utf-8')),
            "access_count": 0
        }
        
        self.cid_counter += 1
        
        # Tallenna pysyväistila jos haluttu
        self._save_mock_data()
        
        print(f"Mock-IPFS: Upload onnistui - CID: {cid}")
        return cid
    
    def download(self, cid: str) -> Optional[Dict[str, Any]]:
        """
        Mock IPFS-download: hakee dataa mock-tietokannasta CID:llä
        """
        if cid in self.content_store:
            # Päivitä käyttötilastot
            self.content_store[cid]["access_count"] += 1
            self.content_store[cid]["last_access"] = datetime.now().isoformat()
            
            self._save_mock_data()
            
            print(f"Mock-IPFS: Download onnistui - CID: {cid}")
            return self.content_store[cid]["data"]
        else:
            print(f"Mock-IPFS: CID:ä ei löydy - {cid}")
            return None
    
    def pin(self, cid: str) -> bool:
        """Mock IPFS-pin - merkitsee datan pysyväksi"""
        if cid in self.content_store:
            self.content_store[cid]["pinned"] = True
            self.content_store[cid]["pinned_at"] = datetime.now().isoformat()
            self._save_mock_data()
            print(f"Mock-IPFS: CID pinned: {cid}")
            return True
        return False
    
    def unpin(self, cid: str) -> bool:
        """Mock IPFS-unpin - poistaa pysyvyysmerkinnän"""
        if cid in self.content_store:
            self.content_store[cid]["pinned"] = False
            self._save_mock_data()
            print(f"Mock-IPFS: CID unpinned: {cid}")
            return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Palauttaa mock-IPFS tilastot"""
        total_size = sum(item["size_bytes"] for item in self.content_store.values())
        pinned_count = sum(1 for item in self.content_store.values() if item.get("pinned", False))
        
        return {
            "total_cids": len(self.content_store),
            "total_size_bytes": total_size,
            "pinned_cids": pinned_count,
            "total_access_count": sum(item.get("access_count", 0) for item in self.content_store.values())
        }
    
    def clear_mock_data(self):
        """Tyhjentää mock-datat (testausta varten)"""
        self.content_store = {}
        self.cid_counter = 0
        if self.persist_data:
            import os
            try:
                os.remove(self.data_file)
            except FileNotFoundError:
                pass
        print("Mock-IPFS: Kaikki data tyhjennetty")
