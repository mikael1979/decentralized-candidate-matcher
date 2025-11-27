"""
vote_command.py - vote komento config-hallinnalle
"""
import click
from src.core.config import ConfigManager
from src.core.file_utils import read_json_file, write_json_file

# Käytä samaa get_election_id funktiota kuin propose_command.py:ssä
try:
    from src.core import get_election_id
except ImportError:
    # Fallback jos ei löydy config_managerista
    def get_election_id(election_param: str = None) -> str:
        """Hae vaalitunniste parametrista tai configista"""
        if election_param:
            return election_param
        return "Jumaltenvaalit2026"  # Oletus

def vote(election, proposal_id, vote, node_id, justification):
    """Äänestä config-päivitysehdotuksesta"""
    
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
        
        weight = 3.0 if "zeus" in node_id else 2.0 if "athena" in node_id else 1.0

        success = taq_config.cast_vote_on_config(
            proposal_id, node_id, vote, weight, justification or ""
        )

        if success:
            proposal = taq_config._load_proposal(proposal_id)
            click.echo(f"✅ Ääni vastaanotettu: {vote}")
            if proposal["status"] == "approved":
                click.echo("🎉 CONFIG-PÄIVITYS HYVÄKSYTTY!")
            elif proposal["status"] == "rejected":
                click.echo("❌ Config-päivitys hylätty.")
            else:
                click.echo("⏳ Odotetaan lisää ääniä...")
        else:
            click.echo("❌ Äänestys epäonnistui")
            
    except Exception as e:
        click.echo(f"❌ Äänestys epäonnistui: {e}")
