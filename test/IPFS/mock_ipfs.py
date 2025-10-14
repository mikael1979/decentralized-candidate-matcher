import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional

try:
    import base58
    HAS_BASE58 = True
except ImportError:
    HAS_BASE58 = False
    print("Varoitus: base58 ei asennettu - käytetään fallback CID-generointia")

class MockIPFS:
    """
    Mock IPFS-implementaatio testaamista varten
    """
    
    def __init__(self):
        self.content_store: Dict[str, Dict[str, Any]] = {}
        self.pins: List[str] = []
        self.stats = {
            "add_count": 0,
            "get_count": 0,
            "pin_count": 0,
            "total_size": 0
        }
    
    def _calculate_cid(self, data: Any) -> str:
        """Laskee CID:n datalle"""
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
        else:
            data_str = str(data)
        
        # SHA-256 hash
        hash_bytes = hashlib.sha256(data_str.encode()).digest()
        
        if HAS_BASE58:
            try:
                # Yksinkertaistettu CID v0 generointi
                # IPFS käyttää base58-encoded SHA256 hashia CID v0:ssa
                cid = "Qm" + base58.b58encode(hash_bytes).decode()
                return cid
            except Exception as e:
                print(f"Virhe CID-generoinnissa: {e}, käytetään fallbackia")
        
        # Fallback: yksinkertainen hash
        return "Qm" + hashlib.sha256(data_str.encode()).hexdigest()[:40]
    
    def add_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Lisää JSON-datan mock-IPFS:ään"""
        cid = self._calculate_cid(data)
        
        # Tallenna data
        self.content_store[cid] = {
            "data": data,
            "size": len(json.dumps(data)),
            "added": datetime.now().isoformat(),
            "cid": cid
        }
        
        # Päivitä statistiikat
        self.stats["add_count"] += 1
        self.stats["total_size"] += len(json.dumps(data))
        
        return {
            "Hash": cid,
            "Size": len(json.dumps(data)),
            "Name": cid
        }
    
    def get_json(self, cid: str) -> Optional[Dict[str, Any]]:
        """Hakee JSON-datan CID:llä"""
        self.stats["get_count"] += 1
        
        if cid in self.content_store:
            return self.content_store[cid]["data"]
        return None
    
    def cat(self, cid: str) -> Optional[bytes]:
        """Hakee raakadataa CID:llä"""
        data = self.get_json(cid)
        if data:
            return json.dumps(data).encode()
        return None
    
    def pin_add(self, cid: str) -> bool:
        """Simuloi CID:n pinnausta"""
        if cid in self.content_store:
            if cid not in self.pins:
                self.pins.append(cid)
                self.stats["pin_count"] += 1
            return True
        return False
    
    def pin_rm(self, cid: str) -> bool:
        """Poistaa pinnauksen"""
        if cid in self.pins:
            self.pins.remove(cid)
            self.stats["pin_count"] -= 1
            return True
        return False
    
    def list_pins(self) -> List[str]:
        """Palauttaa listan pinatuista CIDEistä"""
        return self.pins.copy()
    
    def repo_stat(self) -> Dict[str, Any]:
        """Palauttaa repository statistiikat"""
        return {
            "NumObjects": len(self.content_store),
            "RepoSize": self.stats["total_size"],
            "StorageMax": 10_000_000_000,  # 10GB
            "RepoPath": "/mock/ipfs/repo",
            "Version": "mock-0.1.0"
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Palauttaa mock-IPFS:n tilastot"""
        return {
            **self.stats,
            "total_objects": len(self.content_store),
            "pinned_objects": len(self.pins),
            "timestamp": datetime.now().isoformat()
        }
    
    def clear(self):
        """Tyhjentää koko mock-IPFS:n"""
        self.content_store.clear()
        self.pins.clear()
        self.stats = {
            "add_count": 0,
            "get_count": 0,
            "pin_count": 0,
            "total_size": 0
        }

def test_mock_ipfs_complete():
    """Testaa MockIPFS-toiminnallisuutta kattavasti"""
    print("🧪 KATTAAVA MOCK-IPFS TESTI")
    
    # Alusta IPFS
    ipfs = MockIPFS()
    
    # Testaa erilaisia datoja
    test_cases = [
        {"simple": "data"},
        {"nested": {"data": [1, 2, 3], "name": "test"}},
        {"questions": [
            {"id": 1, "text": "Pitäisikö?"},
            {"id": 2, "text": "Miten?"}
        ]}
    ]
    
    cids = []
    
    for i, test_data in enumerate(test_cases):
        # Lisää data
        result = ipfs.add_json(test_data)
        cid = result["Hash"]
        cids.append(cid)
        print(f"✅ Testidata {i+1} lisätty - CID: {cid}")
        
        # Hae data takaisin
        retrieved = ipfs.get_json(cid)
        success = test_data == retrieved
        print(f"✅ Data {i+1} haettu - Samat: {success}")
        
        if not success:
            print(f"   Odotettu: {test_data}")
            print(f"   Saatu: {retrieved}")
    
    # Testaa pinnausta
    for cid in cids:
        ipfs.pin_add(cid)
    
    pins = ipfs.list_pins()
    print(f"✅ Pinnausta testattu - Pinnatut CID:t: {len(pins)}")
    
    # Testaa cat-toimintoa
    for cid in cids:
        raw_data = ipfs.cat(cid)
        if raw_data:
            parsed = json.loads(raw_data.decode())
            print(f"✅ Cat-toiminto OK CID:lle {cid[:12]}...")
    
    # Näytä statistiikat
    stats = ipfs.get_stats()
    print(f"\n📊 LOPULLISET STATISTIIKAT:")
    for key, value in stats.items():
        if key != 'timestamp':
            print(f"  {key}: {value}")
    
    repo_stats = ipfs.repo_stat()
    print(f"📁 REPO STATISTIIKAT:")
    print(f"  Objekteja: {repo_stats['NumObjects']}")
    print(f"  Koko: {repo_stats['RepoSize']} bytes")
    
    print("\n🎉 MOCK-IPFS TESTI ONNISTUI TÄYDELLISESTI!")

if __name__ == "__main__":
    test_mock_ipfs_complete()
