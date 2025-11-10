#!/usr/bin/env python3
"""
Todellinen IPFS-client HTTP API:lle - PÄIVITETTY
"""

import requests
import json
import time
from typing import Dict, Any, Optional

class RealIPFSClient:
    def __init__(self, host: str = "localhost", port: int = 5001, protocol: str = "http", timeout: int = 30):
        self.base_url = f"{protocol}://{host}:{port}/api/v0"
        self.timeout = timeout
        self.session = requests.Session()
        self.connected = False
        self._test_connection()
    
    def _test_connection(self):
        """Testaa IPFS-yhteys"""
        try:
            response = self.session.post(f"{self.base_url}/id", timeout=5)
            if response.status_code == 200:
                self.connected = True
                node_info = response.json()
                print(f"✅ IPFS-yhteys muodostettu: {node_info.get('ID', 'unknown')[:8]}...")
            else:
                print(f"⚠️  IPFS ei vastaa oikein: {response.status_code}")
        except Exception as e:
            print(f"❌ IPFS-yhteys epäonnistui: {e}")
            self.connected = False
    
    def upload(self, data: Dict[str, Any]) -> str:
        """Lataa data IPFS:ään JSON-muodossa"""
        if not self.connected:
            return self._mock_fallback_upload(data)
            
        try:
            json_data = json.dumps(data, ensure_ascii=False)
            files = {'file': ('data.json', json_data, 'application/json')}
            
            response = self.session.post(
                f"{self.base_url}/add",
                files=files,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                cid = result['Hash']
                print(f"✅ Upload onnistui - CID: {cid}")
                return cid
            else:
                raise Exception(f"IPFS API virhe: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Upload epäonnistui: {e}")
            return self._mock_fallback_upload(data)
    
    def download(self, cid: str) -> Optional[Dict[str, Any]]:
        """Lataa data IPFS:stä CID:llä"""
        if not self.connected:
            return None
            
        try:
            response = self.session.post(
                f"{self.base_url}/cat",
                params={'arg': cid},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return json.loads(response.text)
            else:
                return None
                
        except Exception:
            return None
    
    def pin(self, cid: str) -> bool:
        """Pin CID IPFS:ään"""
        if not self.connected:
            return False
            
        try:
            response = self.session.post(
                f"{self.base_url}/pin/add",
                params={'arg': cid},
                timeout=self.timeout
            )
            return response.status_code == 200
        except:
            return False
    
    def unpin(self, cid: str) -> bool:
        """Poista pin"""
        if not self.connected:
            return False
            
        try:
            response = self.session.post(
                f"{self.base_url}/pin/rm",
                params={'arg': cid},
                timeout=self.timeout
            )
            return response.status_code == 200
        except:
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Hae IPFS-noden tilastot"""
        if not self.connected:
            return {"connected": False}
            
        try:
            repo_stats = self.session.post(f"{self.base_url}/stats/repo", timeout=10).json()
            bw_stats = self.session.post(f"{self.base_url}/stats/bw", timeout=10).json()
            
            return {
                "connected": True,
                "repo_size": repo_stats.get('RepoSize', 0),
                "storage_max": repo_stats.get('StorageMax', 0),
                "bandwidth_in": bw_stats.get('TotalIn', 0),
                "bandwidth_out": bw_stats.get('TotalOut', 0),
                "peers": self._get_peer_count()
            }
        except:
            return {"connected": False}
    
    def _get_peer_count(self) -> int:
        """Hae peerien määrä"""
        try:
            response = self.session.post(f"{self.base_url}/swarm/peers", timeout=10)
            if response.status_code == 200:
                # Peerit ovat merkkijonolistassa
                peers_text = response.text.strip()
                return len([p for p in peers_text.split('\n') if p]) if peers_text else 0
        except:
            pass
        return 0
    
    def _mock_fallback_upload(self, data: Dict[str, Any]) -> str:
        """Mock-fallback kun IPFS ei saatavilla"""
        import hashlib
        content_string = json.dumps(data, sort_keys=True)
        content_hash = hashlib.sha256(content_string.encode()).hexdigest()
        cid = f"QmMock{content_hash[:40]}"
        print(f"🔄 Käytetään mock-CID:ä: {cid}")
        return cid
