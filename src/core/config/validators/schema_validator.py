#!/usr/bin/env python3
"""
Config-skeeman validointi
"""
from typing import Dict, List, Any


class SchemaValidator:
    """Konfiguraation skeeman validointi"""
    
    def validate_config_schema(self, config: Dict) -> bool:
        """Validoi config-skeema"""
        required_sections = ["election", "system_info", "metadata"]
        if not all(section in config for section in required_sections):
            return False
        
        # Tarkista vaalitietojen rakenne
        election = config.get("election", {})
        if not all(key in election for key in ["id", "name", "max_questions", "max_candidates"]):
            return False
        
        return True
    
    def get_validation_errors(self, config: Dict) -> List[str]:
        """Hae validointivirheet"""
        errors = []
        
        required_sections = ["election", "system_info", "metadata"]
        for section in required_sections:
            if section not in config:
                errors.append(f"Puuttuva osio: {section}")
        
        # Tarkista vaalitietojen rakenne
        election = config.get("election", {})
        required_election_keys = ["id", "name", "max_questions", "max_candidates"]
        for key in required_election_keys:
            if key not in election:
                errors.append(f"Puuttuva vaalitieto: election.{key}")
        
        return errors
