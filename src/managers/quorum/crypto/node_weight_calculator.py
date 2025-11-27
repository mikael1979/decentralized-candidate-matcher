#!/usr/bin/env python3
"""
Node-painojen laskenta QuorumManagerille
"""
import hashlib
from typing import Dict


class NodeWeightCalculator:
    """Node-painojen laskenta ja hallinta"""
    
    def calculate_node_weight(self, node_id: str, node_public_key: str) -> int:
        """Laske noden paino äänestyksessä"""
        if not node_public_key or not node_id:
            return 1
        
        node_data = f"{node_id}:{node_public_key}"
        node_hash = hashlib.md5(node_data.encode()).hexdigest()
        hash_int = int(node_hash[:8], 16)
        weight = (hash_int % 10) + 1
        
        return weight
    
    def calculate_total_voting_power(self, nodes: Dict) -> int:
        """Laske nodien yhteinen äänestysvoima"""
        total_power = 0
        for node_id, node_data in nodes.items():
            public_key = node_data.get('public_key', '')
            weight = self.calculate_node_weight(node_id, public_key)
            total_power += weight
        
        return total_power
    
    def get_weighted_vote_threshold(self, nodes: Dict, threshold_percent: float) -> int:
        """Laske painotettu äänestyskynnys"""
        total_power = self.calculate_total_voting_power(nodes)
        return int(total_power * threshold_percent)
