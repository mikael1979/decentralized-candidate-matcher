#!/usr/bin/env python3
"""
TAQ-bonusten laskenta QuorumManagerille
"""
from typing import Dict, Any
from datetime import datetime


class TAQCalculator:
    """TAQ (Trust And Quality) bonusten laskenta"""
    
    def __init__(self, election_id: str = "default_election"):
        self.election_id = election_id
        self._taq_media_bonus = None
    
    def _get_taq_media_bonus(self):
        """Hae TAQMediaBonus (lazy loading)"""
        if self._taq_media_bonus is None:
            try:
                from core.taq_media_bonus import TAQMediaBonus
                self._taq_media_bonus = TAQMediaBonus(self.election_id)
            except ImportError:
                self._taq_media_bonus = None
        return self._taq_media_bonus
    
    def calculate_config_taq_parameters(self, config_proposal: Dict) -> Dict:
        """Laske config-päivityksen TAQ-parametrit"""
        proposal_type = config_proposal.get('update_type', 'minor')
        
        base_params = {
            'minor': {'base_threshold': 0.6, 'time_multiplier': 1.0},
            'major': {'base_threshold': 0.7, 'time_multiplier': 1.2},
            'critical': {'base_threshold': 0.8, 'time_multiplier': 1.5}
        }
        
        params = base_params.get(proposal_type, base_params['minor']).copy()
        taq_bonus = self._get_taq_bonus_for_config(config_proposal)
        if taq_bonus:
            params.update(taq_bonus)
        
        return params
    
    def get_taq_bonus_for_party(self, party_data: Dict) -> Dict:
        """Hae TAQ-bonus puolueelle"""
        taq_bonus = self._get_taq_media_bonus()
        if taq_bonus:
            try:
                return taq_bonus.calculate_party_bonus(party_data)
            except:
                pass
        
        # Fallback: perusbonus
        return {
            'trust_score': 1.0,
            'time_multiplier': 1.0,
            'approval_boost': 0.0
        }
    
    def _get_taq_bonus_for_config(self, config_proposal: Dict) -> Dict:
        """Hae TAQ-bonus config-päivitykselle"""
        # Yksinkertaistettu toteutus
        return {
            'trust_score': 1.0,
            'time_multiplier': 1.0,
            'approval_boost': 0.0
        }
    
    def calculate_required_approvals_with_taq(self, taq_bonus: Dict, total_nodes: int) -> int:
        """Laske tarvittavat hyväksynnät TAQ-bonuksen perusteella"""
        base_approvals = int(total_nodes * 0.6)  # 60% perusvaatimus
        approval_boost = taq_bonus.get('approval_boost', 0.0)
        
        # Vähennä vaatimusta jos korkea trust_score
        trust_score = taq_bonus.get('trust_score', 1.0)
        if trust_score > 1.5:
            base_approvals = int(base_approvals * 0.8)  # 20% alennus
        elif trust_score > 1.2:
            base_approvals = int(base_approvals * 0.9)  # 10% alennus
        
        # Lisää boostia
        boosted_approvals = base_approvals - int(base_approvals * approval_boost)
        
        return max(1, boosted_approvals)  # Vähintään 1
