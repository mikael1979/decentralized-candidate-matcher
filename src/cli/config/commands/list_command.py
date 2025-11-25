"""
list_command.py - list komento config-hallinnalle
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

def list(election):
    """Listaa kaikki config-päivitysehdotukset"""
    
    election_id = get_election_id(election)
    if not election_id:
        click.echo("❌ Vaalia ei ole asetettu")
        return
    
    try:
        # Korjattu import
        try:
            from src.managers.taq_config_manager import TAQConfigManager
        except ImportError:
            from managers.taq_config_manager import TAQConfigManager
            
        taq_config = TAQConfigManager(election_id)
        proposals = taq_config.get_all_proposals()
        
        if not proposals:
            click.echo("ℹ️  Ei config-päivitysehdotuksia")
            return
            
        click.echo("📋 CONFIG-PÄIVITYSEHDOTUKSET")
        
        for i, prop in enumerate(proposals, 1):
            status_icon = "✅" if prop['status'] == 'approved' else "⏳" if prop['status'] == 'pending' else "❌"
            votes = prop.get('votes', {})
            approve_count = len([v for v in votes.values() if v['vote'] == 'approve'])
            total_votes = len(votes)
            
            click.echo(f"{i}. {status_icon} {prop['proposal_id'][:16]}...")
            click.echo(f"   Tyyppi: {prop['type']} | Status: {prop['status']}")
            click.echo(f"   Äänet: {approve_count}/{total_votes}")
            click.echo()
            
    except Exception as e:
        click.echo(f"❌ Listaus epäonnistui: {e}")
