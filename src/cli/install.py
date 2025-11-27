#!/usr/bin/env python3
"""
Järjestelmän asennus - lataa IPFS:stä vaalilistan ja alusta node
"""
import click
import json
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import ConfigManager
from core.ipfs.client import IPFSClient
from core.file_utils import ensure_directory, read_json_file, write_json_file

# MULTINODE: Tuo uudet moduulit
try:
    from nodes.core.node_identity import NodeIdentity
    MULTINODE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Multinode modules not available: {e}")
    MULTINODE_AVAILABLE = False

def get_static_marker_cid():
    """
    Hae staattisen merkin CID first_install.json tiedostosta
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

def check_system_installed():
    """
    Tarkista onko järjestelmä asennettu IPFS:ään
    
    Returns:
        tuple: (is_installed, elections_cid)
    """
    try:
        ipfs_client = IPFSClient()
        
        # Hae oikea CID first_install.json:sta
        static_marker_cid = get_static_marker_cid()
        print(f"🔍 Checking static marker: {static_marker_cid}")
        
        # Yritä ladata staattista merkkitiedostoa
        marker_data = ipfs_client.get_json(static_marker_cid)
        if marker_data and marker_data.get("system") == "decentralized-candidate-matcher":
            print("✅ Hajautettu vaalikone löytyi IPFS:stä")
            
            # Hae elections lista first_install.json:sta
            try:
                install_info_path = Path("data/installation/first_install.json")
                if install_info_path.exists():
                    install_info = read_json_file(install_info_path)
                    elections_cid = install_info.get("elections_list_cid")
                    if elections_cid:
                        return True, elections_cid
            except Exception as e:
                print(f"⚠️  Elections CID load failed: {e}")
                    
    except Exception as e:
        print(f"⚠️  IPFS-tarkistus epäonnistui: {e}")
    
    return False, None

def load_elections_list(elections_cid):
    """
    Lataa elections lista IPFS:stä
    
    Args:
        elections_cid: Elections listan CID
        
    Returns:
        dict: Elections listan data
    """
    try:
        ipfs_client = IPFSClient()
        elections_data = ipfs_client.get_json(elections_cid)
        
        if elections_data:
            print("✅ Vaalilista ladattu IPFS:stä")
            return elections_data
        else:
            print("❌ Vaalilistan lataus epäonnistui")
            return None
            
    except Exception as e:
        print(f"⚠️  Vaalilistan lataus epäonnistui: {e}")
        return None

def initialize_node(election_id, node_type, node_name=None):
    """
    Alusta node
    
    Args:
        election_id: Vaalin tunniste
        node_type: Solmun tyyppi
        node_name: Solmun nimi (valinnainen)
        
    Returns:
        NodeIdentity tai None
    """
    if not MULTINODE_AVAILABLE:
        print("⚠️  Multinode not available, skipping node initialization")
        return None
    
    try:
        print("🌐 Alustetaan node...")
        
        # Tarkista onko node jo olemassa
        nodes_dir = Path(f"data/nodes/{election_id}")
        if nodes_dir.exists():
            identity_files = list(nodes_dir.glob("*_identity.json"))
            if identity_files:
                print("ℹ️  Node identity already exists, using existing")
                latest_file = max(identity_files, key=lambda f: f.stat().st_mtime)
                existing_identity = NodeIdentity(election_id, node_type)
                if existing_identity.load_identity(latest_file.stem.replace("_identity", "")):
                    print(f"✅ Loaded existing node: {existing_identity.node_id}")
                    return existing_identity
        
        # Luo uusi node-identiteetti
        if not node_name:
            node_name = f"{node_type}_{election_id}_{datetime.now().strftime('%H%M%S')}"
            
        identity = NodeIdentity(
            election_id=election_id,
            node_type=node_type,
            node_name=node_name,
            domain="election_network"
        )
        
        identity.save_identity()
        print(f"✅ Node identity created: {identity.node_id}")
        return identity
        
    except Exception as e:
        print(f"❌ Node initialization failed: {e}")
        return None

def show_elections_hierarchy(elections_data):
    """
    Näytä vaalihierarkia käyttäjälle
    
    Args:
        elections_data: Elections listan data
    """
    print("\n🌍 KÄYTÖSSÄ OLEVAT VAALIT:")
    print("=" * 50)
    
    hierarchy = elections_data.get("hierarchy", {})
    
    # Näytä mantereet
    for continent_id, continent_data in hierarchy.get("continents", {}).items():
        continent_name = continent_data["name"]["fi"]
        print(f"\n🏔️  {continent_name.upper()}")
        print("-" * 30)
        
        for country_id, country_data in continent_data.get("countries", {}).items():
            country_name = country_data["name"]["fi"]
            print(f"  🇺🇳 {country_name}")
            
            for election_id, election_data in country_data.get("elections", {}).items():
                election_name = election_data["name"]["fi"]
                status = election_data["status"]
                status_icon = "🟢" if status == "active" else "🟡" if status == "upcoming" else "🔴"
                print(f"    {status_icon} {election_name} ({election_data['election_id']})")
    
    # Näytä muut vaalit
    other_elections = hierarchy.get("other_elections", {})
    if other_elections:
        print(f"\n🎭 MUUT VAALIT:")
        print("-" * 30)
        
        for category, election_data in other_elections.items():
            if isinstance(election_data, dict) and "election_id" in election_data:
                election_name = election_data["name"]["fi"]
                status = election_data["status"]
                status_icon = "🟢" if status == "active" else "🟡" if status == "upcoming" else "🔴"
                print(f"  {status_icon} {election_name} ({election_data['election_id']})")

def validate_election_id(election_id, elections_data):
    """
    Tarkista että election_id on olemassa vaalilistassa
    """
    hierarchy = elections_data.get("hierarchy", {})
    
    # Tarkista mantereiden vaalit
    for continent_data in hierarchy.get("continents", {}).values():
        for country_data in continent_data.get("countries", {}).values():
            for e_id, election_data in country_data.get("elections", {}).items():
                if election_data["election_id"] == election_id:
                    return True
    
    # Tarkista muut vaalit
    for category, election_data in hierarchy.get("other_elections", {}).items():
        if isinstance(election_data, dict) and election_data.get("election_id") == election_id:
            return True
    
    return False

def initialize_basic_data_files(election_id):
    """
    Alustaa perus data-tiedostot vaalille
    """
    data_path = Path(f"data/runtime/{election_id}")
    ensure_directory(data_path)
    
    basic_files = {
        "meta.json": {
            "election_id": election_id,
            "created_at": datetime.now().isoformat(),
            "version": "2.0.0"
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

@click.command()
@click.option('--election-id', help='Valitse vaali (valinnainen)')
@click.option('--node-type', default='worker', help='Solmun tyyppi (coordinator/worker)')
@click.option('--node-name', help='Solmun nimi (valinnainen)')
@click.option('--list-elections', is_flag=True, help='Näytä saatavilla olevat vaalit')
@click.option('--enable-multinode', is_flag=True, help='Ota multinode käyttöön')
def install_system(election_id, node_type, node_name, list_elections, enable_multinode):
    """
    Asenna vaalikone - lataa IPFS:stä vaalilistan ja alusta node
    
    Esimerkkejä:
        # Näytä saatavilla olevat vaalit:
        python install.py --list-elections
        
        # Asenna tietty vaali:
        python install.py --election-id "olympian_gods_2024" --enable-multinode
        
        # Asenna työntekijänode:
        python install.py --election-id "finland_presidential_2024" --node-type worker
    """
    
    print("🔍 Tarkistetaan IPFS-asennusta...")
    
    # Tarkista onko järjestelmä asennettu
    is_installed, elections_cid = check_system_installed()
    
    if not is_installed:
        print("❌ Hajautettua vaalikonetta ei löydy IPFS:stä")
        print("💡 Suorita ensin: python src/cli/first_install.py")
        return
    
    if not elections_cid:
        print("❌ Vaalilistaa ei löydy")
        return
    
    # Lataa elections lista
    elections_data = load_elections_list(elections_cid)
    if not elections_data:
        print("❌ Vaalilistan lataus epäonnistui")
        return
    
    # Näytä vaalit jos pyydetty
    if list_elections:
        show_elections_hierarchy(elections_data)
        return
    
    # Jos vaalia ei ole annettu, näytä lista ja kysy
    if not election_id:
        show_elections_hierarchy(elections_data)
        election_id = click.prompt('\n📝 Valitse vaali (election_id)', type=str)
    
    # Tarkista että vaali on olemassa
    if not validate_election_id(election_id, elections_data):
        print(f"❌ Vaalia '{election_id}' ei löydy")
        return
    
    # Alusta config manager
    config_manager = ConfigManager()
    
    # Tarkista onko config jo olemassa
    current_config = config_manager.load_config()
    if current_config and current_config["metadata"]["election_id"] != election_id:
        click.confirm(
            f"Haluatko vaihtaa vaalia '{current_config['metadata']['election_id']}' -> '{election_id}'?",
            abort=True
        )
    
    # Generoi config
    print(f"📋 Alustetaan config vaalille: {election_id}")
    config = config_manager.generate_config(
        election_id=election_id,
        node_type=node_type,
        version="2.0.0"
    )
    
    config_path = config_manager.save_config(config)
    print(f"✅ Config tallennettu: {config_path}")
    
    # Alusta node
    node_identity = None
    if enable_multinode:
        node_identity = initialize_node(election_id, node_type, node_name)
    
    # Luo data-hakemistot
    data_path = config_manager.get_data_path(election_id)
    ensure_directory(data_path)
    print(f"✅ Data-hakemistot luotu: {data_path}")
    
    # Alusta perus data-tiedostot
    initialize_basic_data_files(election_id)
    
    print(f"\n🎉 ASENNUS VALMIS!")
    print(f"📊 Vaali: {election_id}")
    print(f"🔧 Solmu: {node_type}")
    if node_identity:
        print(f"🌐 Node ID: {node_identity.node_id}")
    print(f"📁 Config: {config_path}")
    print(f"💾 Data: {data_path}")

if __name__ == "__main__":
    install_system()
