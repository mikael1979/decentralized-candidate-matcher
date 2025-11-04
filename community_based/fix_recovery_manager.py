# fix_recovery_manager.py
#!/usr/bin/env python3
"""
Quick fix for EnhancedRecoveryManager to handle ReservationType properly
"""

import sys
from pathlib import Path

def fix_recovery_manager():
    recovery_file = Path("enhanced_recovery_manager.py")
    
    if not recovery_file.exists():
        print("❌ enhanced_recovery_manager.py not found")
        return False
    
    with open(recovery_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Import ReservationType if not already imported
    if "from ipfs_schedule_manager import IPFSScheduleManager" in content and "ReservationType" not in content:
        content = content.replace(
            "from ipfs_schedule_manager import IPFSScheduleManager",
            "from ipfs_schedule_manager import IPFSScheduleManager, ReservationType"
        )
    
    # Fix 2: Replace string with enum in perform_intelligent_backup
    if 'reservation_result = self.schedule_manager.request_reservation("data_backup"' in content:
        content = content.replace(
            'reservation_result = self.schedule_manager.request_reservation("data_backup"',
            'reservation_result = self.schedule_manager.request_reservation(ReservationType.DATA_BACKUP'
        )
    
    # Fix 3: Also check for other string usages
    content = content.replace('"data_backup"', 'ReservationType.DATA_BACKUP')
    
    # Create backup
    backup_file = Path("enhanced_recovery_manager.py.backup")
    recovery_file.rename(backup_file)
    
    # Write fixed content
    with open(recovery_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ EnhancedRecoveryManager fixed!")
    print(f"📦 Backup saved as: {backup_file}")
    return True

if __name__ == "__main__":
    fix_recovery_manager()
