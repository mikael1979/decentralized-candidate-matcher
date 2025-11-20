#!/usr/bin/env python3
"""
Järjestelmän asennus ja konfiguraatio
"""
import click
import json
from datetime import datetime
import os
import sys
from pathlib import Path

# LISÄTTY: Lisää src hakemisto Python-polkuun
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config_manager import ConfigManager
from core.ipfs.client import IPFSClient
from core.file_utils import ensure_directory, read_json_file


def initialize_system_chain(election_id, config_hash, config_cid, template_hash):
    """
    Alustaa system_chain.json config hashilla
    
    Args:
        election_id: Vaalin tunniste
        config_hash: Config-tiedoston hash
        config_cid: IPFS CID configille
        template_hash: Template hash
    """
    chain_data = {
        "chain_id": f"system_chain_{election_id}",
        "blocks": [
            {
                "block_number": 0,
                "block_type": "genesis",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "action": "config_deployed",
                    "config_hash": config_hash,
                    "config_cid": config_cid,
                    "template_hash": template_hash,
                    "election_id": election_id
                },
                "previous_hash": "0",
                "hash": f"genesis_block_{election_id}"
            }
        ]
    }
    
    # Tallenna system_chain
    chain_path = Path("data/runtime/system_chain.json")
    ensure_directory(chain_path.parent)
    
    with open(chain_path, 'w', encoding='utf-8') as f:
        json.dump(chain_data, f, indent=2, ensure_ascii=False)
    
    return chain_path


def publish_config_to_ipfs(config_path):
    """
    Julkaise config IPFS:ään
    
    Args:
        config_path: Config-tiedoston polku
        
    Returns:
        IPFS CID tai None jos epäonnistuu
    """
    try:
        ipfs_client = IPFSClient()
        # Lataa config data ja julkaise JSON:na
        config_data = read_json_file(config_path)
        cid = ipfs_client.add_json(config_data)
        print(f"📤 Config julkaistu IPFS:ään: {cid}")
        return cid
    except Exception as e:
        print(f"⚠️  IPFS ei saatavilla - configia ei julkaistu: {e}")
        return None


@click.command()
@click.option('--election-id', required=False, help='Vaalin tunniste')
@click.option('--first-install', is_flag=True, help='Ensimmäinen asennus')
@click.option('--node-type', default='coordinator', help='Solmun tyyppi (coordinator/worker)')
@click.option('--version', default='1.0.0', help='Järjestelmän versio')
def install_system(election_id, first_install, node_type, version):
    """
    Asenna vaalikonejärjestelmä ja alusta config
    """
    
    # Alusta config manager
    config_manager = ConfigManager()
    
    if first_install:
        if not election_id:
            election_id = click.prompt('📝 Anna vaalin tunniste', type=str)
        
        print(f"🚀 Aloitetaan ensimmäinen asennus: {election_id}")
        
        try:
            # 1. Generoi config template-pohjaisesti
            print("📋 Generoidaan config tiedosto...")
            config = config_manager.generate_config(
                election_id=election_id,
                node_type=node_type,
                version=version
            )
            
            # 2. Tallenna config
            config_path = config_manager.save_config(config)
            print(f"✅ Config tallennettu: {config_path}")
            
            # 3. Julkaise IPFS:ään
            print("🌐 Julkaistaan config IPFS:ään...")
            config_cid = publish_config_to_ipfs(config_path)
            
            # 4. Alusta system_chain config hashilla
            config_hash = config["metadata"]["config_hash"]
            template_hash = config["metadata"]["template_hash"]
            
            chain_path = initialize_system_chain(
                election_id=election_id,
                config_hash=config_hash,
                config_cid=config_cid,
                template_hash=template_hash
            )
            print(f"✅ System chain alustettu: {chain_path}")
            
            # 5. Luo data-hakemistot
            data_path = config_manager.get_data_path(election_id)
            ensure_directory(data_path)
            print(f"✅ Data-hakemistot luotu: {data_path}")
            
            # 6. Luo perus data-tiedostot
            initialize_basic_data_files(election_id)
            
            print(f"\n🎉 JÄRJESTELMÄ ASENNETTU ONNISTUNEESTI!")
            print(f"📊 Vaali: {election_id}")
            print(f"🔧 Solmu: {node_type}")
            print(f"📁 Config: {config_path}")
            if config_cid:
                print(f"🌐 IPFS CID: {config_cid}")
            print(f"🔐 Config Hash: {config_hash}")
            
            # Tarkista configin eheys
            is_valid, message = config_manager.validate_config_integrity()
            print(f"🔍 Config integrity: {message}")
            
        except Exception as e:
            print(f"❌ Asennus epäonnistui: {e}")
            sys.exit(1)
            
    else:
        # Normaali asennus (ilman first-install)
        current_config = config_manager.load_config()
        
        if current_config:
            current_election = current_config["metadata"]["election_id"]
            print(f"📊 Nykyinen config: {current_election}")
            
            if election_id and election_id != current_election:
                click.confirm(
                    f"Haluatko vaihtaa vaalia '{current_election}' -> '{election_id}'?", 
                    abort=True
                )
                # Päivitä config uudella vaali-ID:llä
                new_config = config_manager.generate_config(
                    election_id=election_id,
                    node_type=node_type,
                    version=version
                )
                config_manager.save_config(new_config)
                print(f"✅ Vaali vaihdettu: {election_id}")
            else:
                print("ℹ️  Käytössä on nykyinen config")
        else:
            print("❌ Config tiedostoa ei löydy. Käytä --first-install")
            sys.exit(1)


def initialize_basic_data_files(election_id):
    """
    Alustaa perus data-tiedostot vaalille
    """
    data_path = Path(f"data/runtime/{election_id}")
    ensure_directory(data_path)
    
    # Perus data-tiedostot
    basic_files = {
        "meta.json": {
            "election_id": election_id,
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0"
        },
        "questions.json": {"questions": []},
        "candidates.json": {"candidates": []},
        "parties.json": {"parties": []},
        "candidate_answers.json": {"answers": []}
    }
    
    for filename, content in basic_files.items():
        file_path = data_path / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        print(f"  ✅ {filename} alustettu")


if __name__ == "__main__":
    install_system()
