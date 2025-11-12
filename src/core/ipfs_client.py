import ipfshttpclient
from typing import Optional, Dict

class IPFSClient:
    _instance: Optional['IPFSClient'] = None
    
    def __init__(self):
        self._client = None
        self._connect()
    
    def _connect(self):
        """Yhdistä IPFS:ään"""
        try:
            self._client = ipfshttpclient.connect()
            print("✅ IPFS-yhteys muodostettu")
        except Exception as e:
            print(f"❌ IPFS-yhteys epäonnistui: {e}")
            self._client = MockIPFSClient()
    
    @classmethod
    def get_client(cls) -> 'IPFSClient':
        if cls._instance is None:
            cls._instance = IPFSClient()
        return cls._instance
    
    def add_data(self, data: dict) -> str:
        """Lisää data IPFS:ään ja palauta CID"""
        result = self._client.add_json(data)
        return result['Hash']
    
    def get_data(self, cid: str) -> dict:
        """Hae data IPFS:stä CID:llä"""
        return self._client.get_json(cid)

class MockIPFSClient:
    """Mock IPFS client for development"""
    def __init__(self):
        self._storage = {}
        print("🔶 Käytetään mock IPFS-clientia")
    
    def add_json(self, data: Dict) -> Dict:
        """Simuloi data-tallennus"""
        import hashlib
        content = json.dumps(data, sort_keys=True)
        cid = f"mock_{hashlib.sha256(content.encode()).hexdigest()[:16]}"
        self._storage[cid] = data
        return {'Hash': cid}
    
    def get_json(self, cid: str) -> Dict:
        """Simuloi data-haku"""
        if cid in self._storage:
            return self._storage[cid]
        raise Exception(f"CID ei löydy: {cid}")
