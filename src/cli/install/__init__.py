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
        get_election_info,
        format_election_display,
        initialize_basic_data_files
    )
    from .installer import SystemInstaller
    from .cli import install_system
    
    __all__ = [
        'get_static_marker_cid',
        'check_system_installed',
        'load_elections_list',
        'initialize_node',
        'show_elections_hierarchy',
        'validate_election_id',
        'get_election_info',
        'format_election_display',
        'initialize_basic_data_files',
        'SystemInstaller',
        'install_system'
    ]
    
except ImportError as e:
    print(f"Import error in install package: {e}")
    __all__ = []
