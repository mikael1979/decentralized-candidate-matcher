# src/core/__init__.py
from .config_manager import (
    ConfigManager,
    get_election_id,
    get_data_path,
    validate_election_config
)

__all__ = ["ConfigManager", "get_election_id", "get_data_path", "validate_election_config"]
