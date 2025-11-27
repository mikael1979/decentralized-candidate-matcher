#!/usr/bin/env python3
"""
Config-muutosten soveltaminen
"""
import copy
from typing import Dict, Any
from .nested_data_handler import NestedDataHandler


class ChangeApplier:
    """Konfiguraation muutosten soveltaja"""
    
    def __init__(self):
        self.nested_handler = NestedDataHandler()
    
    def apply_changes(self, config: Dict, changes: Dict) -> Dict:
        """Toteuta muutokset config-objektiin"""
        updated_config = copy.deepcopy(config)
        
        for key, new_value in changes.items():
            self.nested_handler.set_nested_value(updated_config, key, new_value)
            
        return updated_config
    
    def revert_changes(self, config: Dict, changes: Dict) -> Dict:
        """Kumoa muutokset config-objektiista"""
        # Toteutetaan myöhemmin tarvittaessa
        return copy.deepcopy(config)
