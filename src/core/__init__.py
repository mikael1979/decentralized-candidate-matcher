"""
Core-moduulit hajautetulle vaalikoneelle
"""
from .config import ConfigManager
from .config.legacy_compatibility import get_election_id, get_data_path, validate_election_config

__all__ = ['ConfigManager', 'get_election_id', 'get_data_path', 'validate_election_config']
