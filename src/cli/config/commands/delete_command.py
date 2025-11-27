"""
delete_command.py - delete komento config-hallinnalle
"""
from src.core.config import ConfigManager
try:
    from managers.taq_config_manager import TAQConfigManager
except ImportError:
    pass

from src.core.file_utils import read_json_file, write_json_file

def delete_config_value(*args, **kwargs):
    """delete komento - TO BE IMPLEMENTED"""
    print("delete_command - NOT YET IMPLEMENTED")
    return {"status": "not_implemented", "command": "delete"}
