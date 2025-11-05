#!/usr/bin/env python3
"""
JSON Utilities - Yhteinen JSON-käsittely kaikille moduuleille
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

def load_json(file_path: str) -> Optional[Dict[str, Any]]:
    """Lataa JSON-tiedosto turvallisesti"""
    path = Path(file_path)
    if not path.exists():
        return None
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Virhe ladattaessa JSON-tiedostoa {file_path}: {e}")
        return None

def save_json(file_path: str, data: Dict[str, Any]) -> bool:
    """Tallenna JSON-tiedosto turvallisesti"""
    path = Path(file_path)
    
    try:
        path.parent.mkdir(exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Virhe tallennettaessa JSON-tiedostoa {file_path}: {e}")
        return False

def validate_json_schema(data: Dict[str, Any], required_fields: list) -> bool:
    """Tarkista että datassa on tarvittavat kentät"""
    if not data:
        return False
    
    for field in required_fields:
        if field not in data:
            print(f"❌ Puuttuva kenttä: {field}")
            return False
    
    return True
