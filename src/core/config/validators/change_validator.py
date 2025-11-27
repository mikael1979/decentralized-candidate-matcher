#!/usr/bin/env python3
"""
Config-muutosten validointi
"""
from typing import Dict, List, Any


class ChangeValidator:
    """Konfiguraation muutosten validointi"""
    
    def __init__(self):
        self._setup_validation_rules()
    
    def _setup_validation_rules(self):
        """Aseta validointisäännöt"""
        self.validation_rules = {
            "max_questions": lambda v: isinstance(v, int) and 5 <= v <= 100,
            "max_candidates": lambda v: isinstance(v, int) and 10 <= v <= 200,
            "security_measures.rate_limiting": lambda v: isinstance(v, bool),
            "ui.default_theme": lambda v: v in ["light", "dark", "blue"],
            "answer_scale.min": lambda v: isinstance(v, int) and -10 <= v <= 0,
            "answer_scale.max": lambda v: isinstance(v, int) and 0 <= v <= 10,
            "answer_scale.step": lambda v: isinstance(v, int) and 1 <= v <= 5,
            "network_config.min_nodes": lambda v: isinstance(v, int) and 1 <= v <= 100,
            "network_config.sync_interval": lambda v: isinstance(v, int) and v >= 60
        }
    
    def validate_changes(self, changes: Dict, current_config: Dict) -> bool:
        """Validoi config-muutokset"""
        return len(self.get_change_errors(changes, current_config)) == 0
    
    def get_change_errors(self, changes: Dict, current_config: Dict) -> List[str]:
        """Hae muutosvirheet"""
        errors = []
        
        for key, new_value in changes.items():
            # Tarkista että avain on olemassa
            current_value = self._get_nested_value(current_config, key)
            if current_value is None:
                errors.append(f"Tuntematon config-avain: {key}")
                continue
            
            # Tarkista arvojen kelvollisuus
            if not self._validate_config_value(key, new_value):
                errors.append(f"Virheellinen arvo avaimelle {key}: {new_value}")
        
        return errors
    
    def _validate_config_value(self, key: str, value: Any) -> bool:
        """Tarkista yksittäisen config-arvon kelvollisuus"""
        for rule_key, rule_func in self.validation_rules.items():
            if key == rule_key or key.startswith(rule_key + "."):
                return rule_func(value)
        
        # Oletus: hyväksy kaikki muut arvot
        return True
    
    def _get_nested_value(self, config: Dict, key: str) -> Any:
        """Hae arvo nested-rakenteesta"""
        keys = key.split('.')
        current = config
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        return current
