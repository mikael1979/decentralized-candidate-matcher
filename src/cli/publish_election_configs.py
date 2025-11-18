#!/usr/bin/env python3
"""
Julkaise vaalikonfiguraatiot IPFS:ään
"""
import json
import click
from pathlib import Path
from typing import Dict
import sys
import os

# Lisää projektin juuri Python-polkuun OIKEIN
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent  # src/cli/ -> src/ -> project root
sys.path.insert(0, str(project_root))

try:
    from core.ipfs_client import IPFSClient
    print("✅ IPFS-client ladattu onnistuneesti")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print(f"💡 Current directory: {os.getcwd()}")
    print(f"💡 Project root: {project_root}")
    print(f"💡 Python path: {sys.path}")
    sys.exit(1)

@click.group()
def config_publisher():
    """Vaalikonfiguraatioiden julkaisutyökalu IPFS:ään"""
    pass

@config_publisher.command()
def publish_all():
    """Julkaise kaikki konfiguraatiot IPFS:ään"""
    print("🚀 Aloitetaan konfiguraatioiden julkaisu IPFS:ään...")
    client = IPFSClient.get_client("config_publisher")
    
    config_files = {
        "worker_config": "config/worker_config.json",
        "election_registry": "config/election_registry.json", 
        "jumaltenvaalit2026": "config/election_jumaltenvaalit2026.json"
    }
    
    published_cids = {}
    
    for config_name, config_path in config_files.items():
        config_file = Path(config_path)
        if config_file.exists():
            try:
                print(f"📖 Luetaan {config_name}...")
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                print(f"📤 Julkaistaan {config_name} IPFS:ään...")
                # Julkaise IPFS:ään
                cid = client.publish_election_data(f"config_{config_name}", config_data)
                published_cids[config_name] = cid
                print(f"✅ {config_name} julkaistu: {cid}")
                
            except Exception as e:
                print(f"❌ {config_name} julkaisu epäonnistui: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"⚠️ Tiedostoa ei löydy: {config_path}")
    
    # Tallenna CID:t tiedostoon
    if published_cids:
        cid_file = Path("config/published_cids.json")
        cid_file.parent.mkdir(exist_ok=True)
        
        with open(cid_file, 'w', encoding='utf-8') as f:
            json.dump(published_cids, f, indent=2, ensure_ascii=False)
        
        print(f"📄 CID:t tallennettu: {cid_file}")
        
        # Näytä käyttöohjeet
        print("\n🎯 KÄYTTÖOHJEET:")
        registry_cid = published_cids.get('election_registry', 'REPLACE_WITH_ACTUAL_CID')
        print(f"1. Worker node voi nyt ladata konfiguraatiot:")
        print(f"   python src/nodes/worker/election_installer.py --list --registry {registry_cid}")
        print("   python src/nodes/worker/election_installer.py --install jumaltenvaalit2026")
    else:
        print("❌ Yhtään konfiguraatiota ei julkaistu")

@config_publisher.command()
def status():
    """Näytä julkaistujen konfiguraatioiden tila"""
    cid_file = Path("config/published_cids.json")
    if cid_file.exists():
        with open(cid_file, 'r', encoding='utf-8') as f:
            cids = json.load(f)
        
        print("📋 Julkaistut konfiguraatiot:")
        for name, cid in cids.items():
            print(f"  🔗 {name}: {cid}")
            print(f"     🌐 https://ipfs.io/ipfs/{cid}")
    else:
        print("❌ Ei julkaistuja konfiguraatioita")
        print("💡 Julkaise ensin: python src/cli/publish_election_configs.py publish_all")

if __name__ == '__main__':
    config_publisher()
