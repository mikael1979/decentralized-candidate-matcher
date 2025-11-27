#!/usr/bin/env python3
"""
UUSI QUORUMMANAGER - MODULAARINEN PÄÄKOORDINAATTORI
Käyttää erikoistuneita moduuleja verifikaatio- ja äänestyslogiikkaan
"""
from typing import Dict, Any, Optional
from datetime import datetime

from .verification.party_verifier import PartyVerifier
from .verification.config_verifier import ConfigVerifier
from .verification.media_verifier import MediaVerifier
from .voting.quorum_decider import QuorumDecider
from .crypto.vote_signer import VoteSigner
from .crypto.node_weight_calculator import NodeWeightCalculator


class QuorumManager:
    """Modulaarinen QuorumManager - Pääkoordinaattori verifikaatioille"""
    
    def __init__(self, election_id: str):
        self.election_id = election_id
        
        # Alusta moduulit
        self.party_verifier = PartyVerifier(election_id)
        self.config_verifier = ConfigVerifier(election_id)
        self.media_verifier = MediaVerifier()
        self.quorum_decider = QuorumDecider()
        self.vote_signer = VoteSigner()
        self.node_weight_calculator = NodeWeightCalculator()
    
    def initialize_party_verification(self, party_data: Dict) -> Dict:
        """Alusta puolueen vahvistusprosessi"""
        return self.party_verifier.initialize_party_verification(party_data)
    
    def initialize_config_update_verification(self, config_proposal: Dict) -> Dict:
        """Alusta config-päivityksen vahvistusprosessi"""
        return self.config_verifier.initialize_config_update_verification(config_proposal)
    
    def add_media_verification(self, verification_process: Dict, media_data: Dict) -> Dict:
        """Lisää media-vahvistus vahvistusprosessiin"""
        return self.media_verifier.add_media_verification(verification_process, media_data)
    
    def cast_vote(self, verification_process: Dict, node_id: str, 
                  vote: str, node_public_key: str) -> Dict:
        """Äänestä vahvistusprosessia"""
        
        # Tarkista että prosessi on aktiivinen
        if verification_process.get("status") != "active":
            return {
                "status": "error",
                "error": "Vahvistusprosessi ei ole aktiivinen"
            }
        
        # Tarkista aikaraja
        deadline_str = verification_process.get("deadline")
        if deadline_str:
            deadline = datetime.fromisoformat(deadline_str)
            if datetime.now() > deadline:
                return {
                    "status": "error", 
                    "error": "Äänestysaika on päättynyt"
                }
        
        # Allekirjoita ääni
        signature = self.vote_signer.sign_vote(node_id, vote, node_public_key)
        
        # Tallenna ääni
        votes = verification_process.get("votes", {})
        votes[node_id] = {
            "vote": vote,
            "signature": signature,
            "public_key": node_public_key,
            "timestamp": datetime.now().isoformat()
        }
        
        verification_process["votes"] = votes
        
        # Tarkista onko konsensus saavutettu
        if self._check_quorum_decision(verification_process):
            verification_process["status"] = "approved"
        
        return {
            "status": "success",
            "message": "Ääni annettu onnistuneesti",
            "verification_process": verification_process
        }
    
    def get_verification_status(self, verification_process: Dict) -> Dict:
        """Hae vahvistusprosessin tila"""
        process_type = verification_process.get("type")
        
        if process_type == "party_verification":
            return self.party_verifier.get_party_verification_status(verification_process)
        elif process_type == "config_update":
            return self.config_verifier.get_config_verification_status(verification_process)
        else:
            return {
                "status": verification_process.get("status", "unknown"),
                "votes_received": len(verification_process.get("votes", {})),
                "required_approvals": verification_process.get("required_approvals", 1)
            }
    
    def _check_quorum_decision(self, verification_process: Dict) -> bool:
        """Tarkista onko konsensus saavutettu"""
        process_type = verification_process.get("type")
        
        if process_type == "config_update":
            return self.quorum_decider.check_config_quorum_decision(verification_process)
        else:
            # Käytä TAQ-pohjaista päätöstä muille prosesseille
            return self.quorum_decider.check_quorum_decision_with_taq(verification_process)
    
    def calculate_node_weight(self, node_id: str, node_public_key: str) -> int:
        """Laske noden paino äänestyksessä"""
        return self.node_weight_calculator.calculate_node_weight(node_id, node_public_key)
    
    def get_consensus_level(self, verification_process: Dict) -> float:
        """Hae nykyinen konsensustaso"""
        return self.quorum_decider.calculate_consensus_level(verification_process)
