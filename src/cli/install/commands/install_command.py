"""
Pääasennuskomento.
"""
import click
import sys
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
    current_config = config_manager.load_config()
    if current_config and current_config["metadata"]["election_id"] != election_id:
        if not click.confirm(
            f"Haluatko vaihtaa vaalia '{current_config['metadata']['election_id']}' -> '{election_id}'?",
            default=False
        ):
            print("Asennus peruutettu.")
            return
    
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
