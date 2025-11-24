# src/managers/enhanced_integrity_manager.py
#!/usr/bin/env python3
"""
Config-päivitysten eheydenvalvonta
"""
import hashlib
import json
from typing import Dict

class EnhancedIntegrityManager:
    def __init__(self, election_id: str):
        self.election_id = election_id
    
    def verify_config_integrity(self, config_data: Dict, expected_hash: str = None) -> bool:
        """Tarkista config-tiedoston eheys"""
        
        # 1. Tarkista perusrakenne
        if not self._validate_config_structure(config_data):
            return False
        
        # 2. Tarkista hash (jos annettu)
        if expected_hash and self._calculate_config_hash(config_data) != expected_hash:
            return False
        
        # 3. Tarkista arvojen kelvollisuus
        if not self._validate_config_values(config_data):
            return False
        
        # 4. Tarkista riippuvuudet
        if not self._validate_config_dependencies(config_data):
            return False
        
        return True
    
    def _validate_config_structure(self, config: Dict) -> bool:
        """Tarkista configin perusrakenne"""
        required_sections = ["election", "system_info", "metadata"]
        return all(section in config for section in required_sections)
    
    def _validate_config_values(self, config: Dict) -> bool:
        """Tarkista config-arvojen kelvollisuus"""
        election = config.get("election", {})
        
        # Tarkista max_questions
        max_questions = election.get("max_questions", 0)
        if not (5 <= max_questions <= 100):
            return False
        
        # Tarkista max_candidates
        max_candidates = election.get("max_candidates", 0)
        if not (10 <= max_candidates <= 200):
            return False
        
        # Tarkista answer_scale
        answer_scale = election.get("answer_scale", {})
        if not (-5 <= answer_scale.get("min", 0) <= answer_scale.get("max", 0) <= 5):
            return False
        
        return True
    
    def _validate_config_dependencies(self, config: Dict) -> bool:
        """Tarkista config-riippuvuudet"""
        # Esim: max_questions <= max_answers_per_candidate
        election = config.get("election", {})
        security = config.get("security_measures", {})
        
        max_questions = election.get("max_questions", 0)
        max_answers = security.get("max_answers_per_candidate", 0)
        
        if max_answers > 0 and max_questions > max_answers:
            return False
        
        return True
    
    def _calculate_config_hash(self, config_data: Dict) -> str:
        """Laske config-tiedoston tiiviste"""
        config_string = json.dumps(config_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(config_string.encode()).hexdigest()
