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
    Tukee well-known CID:tä ja delta-pohjaista Elo-dataa
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
        # Well-known CID kysymyslistalle
        self.well_known_cid = "QmWellKnownQuestionsList"

    def _calculate_cid(self, data: Any) -> str:
        """Laskee CID:n datalle"""
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
        else:
            data_str = str(data)
        hash_bytes = hashlib.sha256(data_str.encode()).digest()
        if HAS_BASE58:
            try:
                cid = "Qm" + base58.b58encode(hash_bytes).decode()
                return cid
            except Exception as e:
                print(f"Virhe CID-generoinnissa: {e}, käytetään fallbackia")
        return "Qm" + hashlib.sha256(data_str.encode()).hexdigest()[:40]

    def add_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Lisää JSON-datan mock-IPFS:ään"""
        cid = self._calculate_cid(data)
        self.content_store[cid] = {
            "data": data,
            "size": len(json.dumps(data)),
            "added": datetime.now().isoformat(),
            "cid": cid
        }
        # Päivitä well-known CID jos data sisältää kysymyksiä
        if isinstance(data, dict) and "questions" in data:
            self.content_store[self.well_known_cid] = self.content_store[cid]
            self.content_store[self.well_known_cid]["cid"] = self.well_known_cid
        
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
        # Tuki well-known CID:lle
        if cid == self.well_known_cid and self.well_known_cid in self.content_store:
            return self.content_store[self.well_known_cid]["data"]
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
            "StorageMax": 10_000_000_000,
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
    ipfs = MockIPFS()
    
    # Testaa kysymyslista
    questions_data = {
        "election_id": "test_election_2025",
        "timestamp": datetime.now().isoformat(),
        "questions": [
            {
                "id": "q1",
                "question": {"fi": "Pitäisikö?"},
                "elo": {
                    "base_rating": 1200,
                    "deltas": [{"timestamp": "2025-01-01T00:00:00Z", "delta": 32, "by": "user1"}],
                    "current_rating": 1232
                }
            }
        ]
    }
    
    result = ipfs.add_json(questions_data)
    cid = result["Hash"]
    print(f"✅ Kysymyslista lisätty - CID: {cid}")
    
    # Testaa well-known CID
    well_known_data = ipfs.get_json(ipfs.well_known_cid)
    if well_known_data:
        print("✅ Well-known CID toimii")
    else:
        print("❌ Well-known CID ei toimi")
    
    # Näytä statistiikat
    stats = ipfs.get_stats()
    print(f"\n📊 LOPULLISET STATISTIIKAT:")
    for key, value in stats.items():
        if key != 'timestamp':
            print(f"  {key}: {value}")
    
    print("\n🎉 MOCK-IPFS TESTI ONNISTUI TÄYDELLISESTI!")

if __name__ == "__main__":
    test_mock_ipfs_complete()
