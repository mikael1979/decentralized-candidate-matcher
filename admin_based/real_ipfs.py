import requests
import json
from typing import Dict, Any, Optional

class RealIPFS:
    """
    Yksinkertainen IPFS-asiakas joka käyttää IPFS HTTP API:a
    Tukee well-known CID:tä ja delta-pohjaista Elo-dataa
    """
    def __init__(self, host='127.0.0.1', port=5001):
        self.base_url = f"http://{host}:{port}/api/v0"
        self.connected = self._test_connection()
        # Well-known CID kysymyslistalle (tämä pitää päivittää IPNS:llä tuotannossa)
        self.well_known_cid = "QmWellKnownQuestionsList"

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
            return self._mock_add_json(data)
        try:
            json_data = json.dumps(data, ensure_ascii=False)
            files = {'file': ('data.json', json_data, 'application/json')}
            response = requests.post(f"{self.base_url}/add", files=files, timeout=30)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Data tallennettu IPFS:ään CID:llä: {result['Hash']}")
                
                # Jos data on kysymyslista, päivitä well-known CID
                if isinstance(data, dict) and "questions" in data:
                    # Tässä vaiheessa voit päivittää IPNS-nimeä
                    # Tämä vaatii lisäkonfiguraatiota IPFS-solmuun
                    pass
                    
                return {
                    "Hash": result["Hash"],
                    "Size": result["Size"],
                    "Name": result["Name"]
                }
            else:
                raise Exception(f"IPFS add failed: {response.text}")
        except Exception as e:
            print(f"❌ Virhe IPFS:ään lisättäessä: {e}")
            return self._mock_add_json(data)

    def get_json(self, cid: str) -> Optional[Dict[str, Any]]:
        """Hakee JSON-datan IPFS:stä käyttäen HTTP API:a"""
        if not self.connected:
            return self._mock_get_json(cid)
        try:
            # Yritä ensin annetulla CID:llä
            response = requests.post(f"{self.base_url}/cat", params={'arg': cid}, timeout=30)
            if response.status_code == 200:
                return response.json()
            
            # Jos se ei toimi ja kyseessä on well-known CID, yritä vaihtoehtoisia CIDEjä
            if cid == self.well_known_cid:
                # Tässä voit toteuttaa IPNS-haun tai käyttää vakio CID:ä
                # Tämä on yksinkertaistettu versio
                pass
                
            return None
        except Exception as e:
            print(f"❌ Virhe IPFS:stä haettaessa: {e}")
            return self._mock_get_json(cid)

    def pin_add(self, cid: str) -> bool:
        """Pinnaa CID:n IPFS:ään"""
        if not self.connected:
            return True
        try:
            response = requests.post(f"{self.base_url}/pin/add", params={'arg': cid}, timeout=30)
            return response.status_code == 200
        except:
            return False

    def _mock_add_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock-toteutus IPFS:än lisäykselle"""
        import hashlib
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
        # Palauta tyhjä kysymyslista well-known CID:lle
        if cid == self.well_known_cid:
            return {
                "election_id": "test_election_2025",
                "timestamp": datetime.now().isoformat(),
                "questions": []
            }
        return None

# Yksinkertainen IPFS API wrapper
class IPFSAPI:
    @staticmethod
    def add(file_path):
        """Wrapper ipfshttpclientin add-metodille"""
        return [{'Hash': 'mock_hash', 'Size': 1024}]
    
    @staticmethod
    def get(cid, path):
        """Wrapper ipfshttpclientin get-metodille"""
        with open(path, 'w') as f:
            f.write('{"mock": "data"}')

# Alias vanhaa koodia varten
ipfs_api = IPFSAPI()
