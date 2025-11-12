# src/managers/quorum_manager.py
#!/usr/bin/env python3
"""
Hajautettu kvoorumi-pohjainen puoluevahvistusjärjestelmä
"""
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from .crypto_manager import CryptoManager

class QuorumManager:
    def __init__(self, election_id: str):
        self.election_id = election_id
        self.crypto = CryptoManager()
        
        # Kvoorumikonfiguraatio
        self.quorum_config = {
            "min_nodes_for_verification": 3,
            "approval_threshold_percent": 60,
            "verification_timeout_hours": 24,
            "rejection_quorum_percent": 40,
            "node_weight_calculation": "based_on_history"
        }
    
    def initialize_party_verification(self, party_data: Dict) -> Dict:
        """Alusta puolueen kvoorumivahvistus"""
        
        verification_process = {
            "party_id": party_data["party_id"],
            "party_name": party_data["name"]["fi"],
            "public_key_fingerprint": party_data["crypto_identity"]["key_fingerprint"],
            "verification_started": datetime.now().isoformat(),
            "verification_timeout": (datetime.now() + timedelta(hours=24)).isoformat(),
            "current_phase": "media_verification",
            "quorum_votes": [],
            "media_verifications": [],
            "final_decision": None,
            "decision_timestamp": None
        }
        
        return verification_process
    
    def cast_vote(self, verification_process: Dict, node_id: str, 
                 vote: str, node_public_key: str, justification: str = "") -> bool:
        """Äänestä puolueen vahvistamisesta"""
        
        if vote not in ["approve", "reject", "abstain"]:
            return False
        
        # Tarkista että node ei ole jo äänestänyt
        existing_vote = next((v for v in verification_process["quorum_votes"] 
                            if v["node_id"] == node_id), None)
        if existing_vote:
            return False
        
        # Tarkista aikaraja
        timeout = datetime.fromisoformat(verification_process["verification_timeout"])
        if datetime.now() > timeout:
            return False
        
        # Laske noden painoarvo
        node_weight = self._calculate_node_weight(node_id, node_public_key)
        
        # Luo äänirakenne
        vote_record = {
            "node_id": node_id,
            "vote": vote,
            "weight": node_weight,
            "justification": justification,
            "timestamp": datetime.now().isoformat(),
            "node_public_key_fingerprint": self.crypto.calculate_fingerprint(node_public_key),
            "vote_signature": self._sign_vote(node_id, vote, node_public_key)
        }
        
        verification_process["quorum_votes"].append(vote_record)
        
        # Tarkista onko päätös saavutettu
        return self._check_quorum_decision(verification_process)
    
    def add_media_verification(self, verification_process: Dict, 
                             publication_record: Dict, node_id: str) -> bool:
        """Lisää mediavahvistus kvoorumiprosessiin"""
        
        media_verification = {
            "publication_id": publication_record["publication_id"],
            "media_domain": publication_record["media_domain"],
            "trust_score": publication_record["trust_score"],
            "verified_by_node": node_id,
            "verification_timestamp": datetime.now().isoformat(),
            "evidence_url": publication_record.get("media_url", "")
        }
        
        verification_process["media_verifications"].append(media_verification)
        
        # Siirrä seuraavaan vaiheeseen jos mediavahvistukset saavutettu
        media_verifications = len(verification_process["media_verifications"])
        if (media_verifications >= 2 and 
            verification_process["current_phase"] == "media_verification"):
            verification_process["current_phase"] = "quorum_voting"
        
        return True
    
    def _check_quorum_decision(self, verification_process: Dict) -> bool:
        """Tarkista onko kvoorumipäätös saavutettu"""
        
        votes = verification_process["quorum_votes"]
        if not votes:
            return False
        
        total_weight = sum(vote["weight"] for vote in votes)
        approve_weight = sum(vote["weight"] for vote in votes if vote["vote"] == "approve")
        reject_weight = sum(vote["weight"] for vote in votes if vote["vote"] == "reject")
        
        approval_ratio = (approve_weight / total_weight) * 100 if total_weight > 0 else 0
        rejection_ratio = (reject_weight / total_weight) * 100 if total_weight > 0 else 0
        
        min_votes = self.quorum_config["min_nodes_for_verification"]
        approval_threshold = self.quorum_config["approval_threshold_percent"]
        rejection_threshold = self.quorum_config["rejection_quorum_percent"]
        
        # Tarkista ehdot
        has_min_votes = len(votes) >= min_votes
        has_approval_quorum = approval_ratio >= approval_threshold
        has_rejection_quorum = rejection_ratio >= rejection_threshold
        
        if has_min_votes and has_approval_quorum:
            verification_process["final_decision"] = "approved"
            verification_process["decision_timestamp"] = datetime.now().isoformat()
            return True
        
        elif has_min_votes and has_rejection_quorum:
            verification_process["final_decision"] = "rejected" 
            verification_process["decision_timestamp"] = datetime.now().isoformat()
            return True
        
        return False
    
    def _calculate_node_weight(self, node_id: str, node_public_key: str) -> int:
        """Laske noden painoarvo äänestyksessä"""
        # Yksinkertaistettu - oikeassa järjestelmässä perustuisi historiaan
        base_weight = 10
        
        # Lisää painoa jos node on vanha ja luotettu
        if node_id.startswith("node_zeus") or node_id.startswith("node_athena"):
            base_weight += 5
        
        return base_weight
    
    def _sign_vote(self, node_id: str, vote: str, node_public_key: str) -> str:
        """Allekirjoita ääni (yksinkertaistettu)"""
        vote_data = f"{node_id}:{vote}:{datetime.now().isoformat()}"
        return hashlib.sha256(vote_data.encode()).hexdigest()
    
    def get_verification_status(self, verification_process: Dict) -> Dict:
        """Hae vahvistusprosessin tila"""
        
        votes = verification_process["quorum_votes"]
        total_votes = len(votes)
        
        status = {
            "party_id": verification_process["party_id"],
            "current_phase": verification_process["current_phase"],
            "total_votes": total_votes,
            "approve_votes": len([v for v in votes if v["vote"] == "approve"]),
            "reject_votes": len([v for v in votes if v["vote"] == "reject"]),
            "abstain_votes": len([v for v in votes if v["vote"] == "abstain"]),
            "media_verifications": len(verification_process["media_verifications"]),
            "time_remaining_hours": self._calculate_time_remaining(verification_process),
            "final_decision": verification_process.get("final_decision"),
            "quorum_met": verification_process.get("final_decision") is not None
        }
        
        return status
    
    def _calculate_time_remaining(self, verification_process: Dict) -> float:
        """Laske jäljellä oleva aika tunneissa"""
        timeout = datetime.fromisoformat(verification_process["verification_timeout"])
        remaining = timeout - datetime.now()
        return max(0, remaining.total_seconds() / 3600)
