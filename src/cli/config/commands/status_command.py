"""
status_command.py - status komento config-hallinnalle
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

def status(election, proposal_id, verbose):
    """Näytä config-päivitysten tila - KORJATTU"""
    
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
        
        if proposal_id:
            proposal = taq_config._load_proposal(proposal_id)
            if proposal:
                click.echo("📋 CONFIG-PÄIVITYSEHDOTUS")
                click.echo("=" * 60)
                click.echo(f"🔑 ID: {proposal['proposal_id']}")
                click.echo(f"📊 Tyyppi: {proposal['type']}")
                click.echo(f"📈 Status: {proposal['status']}")
                click.echo(f"👤 Ehdotta: {proposal['proposer_node_id']}")
                click.echo(f"📝 Perustelu: {proposal['justification']}")
                
                # KORJATTU: changes-tietojen turvallinen käsittely
                changes = proposal.get('changes', {})
                if changes:
                    click.echo("🔧 MUUTOKSET:")
                    try:
                        if isinstance(changes, dict):
                            for key, value in changes.items():
                                click.echo(f"   • {key} = {value}")
                        else:
                            # Jos changes on tuple tai muu, muunna stringiksi
                            changes_str = str(changes)
                            if len(changes_str) > 100:
                                changes_str = changes_str[:100] + "..."
                            click.echo(f"   • {changes_str}")
                    except Exception as e:
                        click.echo(f"   • [Virhe changes-tiedoissa: {e}]")
                
                if proposal['status'] == 'pending':
                    votes = proposal.get('votes', {})
                    approve_count = len([v for v in votes.values() if v['vote'] == 'approve'])
                    total_votes = len(votes)
                    
                    click.echo(f"📊 Äänet: {approve_count}/{total_votes} hyväksyntää")
                    
            else:
                click.echo("❌ Ehdotusta ei löydy")
        else:
            proposals = taq_config.get_all_proposals()
            click.echo("📋 CONFIG-PÄIVITYSEHDOTUKSET")
            click.echo("=" * 60)
            
            if not proposals:
                click.echo("ℹ️  Ei aktiivisia ehdotuksia")
                return
                
            for prop in proposals:
                status_icon = "✅" if prop['status'] == 'approved' else "⏳" if prop['status'] == 'pending' else "❌"
                votes = prop.get('votes', {})
                approve_count = len([v for v in votes.values() if v['vote'] == 'approve'])
                total_votes = len(votes)
                
                click.echo(f"{status_icon} {prop['proposal_id'][:16]}...")
                click.echo(f"   Tyyppi: {prop['type']} | Status: {prop['status']}")
                click.echo(f"   Äänet: {approve_count}/{total_votes}")
                click.echo()
                
    except Exception as e:
        click.echo(f"❌ Tilahaun epäonnistui: {e}")
