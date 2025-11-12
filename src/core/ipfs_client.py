#!/usr/bin/env python3
"""
IPFS-integrointi Jumaltenvaaleille - Stabiili mock-versio
"""
import json
import hashlib
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path

class IPFSClient:
    _instance: Optional['IPFSClient'] = None
    
    def __init__(self, election_id: str = "Jumaltenvaalit2026"):
        self.election_id = election_id
        self._client = MockIPFSClient()  # Aina mock-tilassa
        print("🔶 Käytetään stabiilia mock IPFS-clientia")
    
    @classmethod
    def get_client(cls, election_id: str = "Jumaltenvaalit2026") -> 'IPFSClient':
        if cls._instance is None:
            cls._instance = IPFSClient(election_id=election_id)
        return cls._instance
    
    def publish_election_data(self, data_type: str, data: Dict) -> str:
        """Julkaise vaalidata IPFS:ään (mock)"""
        try:
            # Lisää metadata
            enhanced_data = {
                "data": data,
                "metadata": {
                    "election_id": self.election_id,
                    "data_type": data_type,
                    "timestamp": datetime.now().isoformat(),
                    "version": "1.0"
                }
            }
            
            # Käytä mock-clientia
            cid = self._client.add_json(enhanced_data)
            
            print(f"✅ {data_type} julkaistu IPFS:ään (mock): {cid}")
            return cid
            
        except Exception as e:
            print(f"❌ IPFS-julkaisu epäonnistui: {e}")
            return f"mock_cid_{hashlib.sha256(json.dumps(data).encode()).hexdigest()[:16]}"
    
    def sync_local_to_ipfs(self) -> Dict[str, str]:
        """Synkronoi kaikki paikallinen data IPFS:ään (mock)"""
        data_files = {
            "parties": "data/runtime/parties.json",
            "questions": "data/runtime/questions.json", 
            "candidates": "data/runtime/candidates.json",
            "meta": "data/runtime/meta.json"
        }
        
        results = {}
        
        for data_type, file_path in data_files.items():
            if Path(file_path).exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    cid = self.publish_election_data(data_type, data)
                    results[data_type] = cid
                    
                except Exception as e:
                    print(f"❌ {data_type} synkronointi epäonnistui: {e}")
                    results[data_type] = None
        
        # Tallenna CID:t
        sync_info = {
            "election_id": self.election_id,
            "sync_timestamp": datetime.now().isoformat(),
            "ipfs_cids": results,
            "synced_files": list(results.keys())
        }
        
        sync_file = "data/runtime/ipfs_sync.json"
        Path(sync_file).parent.mkdir(parents=True, exist_ok=True)
        with open(sync_file, 'w', encoding='utf-8') as f:
            json.dump(sync_info, f, indent=2)
        
        print(f"📊 Synkronoitu {len(results)} tiedostoa IPFS:ään (mock)")
        return results
    
    def fetch_from_ipfs(self, cid: str) -> Optional[Dict]:
        """Hae data IPFS:stä CID:llä (mock)"""
        try:
            data = self._client.get_json(cid)
            return data
        except Exception as e:
            print(f"❌ IPFS-haku epäonnistui CID:llä {cid}: {e}")
            return None
    
    def verify_data_integrity(self, local_data: Dict, ipfs_cid: str) -> bool:
        """Varmista datan eheys verrattuna IPFS:ään (mock)"""
        try:
            ipfs_data = self.fetch_from_ipfs(ipfs_cid)
            if not ipfs_data:
                return False
            
            # Vertaa dataa (huomioi metadata)
            local_hash = hashlib.sha256(
                json.dumps(local_data, sort_keys=True).encode()
            ).hexdigest()
            
            ipfs_hash = hashlib.sha256(
                json.dumps(ipfs_data.get('data', {}), sort_keys=True).encode()
            ).hexdigest()
            
            return local_hash == ipfs_hash
            
        except Exception as e:
            print(f"❌ Eheystarkistus epäonnistui: {e}")
            return False

class MockIPFSClient:
    """Stabiili mock IPFS client kehitystä varten"""
    def __init__(self):
        self._storage = {}
    
    def add_json(self, data):
        """Mock-add_json"""
        import hashlib
        content = json.dumps(data, sort_keys=True)
        cid = f"mock_{hashlib.sha256(content.encode()).hexdigest()[:16]}"
        self._storage[cid] = data
        return cid
    
    def get_json(self, cid):
        """Mock-get_json"""
        if cid in self._storage:
            return self._storage[cid]
        raise Exception(f"CID ei löydy: {cid}")
