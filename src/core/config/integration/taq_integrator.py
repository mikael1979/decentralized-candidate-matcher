#!/usr/bin/env python3
"""
TAQ-integrointi config-päivityksiin
"""
from typing import Dict, Any, Optional


class TAQIntegrator:
    """TAQ-kvoorumin integrointi config-päivityksiin"""
    
    def __init__(self, election_id: str):
        self.election_id = election_id
        self._taq_config = None
    
    def _lazy_load_taq_config(self):
        """Lataa TAQConfigManager vain tarvittaessa"""
        if self._taq_config is None:
            try:
                from managers.taq_config_manager import TAQConfigManager
                self._taq_config = TAQConfigManager(self.election_id)
            except ImportError:
                self._taq_config = None
        return self._taq_config
    
    def propose_config_update(self, changes: Dict, update_type: str, 
                            justification: str, node_id: str) -> Optional[str]:
        """Ehdotta config-päivitystä TAQ-kvoorumille"""
        taq_config = self._lazy_load_taq_config()
        if not taq_config:
            return None
        
        return taq_config.propose_config_update(
            changes, update_type, justification, node_id
        )
    
    def is_available(self) -> bool:
        """Tarkista onko TAQ-integrointi saatavilla"""
        return self._lazy_load_taq_config() is not None
