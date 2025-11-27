#!/usr/bin/env python3
"""
Äänien allekirjoitus QuorumManagerille
"""
import hashlib
from typing import Dict


class VoteSigner:
    """Äänien allekirjoitus ja validointi"""
    
    def __init__(self):
        self._crypto_manager = None
    
    def _get_crypto_manager(self):
        """Hae CryptoManager (lazy loading)"""
        if self._crypto_manager is None:
            try:
                from crypto_manager import CryptoManager
                self._crypto_manager = CryptoManager()
            except ImportError:
                self._crypto_manager = None
        return self._crypto_manager
    
    def sign_vote(self, node_id: str, vote: str, node_public_key: str) -> str:
        """Allekirjoita ääni"""
        crypto_mgr = self._get_crypto_manager()
        if crypto_mgr:
            vote_data = f"{node_id}:{vote}"
            return crypto_mgr.sign_data(vote_data, node_public_key)
        else:
            vote_data = f"{node_id}:{vote}:{node_public_key}"
            return hashlib.sha256(vote_data.encode()).hexdigest()
    
    def verify_vote_signature(self, vote_data: str, signature: str, public_key: str) -> bool:
        """Tarkista äänen allekirjoitus"""
        crypto_mgr = self._get_crypto_manager()
        if crypto_mgr:
            return crypto_mgr.verify_signature(vote_data, signature, public_key)
        else:
            expected_hash = hashlib.sha256(vote_data.encode()).hexdigest()
            return signature == expected_hash
