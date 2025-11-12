#!/usr/bin/env python3
"""
Yhteiset virheenkäsittelyfunktiot
"""
import sys
import json
import click
from pathlib import Path

class ElectionSystemError(Exception):
    """Perusvirheluokka vaalijärjestelmälle"""
    pass

class FileNotFoundError(ElectionSystemError):
    """Tiedostoa ei löydy"""
    pass

class DataValidationError(ElectionSystemError):
    """Data validointivirhe"""
    pass

class ElectionNotFoundError(ElectionSystemError):
    """Vaalia ei löydy"""
    pass

def handle_file_errors(func):
    """Decorator tiedostokäsittelyvirheille"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            click.echo(f"❌ Tiedostovirhe: {e}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            click.echo(f"❌ JSON-virhe tiedostossa: {e}")
            sys.exit(1)
        except PermissionError as e:
            click.echo(f"❌ Käyttöoikeusvirhe: {e}")
            sys.exit(1)
        except Exception as e:
            click.echo(f"❌ Odottamaton virhe: {e}")
            sys.exit(1)
    return wrapper

def validate_election_exists(election_id: str):
    """Varmista että vaali on olemassa"""
    meta_file = Path(f"data/runtime/meta.json")
    if not meta_file.exists():
        raise ElectionNotFoundError(f"Järjestelmää ei ole asennettu vaaliin: {election_id}")
    
    with open(meta_file, 'r', encoding='utf-8') as f:
        meta_data = json.load(f)
    
    if meta_data.get("metadata", {}).get("election_id") != election_id:
        raise ElectionNotFoundError(f"Vaalia ei löydy: {election_id}")

def safe_json_read(file_path: str) -> dict:
    """Turvallinen JSON-tiedoston lukeminen"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Tiedostoa ei löydy: {file_path}")
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise DataValidationError(f"Virheellinen JSON tiedostossa {file_path}: {e}")

def safe_json_write(file_path: str, data: dict):
    """Turvallinen JSON-tiedoston kirjoitus"""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        raise DataValidationError(f"Kirjoitusvirhe tiedostoon {file_path}: {e}")

def validate_answer_value(value: int) -> bool:
    """Varmista että vastaus on validi"""
    return -5 <= value <= 5

def validate_confidence_level(confidence: int) -> bool:
    """Varmista että luottamustaso on validi"""
    return 1 <= confidence <= 5
