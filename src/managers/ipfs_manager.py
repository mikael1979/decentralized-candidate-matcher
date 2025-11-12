#!/usr/bin/env python3
"""
IPFS-integrointi hajautettuun data-tallennukseen
"""
import json
from typing import Dict, Optional
from src.core.ipfs_client import IPFSClient

class IPFSManager:
    def __init__(self, election_id: str):
        self.election_id = election_id
        self.ipfs_client = IPFSClient.get_client()
    
    def store_question(self, question_data: Dict) -> str:
        """Tallenna kysymys IPFS:ään"""
        cid = self.ipfs_client.add_data({
            "type": "question",
            "election_id": self.election_id,
            "data": question_data,
            "timestamp": self._get_timestamp()
        })
        return cid
    
    def store_candidate_answer(self, secure_answer: Dict) -> str:
        """Tallenna ehdokkaan allekirjoitettu vastaus IPFS:ään"""
        cid = self.ipfs_client.add_data({
            "type": "candidate_answer",
            "election_id": self.election_id,
            "data": secure_answer,
            "timestamp": self._get_timestamp()
        })
        return cid
    
    def store_party_registration(self, party_data: Dict) -> str:
        """Tallenna puolueen PKI-rekisteröinti IPFS:ään"""
        cid = self.ipfs_client.add_data({
            "type": "party_registration",
            "election_id": self.election_id,
            "data": party_data,
            "timestamp": self._get_timestamp()
        })
        return cid
    
    def retrieve_data(self, cid: str) -> Optional[Dict]:
        """Hae data IPFS:stä CID:llä"""
        try:
            return self.ipfs_client.get_data(cid)
        except Exception as e:
            print(f"IPFS-haku epäonnistui: {e}")
            return None
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()
