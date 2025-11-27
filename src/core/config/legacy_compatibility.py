#!/usr/bin/env python3
"""
Legacy compatibility - vanhojen funktioiden siirto uuteen rakenteeseen
"""
from pathlib import Path
from typing import Dict, Optional
from .config_manager import ConfigManager


def get_election_id(election_param: str = None) -> str:
    """Hae vaalitunniste parametrista tai configista"""
    if election_param:
        return election_param
    
    # Yritä lukea nykyinen vaali configista
    try:
        manager = ConfigManager()
        config = manager.get_election_config()
        if config:
            return config.get("election", {}).get("id", "Jumaltenvaalit2026")
    except:
        pass
    
    return "Jumaltenvaalit2026"


def get_data_path(election_id: str = None) -> Path:
    """Hae data-polku vaalille"""
    target_election = election_id or get_election_id()
    return Path(f"data/elections/{target_election}")


def validate_election_config(config_data: Dict) -> bool:
    """Validoi vaalikonfiguraatio (ulkopuolinen käyttö)"""
    # Yksinkertainen validointi - voidaan parantaa myöhemmin
    required_sections = ["election", "system_info", "metadata"]
    return all(section in config_data for section in required_sections)
