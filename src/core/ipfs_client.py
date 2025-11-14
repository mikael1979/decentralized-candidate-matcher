#!/usr/bin/env python3
"""
IPFS-client, joka käyttää suoraan IPFS HTTP API:ta requests-kirjaston kautta
Tukee kaikkia IPFS Kubo versioita (0.10.0+)
"""
import requests
import json
import time
from typing import Dict, Any, Optional, List
from pathlib import Path

class MockIPFSClient:
    """Mock IPFS-client testausta varten"""
    
    def __init__(self):
        self.mock_data = {}
        print("🔶 Käytetään stabiilia mock IPFS-clientia")
    
    def add_json(self, data: Dict) -> Dict[str, str]:
        import hashlib
        content = json.dumps(data, sort_keys=True, ensure_ascii=False)
        cid = f"mock_{hashlib.md5(content.encode()).hexdigest()[:16]}"
        self.mock_data[cid] = data
        return {'Hash': cid}
    
    def get_json(self, cid: str) -> Dict:
        return self.mock_data.get(cid, {"error": "Data not found"})
    
    def add_bytes(self, data: bytes, content_type: str = 'application/octet-stream') -> Dict[str, str]:
        import hashlib
        cid = f"mock_{hashlib.md5(data).hexdigest()[:16]}"
        self.mock_data[cid] = data
        return {'Hash': cid}
    
    def cat(self, cid: str) -> bytes:
        data = self.mock_data.get(cid)
        if isinstance(data, bytes):
            return data
        return json.dumps(data or {}).encode()

class RealIPFSClient:
    """Oikea IPFS-client, joka käyttää HTTP API:ta"""
    
    def __init__(self, api_url: str = "http://127.0.0.1:5001", timeout: int = 30):
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        
        # Testaa yhteys
        try:
            response = self.session.post(f"{self.api_url}/api/v0/version", timeout=5)
            if response.status_code == 200:
                version_info = response.json()
                print(f"✅ IPFS yhdistetty: {version_info.get('Version', 'Unknown')}")
            else:
                raise Exception(f"IPFS API returned status {response.status_code}")
        except Exception as e:
            raise Exception(f"IPFS ei saatavilla: {e}")
    
    def add_json(self, data: Dict) -> Dict[str, str]:
        """Lisää JSON-data IPFS:ään"""
        try:
            # Muunna JSONiksi
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            files = {
                'file': ('data.json', json_str, 'application/json')
            }
            
            response = self.session.post(
                f"{self.api_url}/api/v0/add",
                files=files,
                params={'pin': 'true'},
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            return result
            
        except Exception as e:
            raise Exception(f"IPFS lisäys epäonnistui: {e}")
    
    def get_json(self, cid: str) -> Dict:
        """Hae JSON-data IPFS:stä"""
        try:
            response = self.session.post(
                f"{self.api_url}/api/v0/cat",
                params={'arg': cid},
                timeout=self.timeout
            )
            response.raise_for_status()
            return json.loads(response.text)
        except Exception as e:
            raise Exception(f"IPFS haku epäonnistui: {e}")
    
    def add_bytes(self, data: bytes, content_type: str = 'application/octet-stream') -> Dict[str, str]:
        """Lisää raakadata IPFS:ään"""
        try:
            files = {
                'file': ('content.html', data, content_type)
            }
            
            response = self.session.post(
                f"{self.api_url}/api/v0/add",
                files=files,
                params={'pin': 'true'},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"IPFS bytes lisäys epäonnistui: {e}")
    
    def cat(self, cid: str) -> bytes:
        """Hae raakadata IPFS:stä"""
        try:
            response = self.session.post(
                f"{self.api_url}/api/v0/cat",
                params={'arg': cid},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.content
        except Exception as e:
            raise Exception(f"IPFS cat epäonnistui: {e}")

class IPFSClient:
    """Pää-IPFS-client, joka valitsee automaattisesti oikean toteutuksen"""
    
    _instances = {}
    
    def __init__(self, election_id: str = "default"):
        self.election_id = election_id
        
        # Yritä ensin oikeaa IPFS:ää
        try:
            self._client = RealIPFSClient()
            print(f"✅ Oikea IPFS-client käytössä vaalille: {election_id}")
        except Exception as e:
            # Fallback mock-clientiin
            self._client = MockIPFSClient()
            print(f"🔶 Mock IPFS-client käytössä vaalille: {election_id}")
    
    @classmethod
    def get_client(cls, election_id: str = "default") -> 'IPFSClient':
        if election_id not in cls._instances:
            cls._instances[election_id] = IPFSClient(election_id)
        return cls._instances[election_id]
    
    def publish_election_data(self, data_type: str, data: Dict) -> str:
        """Julkaise vaalidata IPFS:ään ja palauta CID"""
        try:
            # Lisää metadata
            full_data = {
                "metadata": {
                    "type": data_type,
                    "election_id": self.election_id,
                    "timestamp": time.time(),
                    "version": "1.0"
                },
                "data": data
            }
            
            result = self._client.add_json(full_data)
            cid = result['Hash']
            print(f"✅ {data_type} julkaistu IPFS:ään: {cid}")
            return cid
            
        except Exception as e:
            print(f"❌ IPFS-julkaisu epäonnistui: {e}")
            # Fallback mock-CID:lle
            return f"mock_fallback_{data_type}_{int(time.time())}"

    def publish_html_content(self, content: str, filename: str = "profile.html") -> str:
        """Julkaise suoraan HTML-sisältö IPFS:ään"""
        try:
            # Muunna HTML-sisältö bytes-muotoon
            html_bytes = content.encode('utf-8')
            
            # Julkaise suoraan HTML-sisältö
            result = self._client.add_bytes(html_bytes, 'text/html; charset=utf-8')
            cid = result['Hash']
            print(f"✅ HTML-sisältö julkaistu IPFS:ään: {cid}")
            return cid
            
        except Exception as e:
            print(f"❌ HTML-julkaisu epäonnistui: {e}")
            return f"mock_html_{int(time.time())}"
    
    def retrieve_election_data(self, cid: str) -> Dict:
        """Hae vaalidata IPFS:stä"""
        try:
            data = self._client.get_json(cid)
            return data
        except Exception as e:
            print(f"❌ IPFS-haku epäonnistui: {e}")
            return {"error": str(e)}

    def retrieve_html_content(self, cid: str) -> str:
        """Hae HTML-sisältö IPFS:stä"""
        try:
            content = self._client.cat(cid)
            return content.decode('utf-8')
        except Exception as e:
            print(f"❌ HTML-haku epäonnistui: {e}")
            return f"<html><body>Error: {e}</body></html>"

    def add_file(self, file_path: Path) -> str:
        """Lisää tiedosto IPFS:ään"""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.name, f, 'application/octet-stream')}
                
                if isinstance(self._client, RealIPFSClient):
                    response = self._client.session.post(
                        f"{self._client.api_url}/api/v0/add",
                        files=files,
                        params={'pin': 'true'},
                        timeout=self._client.timeout
                    )
                    response.raise_for_status()
                    result = response.json()
                    return result['Hash']
                else:
                    # Mock-toteutus
                    data = f.read()
                    result = self._client.add_bytes(data)
                    return result['Hash']
                    
        except Exception as e:
            print(f"❌ Tiedoston lisäys IPFS:ään epäonnistui: {e}")
            return f"mock_file_{file_path.stem}_{int(time.time())}"

# Testaus
if __name__ == "__main__":
    client = IPFSClient.get_client("test")
    
    # Testidata
    test_data = {
        "test": "data",
        "timestamp": time.time()
    }
    
    # Testaa julkaisu
    cid = client.publish_election_data("test_type", test_data)
    print(f"Testi CID: {cid}")
    
    # Testaa haku
    if not cid.startswith("mock"):
        retrieved = client.retrieve_election_data(cid)
        print(f"Haettu data: {retrieved}")
