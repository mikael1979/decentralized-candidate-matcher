#!/usr/bin/env python3
"""
Standard IPFS Client - Yhdenmukainen IPFS-asiakas kaikille moduuleille
"""

import json
from typing import Dict, Any, Optional

class StandardIPFSClient:
    """Yhdenmukainen IPFS-asiakas"""
    
    def __init__(self, mode: str = "mock"):
        self.mode = mode
        self.client = self._initialize_client()
        print(f"✅ Standard IPFS Client alustettu ({mode} mode)")
    
    def _initialize_client(self):
        """Alusta IPFS-asiakas tilan mukaan"""
        if self.mode == "mock":
            try:
                from mock_ipfs import MockIPFS
                return MockIPFS()
            except ImportError:
                print("⚠️  MockIPFS ei saatavilla - käytetään fallbackia")
                return self._create_fallback_client()
        else:
            # Tulevaisuudessa: todellinen IPFS-client
            return self._create_fallback_client()
    
    def _create_fallback_client(self):
        """Luo fallback-client kun IPFS ei saatavilla"""
        class FallbackIPFS:
            def __init__(self):
                self.content_store = {}
            
            def upload(self, data):
                import hashlib
                content_string = json.dumps(data, sort_keys=True)
                content_hash = hashlib.sha256(content_string.encode()).hexdigest()
                cid = f"QmFallback{content_hash[:40]}"
                self.content_store[cid] = data
                return cid
            
            def download(self, cid):
                return self.content_store.get(cid)
            
            def get_stats(self):
                return {
                    "total_cids": len(self.content_store),
                    "total_size_bytes": 0,
                    "mode": "fallback"
                }
        
        return FallbackIPFS()
    
    def upload(self, data: Dict[str, Any]) -> str:
        """Lataa data IPFS:ään"""
        return self.client.upload(data)
    
    def download(self, cid: str) -> Optional[Dict[str, Any]]:
        """Lataa data IPFS:stä"""
        return self.client.download(cid)
    
    def get_status(self) -> Dict[str, Any]:
        """Hae IPFS-statuksen"""
        return self.client.get_stats()

# Singleton instance
_ipfs_client = None

def get_ipfs_client(mode: str = "mock") -> StandardIPFSClient:
    """Hae StandardIPFSClient-instanssi"""
    global _ipfs_client
    if _ipfs_client is None:
        _ipfs_client = StandardIPFSClient(mode)
    return _ipfs_client
