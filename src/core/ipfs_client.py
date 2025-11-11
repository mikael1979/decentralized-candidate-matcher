import ipfshttpclient
from typing import Optional

class MockIPFSClient:
    """Mock IPFS client for testing"""
    def add_json(self, data):
        return {'Hash': f'mock_cid_{hash(str(data))}'}
    
    def get_json(self, cid):
        return {'mock': 'data'}

class IPFSClient:
    _instance: Optional['IPFSClient'] = None
    
    def __init__(self):
        self._client = None
        self._connect()
    
    def _connect(self):
        """Yhdistä IPFS:ään tai käytä mockia"""
        try:
            self._client = ipfshttpclient.connect()
        except Exception:
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
