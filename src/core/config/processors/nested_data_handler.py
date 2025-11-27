#!/usr/bin/env python3
"""
Nested-data struktuurien käsittely
"""
from typing import Dict, Any


class NestedDataHandler:
    """Nested-data struktuurien käsittelijä"""
    
    def get_nested_value(self, data: Dict, key: str) -> Any:
        """Hae arvo nested-rakenteesta piste-erotellulla avaimella"""
        keys = key.split('.')
        current = data
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        return current
    
    def set_nested_value(self, data: Dict, key: str, value: Any) -> None:
        """Aseta arvo nested-rakenteeseen piste-erotellulla avaimella"""
        keys = key.split('.')
        current = data
        
        # Navigoi viimeiseen tasoon asti
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # Aseta arvo
        current[keys[-1]] = value
    
    def delete_nested_value(self, data: Dict, key: str) -> bool:
        """Poista arvo nested-rakenteesta"""
        keys = key.split('.')
        current = data
        
        # Navigoi viimeiseen tasoon asti
        for k in keys[:-1]:
            if k not in current or not isinstance(current[k], dict):
                return False
            current = current[k]
        
        # Poista arvo
        if keys[-1] in current:
            del current[keys[-1]]
            return True
        return False
