"""
get_command.py - get/info komento config-hallinnalle
"""
import click
from src.core.config_manager import ConfigManager
from src.core.file_utils import read_json_file, write_json_file

# Käytä samaa get_election_id funktiota
try:
    from src.core.config_manager import get_election_id
except ImportError:
    # Fallback jos ei löydy config_managerista
    def get_election_id(election_param: str = None) -> str:
        """Hae vaalitunniste parametrista tai configista"""
        if election_param:
            return election_param
        return "Jumaltenvaalit2026"  # Oletus

def config_info(election):
    """Näytä config-tiedoston perustiedot"""
    
    election_id = get_election_id(election)
    if not election_id:
        click.echo("❌ Vaalia ei ole asetettu")
        return
    
    try:
        config_mgr = ConfigManager()
        info = config_mgr.get_config_info(election_id)
        
        if not info:
            click.echo("❌ Config-tietoja ei löydy")
            return
            
        click.echo("📊 CONFIG-TIEDOT")
        click.echo("=" * 50)
        click.echo(f"🏛️  Vaali: {info['election_id']}")
        click.echo(f"🔐 Hash: {info['config_hash'][:16]}...")
        click.echo(f"🕒 Päivitetty: {info['last_updated']}")
        click.echo(f"📈 Päivityksiä: {info['update_count']}")
        click.echo(f"❓ Max kysymyksiä: {info['max_questions']}")
        click.echo(f"👤 Max ehdokkaita: {info['max_candidates']}")
        
    except Exception as e:
        click.echo(f"❌ Config-tietojen haku epäonnistui: {e}")
