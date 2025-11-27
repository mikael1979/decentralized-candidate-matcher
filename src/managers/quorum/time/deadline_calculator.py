#!/usr/bin/env python3
"""
Deadline-laskenta QuorumManagerille
"""
from datetime import datetime, timedelta
from typing import Dict


class DeadlineCalculator:
    """Deadlinejen laskenta ja hallinta"""
    
    def from_timeout_string(self, timeout_str: str) -> datetime:
        """Muunna timeout-string deadlineksi"""
        now = datetime.now()
        
        if timeout_str.endswith("h"):
            hours = int(timeout_str[:-1])
            return now + timedelta(hours=hours)
        elif timeout_str.endswith("d"):
            days = int(timeout_str[:-1])
            return now + timedelta(days=days)
        else:
            return now + timedelta(hours=24)
    
    def is_deadline_passed(self, deadline: datetime) -> bool:
        """Tarkista onko deadline mennyt"""
        return datetime.now() > deadline
    
    def get_time_until_deadline(self, deadline: datetime) -> timedelta:
        """Hae aika deadlineen"""
        return deadline - datetime.now()
