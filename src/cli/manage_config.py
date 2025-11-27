#!/usr/bin/env python3
"""
MODULAARINEN CONFIG-HALLINTA - PÄIVITETTY UUDELLE RAKENTEELLE
"""
import sys
import os
import click
import json

# Lisää src hakemisto Python-polkuun
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..', '..')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

try:
    from src.core.config import ConfigManager
    from src.core.config.legacy_compatibility import get_election_id, get_data_path, validate_election_config
except ImportError as e:
    print(f"❌ Import-virhe: {e}")
    print("💡 Varmista että olet projektin juuressa")
    sys.exit(1)

@click.group()
def manage_config():
    """Config-hallinta uudella modulaarisella rakenteella"""
    pass

@manage_config.command()
@click.option('--election-id', help='Vaalitunniste')
def info(election_id):
    """Näytä config-tiedot"""
    target_election = get_election_id(election_id)
    manager = ConfigManager(target_election)
    
    config_info = manager.get_config_info()
    if not config_info:
        print("❌ Config-tietoja ei löytynyt")
        return
    
    print(f"📊 CONFIG-TIEDOT - {target_election}")
    print(f"🔐 Hash: {config_info['config_hash'][:16]}...")
    print(f"🕒 Viimeksi päivitetty: {config_info['last_updated']}")
    print(f"📈 Päivityksiä: {config_info['update_count']}")
    print(f"❓ Max kysymyksiä: {config_info['max_questions']}")
    print(f"👥 Max ehdokkaita: {config_info['max_candidates']}")

@manage_config.command()
@click.option('--election-id', help='Vaalitunniste')
def show(election_id):
    """Näytä koko config"""
    target_election = get_election_id(election_id)
    manager = ConfigManager(target_election)
    
    config = manager.get_election_config()
    if not config:
        print("❌ Config-tiedostoa ei löytynyt")
        return
    
    print(json.dumps(config, indent=2, ensure_ascii=False))

@manage_config.command()
@click.option('--election-id', help='Vaalitunniste')
def validate(election_id):
    """Validoi config"""
    target_election = get_election_id(election_id)
    manager = ConfigManager(target_election)
    
    config = manager.get_election_config()
    if not config:
        print("❌ Config-tiedostoa ei löytynyt")
        return
    
    is_valid = validate_election_config(config)
    if is_valid:
        print("✅ Config on validi")
    else:
        print("❌ Config ei ole validi")

if __name__ == '__main__':
    manage_config()
