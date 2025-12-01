"""
Install CLI package - modulaarinen versio.
"""
import sys
from pathlib import Path

# Yritä importata suhteellisesti
try:
    from .utils import (
        get_static_marker_cid,
        check_system_installed,
        load_elections_list,
        initialize_node,
        show_elections_hierarchy,
        validate_election_id,
        initialize_basic_data_files
    )
    from .commands import install_command
    
    __all__ = [
        'get_static_marker_cid',
        'check_system_installed',
        'load_elections_list',
        'initialize_node',
        'show_elections_hierarchy',
        'validate_election_id',
        'initialize_basic_data_files',
        'install_command'
    ]
    
except ImportError as e:
    print(f"Import error in install package: {e}")
    __all__ = []
