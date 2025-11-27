#!/usr/bin/env python3
"""
Puolueiden vahvistus QuorumManagerille
"""
from typing import Dict, Any
from datetime import datetime


class PartyVerifier:
    """Puolueiden vahvistusprosessin hallinta"""
    
    def __init__(self, election_id: str = "default_election"):
        from ...quorum.voting.taq_calculator import TAQCalculator
        from ...quorum.time.timeout_manager import TimeoutManager
        from ...quorum.time.deadline_calculator import DeadlineCalculator
        
        self.taq_calculator = TAQCalculator(election_id)
        self.timeout_manager = TimeoutManager()
        self.deadline_calculator = DeadlineCalculator()
        self.election_id = election_id
    
    def initialize_party_verification(self, party_data: Dict) -> Dict:
        """Alusta puolueen vahvistusprosessi"""
        # Hae TAQ-bonus puolueelle
        taq_bonus = self.taq_calculator.get_taq_bonus_for_party(party_data)
        
        # Laske timeout TAQ-bonuksen perusteella
        timeout_str = self.timeout_manager.calculate_timeout_with_taq(taq_bonus)
        deadline = self.deadline_calculator.from_timeout_string(timeout_str)
        
        # Luo vahvistusprosessi
        verification_process = {
            "type": "party_verification",
            "election_id": self.election_id,
            "party_data": party_data,
            "taq_bonus": taq_bonus,
            "timeout": timeout_str,
            "deadline": deadline.isoformat(),
            "status": "active",
            "votes": {},
            "created_at": datetime.now().isoformat(),
            "total_nodes": 5,  # Oletusarvo, voitaisiin hakea configista
            "required_approvals": self._calculate_required_approvals(taq_bonus, 5)
        }
        
        return verification_process
    
    def _calculate_required_approvals(self, taq_bonus: Dict, total_nodes: int) -> int:
        """Laske tarvittavat hyväksynnät"""
        return self.taq_calculator.calculate_required_approvals_with_taq(
            taq_bonus, total_nodes
        )
    
    def add_party_media(self, verification_process: Dict, media_data: Dict) -> Dict:
        """Lisää media-tiedostoja puolueen vahvistukseen"""
        if "media_files" not in verification_process:
            verification_process["media_files"] = []
        
        verification_process["media_files"].append(media_data)
        return verification_process
    
    def get_party_verification_status(self, verification_process: Dict) -> Dict:
        """Hae puolueen vahvistuksen tila"""
        return {
            "status": verification_process.get("status", "unknown"),
            "votes_received": len(verification_process.get("votes", {})),
            "required_approvals": verification_process.get("required_approvals", 1),
            "time_remaining": self.timeout_manager.calculate_time_remaining(verification_process),
            "taq_bonus": verification_process.get("taq_bonus", {})
        }
