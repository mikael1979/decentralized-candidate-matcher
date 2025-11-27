#!/usr/bin/env python3
"""
Konsensuspäätökset QuorumManagerille
"""
from typing import Dict, List


class QuorumDecider:
    """Konsensuspäätösten tekeminen"""
    
    def check_config_quorum_decision(self, verification_process: Dict) -> bool:
        """Tarkista onko config-päivitys saanut tarpeeksi tukea"""
        votes = verification_process.get('votes', {})
        required_approvals = verification_process.get('required_approvals', 1)
        
        yes_votes = sum(1 for vote_data in votes.values() 
                       if vote_data.get('vote') == 'yes')
        
        return yes_votes >= required_approvals
    
    def check_quorum_decision_with_taq(self, verification_process: Dict) -> bool:
        """Tarkista konsensus TAQ-bonuksen perusteella"""
        votes = verification_process.get('votes', {})
        taq_bonus = verification_process.get('taq_bonus', {})
        total_nodes = verification_process.get('total_nodes', 1)
        
        trust_score = taq_bonus.get('trust_score', 1.0)
        required_percentage = 0.6 / trust_score
        
        required_approvals = int(total_nodes * required_percentage)
        yes_votes = sum(1 for vote_data in votes.values() 
                       if vote_data.get('vote') == 'yes')
        
        return yes_votes >= max(1, required_approvals)
    
    def calculate_consensus_level(self, verification_process: Dict) -> float:
        """Laske nykyinen konsensustaso"""
        votes = verification_process.get('votes', {})
        total_nodes = verification_process.get('total_nodes', 1)
        
        if total_nodes == 0:
            return 0.0
        
        yes_votes = sum(1 for vote_data in votes.values() 
                       if vote_data.get('vote') == 'yes')
        
        return yes_votes / total_nodes
