import requests
import json
from typing import Dict, Any, Optional

class RealIPFS:
    """
    Yksinkertainen IPFS-asiakas joka käyttää IPFS HTTP API:a
    """
    
    def __init__(self, host='127.0.0.1', port=5001):
        self.base_url = f"http://{host}:{port}/api/v0"
        self.connected = self._test_connection()
    
    def _test_connection(self):
        """Testaa IPFS-solmun saatavuutta"""
        try:
            response = requests.post(f"{self.base_url}/id", timeout=5)
            return response.status_code == 200
        except:
            print("❌ IPFS-solmu ei ole käynnissä. Käytetään fallback-tietoja.")
            return False
    
    def add_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Lisää JSON-datan IPFS:ään käyttäen HTTP API:a"""
        if not self.connected:
            # Fallback mock-toteutus
            return self._mock_add_json(data)
            
        try:
            # Muunna data JSON-muotoon
            json_data = json.dumps(data, ensure_ascii=False)
            
            # Lähetä data IPFS:ään
            files = {'file': ('data.json', json_data, 'application/json')}
            response = requests.post(f"{self.base_url}/add", files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Data tallennettu IPFS:ään CID:llä: {result['Hash']}")
                return {
                    "Hash": result["Hash"],
                    "Size": result["Size"],
                    "Name": result["Name"]
                }
            else:
                raise Exception(f"IPFS add failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Virhe IPFS:ään lisättäessä: {e}")
            # Fallback mock-toteutus
            return self._mock_add_json(data)
    
    def get_json(self, cid: str) -> Optional[Dict[str, Any]]:
        """Hakee JSON-datan IPFS:stä käyttäen HTTP API:a"""
        if not self.connected:
            # Fallback mock-toteutus
            return self._mock_get_json(cid)
            
        try:
            response = requests.post(f"{self.base_url}/cat", params={'arg': cid}, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            print(f"❌ Virhe IPFS:stä haettaessa: {e}")
            # Fallback mock-toteutus
            return self._mock_get_json(cid)
    
    def pin_add(self, cid: str) -> bool:
        """Pinnaa CID:n IPFS:ään"""
        if not self.connected:
            return True  # Mock-pinaus aina onnistuu
            
        try:
            response = requests.post(f"{self.base_url}/pin/add", params={'arg': cid}, timeout=30)
            return response.status_code == 200
        except:
            return False
    
    def _mock_add_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock-toteutus IPFS:än lisäykselle"""
        import hashlib
        import time
        
        # Luo mock-CID
        json_str = json.dumps(data, sort_keys=True)
        hash_obj = hashlib.sha256(json_str.encode())
        mock_cid = f"mock_{hash_obj.hexdigest()[:16]}"
        
        print(f"🔶 Mock-IPFS: Data tallennettu mock-CID:llä: {mock_cid}")
        
        return {
            "Hash": mock_cid,
            "Size": len(json_str),
            "Name": "data.json"
        }
    
    def _mock_get_json(self, cid: str) -> Optional[Dict[str, Any]]:
        """Mock-toteutus IPFS:stä haulle"""
        # Tässä mock-toteutuksessa palautetaan aina None
        # Oikeassa toteutuksessa voitaisiin pitää kirjaa mock-datasta
        return None

# Yksinkertainen IPFS API wrapper
class IPFSAPI:
    @staticmethod
    def add(file_path):
        """Wrapper ipfshttpclientin add-metodille"""
        # Tämä on yksinkertaistettu versio
        # Oikeassa käytössä tarvitaan ipfshttpclient
        return [{'Hash': 'mock_hash', 'Size': 1024}]
    
    @staticmethod
    def get(cid, path):
        """Wrapper ipfshttpclientin get-metodille"""
        # Mock-toteutus
        with open(path, 'w') as f:
            f.write('{"mock": "data"}')

# Alias vanhaa koodia varten
ipfs_api = IPFSAPI()
