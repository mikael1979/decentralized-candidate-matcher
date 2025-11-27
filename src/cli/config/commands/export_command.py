"""
export_command.py - export/history komento config-hallinnalle
"""
import click
from src.core.config import ConfigManager
from src.core.file_utils import read_json_file, write_json_file

# Käytä samaa get_election_id funktiota
try:
    from src.core import get_election_id
except ImportError:
    # Fallback jos ei löydy config_managerista
    def get_election_id(election_param: str = None) -> str:
        """Hae vaalitunniste parametrista tai configista"""
        if election_param:
            return election_param
        return "Jumaltenvaalit2026"  # Oletus

def history(election):
    """Näytä config-päivityshistoria"""
    
    election_id = get_election_id(election)
    if not election_id:
        click.echo("❌ Vaalia ei ole asetettu")
        return
    
    try:
        config_mgr = ConfigManager()
        history_data = config_mgr.get_config_update_history(election_id)
        
        if not history_data:
            click.echo("ℹ️  Ei config-päivityshistoriaa")
            return
            
        click.echo("📜 CONFIG-PÄIVITYSHISTORIA")
        click.echo("=" * 60)
        
        for i, entry in enumerate(history_data, 1):
            click.echo(f"{i}. {entry['timestamp']}")
            click.echo(f"   📋 Proposal: {entry['proposal_id'][:16]}...")
            click.echo(f"   👤 Hyväksyjät: {len(entry.get('approved_by', []))}")
            if entry.get('justification'):
                click.echo(f"   📝 {entry['justification'][:50]}...")
            click.echo()
            
    except Exception as e:
        click.echo(f"❌ Historian haku epäonnistui: {e}")
