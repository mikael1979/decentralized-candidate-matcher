"""
Käyttöliittymä asennukseen - Click CLI
"""
import click
import sys
from pathlib import Path

# Lisää polku
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    # Yritä suhteellista importtia
    from .installer import SystemInstaller
except ImportError as e:
    print(f"⚠️  Relative import failed: {e}")
    # Yritä absoluuttista
    try:
        from src.cli.install.installer import SystemInstaller
    except ImportError as e2:
        print(f"❌ Absolute import also failed: {e2}")
        raise


@click.command()
@click.option('--election-id', help='Valitse vaali (valinnainen)')
@click.option('--node-type', default='worker', help='Solmun tyyppi (coordinator/worker)')
@click.option('--node-name', help='Solmun nimi (valinnainen)')
@click.option('--list-elections', is_flag=True, help='Näytä saatavilla olevat vaalit')
@click.option('--enable-multinode', is_flag=True, help='Ota multinode käyttöön')
def install_system(election_id, node_type, node_name, list_elections, enable_multinode):
    """
    Asenna vaalikone - lataa IPFS:stä vaalilistan ja alusta node
    """
    
    print("🔍 Tarkistetaan IPFS-asennusta...")
    
    installer = SystemInstaller()
    
    success, result = installer.run(
        election_id=election_id,
        node_type=node_type,
        node_name=node_name,
        enable_multinode=enable_multinode,
        list_elections=list_elections
    )
    
    if not success:
        print(result)
        return
    
    if list_elections:
        return  # Vaalilista on jo näytetty
    
    # Tulosta onnistunut asennus
    print(f"\n🎉 ASENNUS VALMIS!")
    print(f"📊 Vaali: {result['election_id']}")
    print(f"🔧 Solmu: {result['node_type']}")
    if result.get('node_identity'):
        print(f"🌐 Node ID: {result['node_identity'].node_id}")
    print(f"📁 Config: {result['config_path']}")
    print(f"💾 Data: {result['data_path']}")


if __name__ == "__main__":
    install_system()
