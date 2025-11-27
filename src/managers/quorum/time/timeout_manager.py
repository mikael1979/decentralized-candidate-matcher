#!/usr/bin/env python3
"""
Timeout- ja deadline-hallinta QuorumManagerille
"""
from datetime import datetime, timedelta
from typing import Dict


class TimeoutManager:
    """Aikarajojen ja deadlinejen hallinta"""
    
    def calculate_config_timeout(self, proposal_type: str) -> str:
        """Laske config-päivityksen timeout aika"""
        timeouts = {
            "minor": "24h",
            "major": "48h", 
            "critical": "72h"
        }
        return timeouts.get(proposal_type, "24h")
    
    def get_time_adjusted_threshold(self, base_threshold: float) -> float:
        """Laske aikaan perustuva kynnysarvo"""
        return base_threshold
    
    def calculate_time_remaining(self, verification_process: Dict) -> float:
        """Laske jäljellä oleva aika prosessille"""
        deadline_str = verification_process.get("deadline")
        if not deadline_str:
            return 0.0
        
        try:
            deadline = datetime.fromisoformat(deadline_str)
            now = datetime.now()
            time_remaining = (deadline - now).total_seconds()
            return max(0.0, time_remaining)
        except:
            return 0.0
    
    def calculate_timeout_with_taq(self, taq_bonus: Dict) -> str:
        """Laske timeout TAQ-bonuksen perusteella"""
        base_timeout = "24h"
        taq_multiplier = taq_bonus.get("time_multiplier", 1.0)
        
        if taq_multiplier > 1.5:
            return "12h"
        elif taq_multiplier > 1.2:
            return "18h"
        else:
            return base_timeout
