# services/time_lock_collector.py - KORJAA RIVI 2:

# VANHA:  
# from services.ui.console_ui import input_time_lock

# UUSI:
from services.console_ui import input_time_lock

def collect_time_lock_info() -> dict:
    edit_deadline, grace_hours = input_time_lock()
    
    time_lock = {
        "timelock_enabled": edit_deadline is not None
    }
    
    if edit_deadline:
        time_lock.update({
            "edit_deadline": edit_deadline,
            "grace_period_hours": grace_hours
        })
    
    return time_lock
