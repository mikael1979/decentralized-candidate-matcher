#!/usr/bin/env python3
"""
Järjestelmän asennus ja konfiguraatio - MULTINODE VERSION
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

# MULTINODE: Tuo uudet moduulit
try:
    from nodes.core.node_identity import NodeIdentity
    from nodes.core.network_manager import NetworkManager
    from nodes.discovery.peer_discovery import PeerDiscovery
    MULTINODE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Multinode modules not available: {e}")
    MULTINODE_AVAILABLE = False


def initialize_multinode_system(election_id, node_type, config_manager, bootstrap_debug=False):
    """
    Alustaa multinode-järjestelmän
    
    Args:
        election_id: Vaalin tunniste
        node_type: Solmun tyyppi
        config_manager: Config manager instance
        bootstrap_debug: Käytä debug-bootstrap peeritä
        
    Returns:
        tuple: (node_identity, network_manager) tai None jos epäonnistuu
    """
    if not MULTINODE_AVAILABLE:
        print("⚠️  Multinode not available, skipping node initialization")
        return None, None
    
    try:
        print("🌐 Alustetaan multinode-järjestelmä...")
        
        # 1. Luo node-identiteetti
        node_name = f"{node_type}_{election_id}"
        identity = NodeIdentity(
            election_id=election_id,
            node_type=node_type,
            node_name=node_name,
            domain="election_network"
        )
        
        # 2. Tallenna identiteetti
        identity.save_identity()
        print(f"✅ Node identity created: {identity.node_id}")
        
        # 3. Luo verkkomanageri
        network = NetworkManager(identity)
        
        # 4. Yhdistä verkkoon
        if bootstrap_debug:
            print("🔧 DEBUG: Using debug bootstrap peers")
            bootstrap_peers = get_debug_bootstrap_peers(election_id)
        else:
            bootstrap_peers = get_bootstrap_peers(election_id, config_manager)
            
        network.connect_to_network(bootstrap_peers)
        
        # 5. Alusta peer discovery
        discovery = PeerDiscovery(election_id)
        discovered_peers = discovery.discover_peers(force=True)
        print(f"🔍 Peer discovery found {len(discovered_peers)} peers")
        
        # 6. Lisää löydetyt peerit verkkoon
        for peer_info in discovered_peers:
            try:
                # Käytä debug-peeritä tai oikeaa peeriä
                if bootstrap_debug:
                    peer_identity = create_debug_peer_identity(election_id, peer_info)
                else:
                    peer_identity = create_peer_identity(election_id, peer_info)
                    
                network.add_peer(peer_identity)
                print(f"✅ Added peer: {peer_identity.node_id}")
            except Exception as e:
                print(f"⚠️  Failed to add discovered peer: {e}")
        
        print(f"🎉 Multinode system initialized: {identity.node_id}")
        print(f"   📡 Network peers: {network.get_peer_count()}")
        print(f"   🔗 Connection status: {network.connection_status}")
        
        return identity, network
        
    except Exception as e:
        print(f"❌ Multinode initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def get_bootstrap_peers(election_id, config_manager):
    """
    Hae bootstrap-peerit configista - YKSINKERTAISTETTU VERSIO
    
    Args:
        election_id: Vaalin tunniste
        config_manager: Config manager instance
        
    Returns:
        list: Tyhjä lista (ei bootstrap-peerejä oletuksena)
    """
    print("🔧 Using empty bootstrap peers (no bootstrap nodes configured)")
    return []  # Yksinkertainen ratkaisu - ei bootstrap-peerejä


def get_debug_bootstrap_peers(election_id):
    """
    Debug-bootstrap peerit testaamista varten
    
    Args:
        election_id: Vaalin tunniste
        
    Returns:
        list: Debug NodeIdentity-olioita
    """
    debug_peers = []
    try:
        print("🐛 DEBUG: Creating debug bootstrap peers...")
        
        # Luo 2 debug-peeriä
        for i in range(2):
            peer_identity = NodeIdentity(
                election_id=election_id,
                node_type="coordinator",
                node_name=f"debug_bootstrap_{election_id}_{i+1}",
                domain="debug_network"
            )
            debug_peers.append(peer_identity)
            print(f"🐛 DEBUG: Created bootstrap peer: {peer_identity.node_id}")
            
    except Exception as e:
        print(f"⚠️  Failed to create debug bootstrap peers: {e}")
    
    return debug_peers


def create_peer_identity(election_id, peer_info):
    """
    Luo NodeIdentity peer-infosta
    
    Args:
        election_id: Vaalin tunniste
        peer_info: Peerin tiedot
        
    Returns:
        NodeIdentity: Peerin identiteetti
    """
    return NodeIdentity(
        election_id=election_id,
        node_type=peer_info.get('node_type', 'worker'),
        node_name=peer_info.get('node_id', 'unknown_peer'),
        domain=peer_info.get('domain', 'discovered')
    )


def create_debug_peer_identity(election_id, peer_info):
    """
    Luo debug-NodeIdentity peer-infosta
    
    Args:
        election_id: Vaalin tunniste
        peer_info: Peerin tiedot
        
    Returns:
        NodeIdentity: Debug-peerin identiteetti
    """
    peer_id = peer_info.get('node_id', f"debug_peer_{len(peer_info)}")
    peer_identity = NodeIdentity(
        election_id=election_id,
        node_type="worker",
        node_name=peer_id,
        domain="debug_discovered"
    )
    # Ylikirjoita node_id debug-tunnuksella
    peer_identity.node_id = peer_id
    return peer_identity


def initialize_system_chain(election_id, config_hash, config_cid, template_hash, node_identity=None):
    """
    Alustaa system_chain.json config hashilla - MULTINODE EXTENDED
    
    Args:
        election_id: Vaalin tunniste
        config_hash: Config-tiedoston hash
        config_cid: IPFS CID configille
        template_hash: Template hash
        node_identity: NodeIdentity instance (multinode)
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
    
    # LISÄTTY: Multinode-tiedot system_chainiin
    if node_identity:
        chain_data["multinode_info"] = {
            "node_id": node_identity.node_id,
            "node_type": node_identity.node_type,
            "public_key_fingerprint": node_identity.keys["key_fingerprint"],
            "capabilities": node_identity.capabilities,
            "trust_score": node_identity.trust_score
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
@click.option('--enable-multinode', is_flag=True, help='Ota multinode käyttöön')
@click.option('--bootstrap-debug', is_flag=True, help='Käytä debug-bootstrap peeritä')
def install_system(election_id, first_install, node_type, version, enable_multinode, bootstrap_debug):
    """
    Asenna vaalikonejärjestelmä ja alusta config - MULTINODE VERSION
    
    Esimerkkejä:
        python install.py --first-install --election-id "Test2024"  # Perusasennus
        python install.py --first-install --election-id "Test2024" --enable-multinode  # Multinode
        python install.py --first-install --election-id "Test2024" --enable-multinode --bootstrap-debug  # Debug
    """
    
    # Alusta config manager
    config_manager = ConfigManager()
    
    # MULTINODE: Tarkista saatavuus
    if enable_multinode and not MULTINODE_AVAILABLE:
        print("❌ Multinode requested but modules not available")
        click.confirm("Continue without multinode?", abort=True)
        enable_multinode = False
    
    if first_install:
        if not election_id:
            election_id = click.prompt('📝 Anna vaalin tunniste', type=str)
        
        print(f"🚀 Aloitetaan ensimmäinen asennus: {election_id}")
        if enable_multinode:
            print(f"🌐 Multinode ENABLED - Node type: {node_type}")
            if bootstrap_debug:
                print("🐛 DEBUG: Bootstrap debug mode enabled")
        
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
            
            # 3. MULTINODE: Alusta node-järjestelmä
            node_identity = None
            network_manager = None
            if enable_multinode:
                node_identity, network_manager = initialize_multinode_system(
                    election_id, node_type, config_manager, bootstrap_debug
                )
            
            # 4. Julkaise IPFS:ään
            print("🌐 Julkaistaan config IPFS:ään...")
            config_cid = publish_config_to_ipfs(config_path)
            
            # 5. Alusta system_chain config hashilla (multinode-tiedot mukaan)
            config_hash = config["metadata"]["config_hash"]
            template_hash = config["metadata"]["template_hash"]
            
            chain_path = initialize_system_chain(
                election_id=election_id,
                config_hash=config_hash,
                config_cid=config_cid,
                template_hash=template_hash,
                node_identity=node_identity  # MULTINODE: node identity mukaan
            )
            print(f"✅ System chain alustettu: {chain_path}")
            
            # 6. Luo data-hakemistot
            data_path = config_manager.get_data_path(election_id)
            ensure_directory(data_path)
            print(f"✅ Data-hakemistot luotu: {data_path}")
            
            # 7. Luo perus data-tiedostot
            initialize_basic_data_files(election_id)
            
            # 8. MULTINODE: Tallenna node-tiedot
            if node_identity and network_manager:
                save_node_registry(election_id, node_identity, network_manager)
            
            print(f"\n🎉 JÄRJESTELMÄ ASENNETTU ONNISTUNEESTI!")
            print(f"📊 Vaali: {election_id}")
            print(f"🔧 Solmu: {node_type}")
            if enable_multinode:
                if node_identity:
                    print(f"🌐 Node ID: {node_identity.node_id}")
                    print(f"📡 Network peers: {network_manager.get_peer_count() if network_manager else 0}")
                    print(f"🔗 Connection: {network_manager.connection_status if network_manager else 'N/A'}")
                else:
                    print(f"🌐 Node: Multinode initialization failed")
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
                
                # MULTINODE: Alusta uusi node uudelle vaalille
                if enable_multinode:
                    node_identity, network_manager = initialize_multinode_system(
                        election_id, node_type, config_manager, bootstrap_debug
                    )
            else:
                print("ℹ️  Käytössä on nykyinen config")
        else:
            print("❌ Config tiedostoa ei löydy. Käytä --first-install")
            sys.exit(1)


def save_node_registry(election_id, node_identity, network_manager):
    """
    Tallenna node-rekisteri tiedostoon
    
    Args:
        election_id: Vaalin tunniste
        node_identity: NodeIdentity instance
        network_manager: NetworkManager instance
    """
    try:
        registry_path = Path(f"data/nodes/{election_id}/node_registry.json")
        ensure_directory(registry_path.parent)
        
        registry_data = {
            "election_id": election_id,
            "nodes": {
                node_identity.node_id: {
                    "identity": node_identity.to_dict(),
                    "network_stats": network_manager.get_network_stats(),
                    "registered_at": datetime.now().isoformat()
                }
            },
            "total_nodes": 1,
            "last_updated": datetime.now().isoformat()
        }
        
        with open(registry_path, 'w', encoding='utf-8') as f:
            json.dump(registry_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Node registry saved: {registry_path}")
        
    except Exception as e:
        print(f"⚠️  Failed to save node registry: {e}")


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
