# src/cli/install/utils.py
"""
Apufunktiot asennukseen
"""
import sys
from pathlib import Path
import json
from datetime import datetime

# Lisää polku
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.file_utils import read_json_file


def get_static_marker_cid():
    """
    Hae staattisen merkin CID first_install.json tiedostosta
    
    Returns:
        str: Staattisen merkin CID
    """
    try:
        install_info_path = Path("data/installation/first_install.json")
        if install_info_path.exists():
            install_info = read_json_file(install_info_path)
            return install_info.get("static_marker_cid")
    except Exception as e:
        print(f"⚠️  First install info load failed: {e}")
    
    # Fallback vanhaan CID:ään
    return "QmVaaliKoneStaticMarker123456789"


def validate_election_id(election_id, elections_data):
    """
    Tarkista että election_id on olemassa vaalilistassa
    
    Args:
        election_id: Tarkistettava vaalin tunniste
        elections_data: Elections listan data
        
    Returns:
        bool: True jos vaali löytyy, muuten False
    """
    if not elections_data or not election_id:
        return False
        
    hierarchy = elections_data.get("hierarchy", {})
    
    # Tarkista mantereiden vaalit
    for continent_data in hierarchy.get("continents", {}).values():
        for country_data in continent_data.get("countries", {}).values():
            for e_id, election_data in country_data.get("elections", {}).items():
                if election_data.get("election_id") == election_id:
                    return True
    
    # Tarkista muut vaalit
    other_elections = hierarchy.get("other_elections", {})
    if isinstance(other_elections, dict):
        for category, election_data in other_elections.items():
            if isinstance(election_data, dict) and election_data.get("election_id") == election_id:
                return True
    
    return False


def get_election_info(election_id, elections_data):
    """
    Hae vaalin tiedot
    
    Args:
        election_id: Haettava vaalin tunniste
        elections_data: Elections listan data
        
    Returns:
        dict: Vaalin tiedot tai None jos ei löydy
    """
    if not elections_data or not election_id:
        return None
        
    hierarchy = elections_data.get("hierarchy", {})
    
    # Etsi mantereiden vaaleista
    for continent_data in hierarchy.get("continents", {}).values():
        for country_data in continent_data.get("countries", {}).values():
            for e_id, election_data in country_data.get("elections", {}).items():
                if election_data.get("election_id") == election_id:
                    return election_data
    
    # Etsi muista vaaleista
    other_elections = hierarchy.get("other_elections", {})
    if isinstance(other_elections, dict):
        for category, election_data in other_elections.items():
            if isinstance(election_data, dict) and election_data.get("election_id") == election_id:
                return election_data
    
    return None


def format_election_display(election_data):
    """
    Muotoile vaalin näyttäminen käyttäjälle
    
    Args:
        election_data: Vaalin tiedot
        
    Returns:
        str: Muotoiltu merkkijono
    """
    if not election_data:
        return "Unknown election"
    
    name = election_data.get("name", {}).get("fi", "Nimetön vaali")
    election_id = election_data.get("election_id", "unknown")
    status = election_data.get("status", "unknown")
    
    status_icons = {
        "active": "🟢",
        "upcoming": "🟡", 
        "completed": "🔴",
        "unknown": "⚪"
    }
    
    icon = status_icons.get(status, "⚪")
    return f"{icon} {name} ({election_id})"


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
