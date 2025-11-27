#!/usr/bin/env python3
"""
Config-päivityshistorian hallinta
"""
from typing import Dict, List, Any
from datetime import datetime


class HistoryManager:
    """Konfiguraation päivityshistorian hallinta"""
    
    def add_update_entry(self, config: Dict, update_data: Dict) -> None:
        """Lisää päivitys historiatietoihin"""
        if "metadata" not in config:
            config["metadata"] = {}
        
        if "update_history" not in config["metadata"]:
            config["metadata"]["update_history"] = []
        
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "proposal_id": update_data.get("proposal_id", ""),
            "changes": update_data.get("changes", {}),
            "approved_by": update_data.get("approved_by", []),
            "justification": update_data.get("justification", "")
        }
        
        config["metadata"]["update_history"].append(history_entry)
    
    def get_update_history(self, config: Dict) -> List[Dict]:
        """Hae päivityshistoria"""
        return config.get("metadata", {}).get("update_history", [])
    
    def trim_history(self, config: Dict, max_entries: int = 50) -> None:
        """Rajaa historiatietoja maksimimäärään"""
        if "metadata" in config and "update_history" in config["metadata"]:
            history = config["metadata"]["update_history"]
            if len(history) > max_entries:
                config["metadata"]["update_history"] = history[-max_entries:]
