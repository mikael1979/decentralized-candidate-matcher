"""
Pääasennuskomento.
"""
import click
import sys
import json
from pathlib import Path

# Import riippuvuudet
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from core.config import ConfigManager
from core.file_utils import ensure_directory

# Import utils-moduulit
from ..utils.ipfs_utils import check_system_installed, load_elections_list
from ..utils.node_utils import initialize_node
from ..utils.election_utils import show_elections_hierarchy, validate_election_id
from ..utils.file_utils import initialize_basic_data_files


@click.command()
@click.option('--election-id', help='Valitse vaali (valinnainen)')
@click.option('--node-type', default='worker', help='Solmun tyyppi (coordinator/worker)')
@click.option('--node-name', help='Solmun nimi (valinnainen)')
@click.option('--list-elections', is_flag=True, help='Näytä saatavilla olevat vaalit')
@click.option('--enable-multinode', is_flag=True, help='Ota multinode käyttöön')
def install_command(election_id, node_type, node_name, list_elections, enable_multinode):
    """
    Asenna vaalikone - lataa IPFS:stä vaalilistan ja alusta node
    
    Esimerkkejä:
        # Näytä saatavilla olevat vaalit:
        python -m src.cli.install --list-elections
        
        # Asenna tietty vaali:
        python -m src.cli.install --election-id "olympian_gods_2024" --enable-multinode
        
        # Asenna työntekijänode:
        python -m src.cli.install --election-id "finland_presidential_2024" --node-type worker
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
        # Käytä click.prompt() oikein
        ctx = click.get_current_context()
        if ctx.invoked_subcommand is None:
            election_id = click.prompt('\n📝 Valitse vaali (election_id)', type=str)
        else:
            return
    
    # Tarkista että vaali on olemassa
    if not validate_election_id(election_id, elections_data):
        print(f"❌ Vaalia '{election_id}' ei löydy")
        return
    
    # Alusta config manager
    config_manager = ConfigManager()
    
    # Tarkista onko config jo olemassa
    current_config = None
    try:
        # Yritä eri metodeja
        if hasattr(config_manager, 'get_election_config'):
            current_config = config_manager.get_election_config()
        elif hasattr(config_manager, 'load_config'):
            current_config = config_manager.load_config()
        elif hasattr(config_manager, 'get_config'):
            current_config = config_manager.get_config()
        else:
            # Lue suoraan tiedostosta
            config_path = Path("config.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    current_config = json.load(f)
    except Exception as e:
        print(f"⚠️  Config load failed: {e}")
        current_config = None
    
    # Jos config on olemassa ja vaali eri, kysy vahvistus
    current_election_id = None
    if current_config:
        # Yritä eri tapoja saada election_id
        if current_config.get("metadata") and current_config["metadata"].get("election_id"):
            current_election_id = current_config["metadata"]["election_id"]
        elif current_config.get("election_id"):
            current_election_id = current_config["election_id"]
        elif current_config.get("election", {}).get("id"):
            current_election_id = current_config["election"]["id"]
    
    if current_election_id and current_election_id != election_id:
        try:
            if not click.confirm(
                f"Haluatko vaihtaa vaalia '{current_election_id}' -> '{election_id}'?",
                default=False
            ):
                print("Asennus peruutettu.")
                return
        except Exception as e:
            print(f"⚠️  Confirmation failed: {e}")
            print("Asennus peruutettu.")
            return
    
    # Generoi config - käytä oikeaa ConfigManager-menetelmää
    print(f"📋 Alustetaan config vaalille: {election_id}")
    
    config = None
    try:
        # Yritä eri metodeja configin generointiin
        if hasattr(config_manager, '_create_default_config'):
            config = config_manager._create_default_config(election_id)
            # Lisää node_type jos saatavilla
            if node_type and 'metadata' in config:
                config['metadata']['node_type'] = node_type
                config['metadata']['version'] = "2.0.0"
        else:
            # Luo manuaalinen config
            config = {
                "metadata": {
                    "election_id": election_id,
                    "node_type": node_type,
                    "version": "2.0.0",
                    "created_at": datetime.now().isoformat()
                },
                "election": {
                    "id": election_id,
                    "name": f"Vaalikone - {election_id}",
                    "status": "active"
                }
            }
    except Exception as e:
        print(f"⚠️  Config generation failed: {e}")
        # Luo perus config
        import datetime
        config = {
            "metadata": {
                "election_id": election_id,
                "node_type": node_type,
                "version": "2.0.0",
                "created_at": datetime.datetime.now().isoformat()
            }
        }
    
    # Tallenna config
    config_path = None
    try:
        # Yritä eri tallennusmetodeja
        if hasattr(config_manager, 'update_config_with_taq'):
            # Tämä saattaa olla oikea tapa refaktoroituun ConfigManageriin
            config_manager.update_config_with_taq(config, "install", "system")
            config_path = Path("config.json")
        elif hasattr(config_manager, 'save_config'):
            config_path = config_manager.save_config(config)
        else:
            # Fallback: tallenna itse
            config_path = Path("config.json")
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
    except Exception as e:
        print(f"⚠️  Config save failed: {e}")
        config_path = Path("config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    print(f"✅ Config tallennettu: {config_path}")
    
    # Alusta node
    node_identity = None
    if enable_multinode:
        node_identity = initialize_node(election_id, node_type, node_name)
    
    # Luo data-hakemistot
    data_path = None
    try:
        if hasattr(config_manager, 'get_data_path'):
            data_path = config_manager.get_data_path(election_id)
        else:
            # Fallback: käytä vakio polkua
            data_path = Path(f"data/{election_id}")
    except Exception as e:
        print(f"⚠️  Data path failed: {e}")
        data_path = Path(f"data/{election_id}")
    
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
