#!/usr/bin/env python3
"""
Yhteiset tiedostonkäsittelyfunktiot - KORJATTU VERSIO
"""
import json
import os
from pathlib import Path
from typing import Dict, Any
from .error_handling import ElectionSystemError

def read_json_file(file_path: str, default: Any = None) -> Any:
    """
    Turvallinen JSON-tiedoston lukeminen UTF-8 encodingilla
    
    Args:
        file_path: Polku JSON-tiedostoon
        default: Oletusarvo jos tiedostoa ei löydy
        
    Returns:
        JSON-data tai default-arvo
    """
    path = Path(file_path)
    
    # Jos tiedostoa ei ole, palauta default
    if not path.exists():
        if default is not None:
            return default
        raise ElectionSystemError(f"Tiedostoa ei löydy: {file_path}")
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ElectionSystemError(f"Virheellinen JSON tiedostossa {file_path}: {e}")
    except Exception as e:
        raise ElectionSystemError(f"Tiedoston lukuvirhe {file_path}: {e}")

def write_json_file(file_path: str, data: Any, ensure_ascii: bool = False):
    """
    Turvallinen JSON-tiedoston kirjoitus UTF-8 encodingilla
    
    Args:
        file_path: Polku JSON-tiedostoon
        data: Kirjoitettava data
        ensure_ascii: Pakota ASCII-merkistö
    """
    path = Path(file_path)
    
    # KORJATTU: Varmistetaan että hakemisto on olemassa
    path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=ensure_ascii)
    except Exception as e:
        raise ElectionSystemError(f"Tiedoston kirjoitusvirhe {file_path}: {e}")

def calculate_file_hash(file_path: str) -> str:
    """
    Laske tiedoston SHA-256 tiiviste
    
    Args:
        file_path: Polku tiedostoon
        
    Returns:
        SHA-256 tiiviste hex-muodossa
    """
    import hashlib
    
    path = Path(file_path)
    if not path.exists():
        raise ElectionSystemError(f"Tiedostoa ei löydy: {file_path}")
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return hashlib.sha256(content.encode()).hexdigest()
    except Exception as e:
        raise ElectionSystemError(f"Tiivisteen laskenta epäonnistui {file_path}: {e}")

def file_exists(file_path: str) -> bool:
    """
    Tarkista onko tiedosto olemassa
    
    Args:
        file_path: Polku tiedostoon
        
    Returns:
        True jos tiedosto on olemassa
    """
    return Path(file_path).exists()

def ensure_directory(directory_path: str):
    """
    Varmista että hakemisto on olemassa
    
    Args:
        directory_path: Polku hakemistoon
    """
    Path(directory_path).mkdir(parents=True, exist_ok=True)

def get_data_file_path(filename: str, election_id: str = "Jumaltenvaalit2026") -> str:
    """
    Hae standardoitu data-tiedoston polku
    
    Args:
        filename: Tiedostonimi
        election_id: Vaalin tunniste
        
    Returns:
        Täysi polku tiedostoon
    """
    return f"data/runtime/{filename}"

# Aliasit yhteensopivuuden vuoksi
safe_json_read = read_json_file
safe_json_write = write_json_file
