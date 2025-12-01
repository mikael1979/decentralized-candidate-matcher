# src/cli/install/utils/config_utils.py
"""
Config-apufunktiot
"""
import json
from pathlib import Path
from datetime import datetime


def create_backup_config(config_manager):
    """
    Luo varmuuskopio nykyisestä configista
    
    Args:
        config_manager: ConfigManager-instanssi
        
    Returns:
        Path: Varmuuskopion polku tai None
    """
    try:
        current_config = config_manager.load_config()
        if not current_config:
            return None
            
        backup_dir = Path("data/backups")
        backup_dir.mkdir(exist_ok=True, parents=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"config_backup_{timestamp}.json"
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(current_config, f, indent=2, ensure_ascii=False)
            
        return backup_path
        
    except Exception as e:
        print(f"⚠️  Varmuuskopion luonti epäonnistui: {e}")
        return None
