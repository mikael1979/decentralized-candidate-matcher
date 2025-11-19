# src/core/ipfs/client.py
"""
Yksinkertaistettu IPFS-client - tukee uusia archive/delta moduuleja
"""
import json
import requests
from typing import Dict, Any, Optional

class IPFSClient:
    """Yksinkertaistettu IPFS-client uusille moduuleille"""
    
    def __init__(self, api_url: str = "http://127.0.0.1:5001", timeout: int = 30):
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout
        self.connected = self._test_connection()
        
        if self.connected:
            print("✅ Connected to IPFS")
        else:
            print("🔶 Using mock IPFS mode")
    
    def _test_connection(self) -> bool:
        """Testaa IPFS-yhteys"""
        try:
            response = requests.post(f"{self.api_url}/api/v0/version", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def add_json(self, data: Dict) -> str:
        """Lisää JSON-data IPFS:ään"""
        if not self.connected:
            return self._mock_add(data)
        
        try:
            files = {'file': ('data.json', json.dumps(data), 'application/json')}
            response = requests.post(
                f"{self.api_url}/api/v0/add",
                files=files,
                params={'pin': 'true'},
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            return result['Hash']
        except Exception as e:
            print(f"IPFS add failed: {e}")
            return self._mock_add(data)
    
    def get_json(self, cid: str) -> Dict:
        """Hae JSON-data IPFS:stä"""
        if not self.connected:
            return self._mock_get(cid)
        
        try:
            response = requests.post(
                f"{self.api_url}/api/v0/cat",
                params={'arg': cid},
                timeout=self.timeout
            )
            response.raise_for_status()
            return json.loads(response.text)
        except Exception as e:
            print(f"IPFS get failed: {e}")
            return self._mock_get(cid)
    
    def _mock_add(self, data: Dict) -> str:
        """Mock-toteutus"""
        import hashlib
        data_str = json.dumps(data, sort_keys=True)
        return f"mock_{hashlib.md5(data_str.encode()).hexdigest()[:16]}"
    
    def _mock_get(self, cid: str) -> Dict:
        """Mock-haku"""
        return {"mock_data": True, "cid": cid, "type": "mock"}
