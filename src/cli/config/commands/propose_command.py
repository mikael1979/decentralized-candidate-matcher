"""
Propose config update command.
"""
import click
import sys
from pathlib import Path

# Lisää projektin juuri Python-polkuun
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Import ConfigManager suhteellisesti
try:
    # Yritä ensin core.config-managerista
    from core.config import ConfigManager
except ImportError:
    # Fallback: yritä suoraan config_manager.py:stä
    try:
        from core.config_manager import ConfigManager
    except ImportError as e:
        print(f"❌ ConfigManager import failed: {e}")
        sys.exit(1)


@click.command()
@click.option('--election', required=False, help='Election ID (optional)')
@click.option('--change-type', required=True, type=click.Choice(['add', 'update', 'remove']), 
              help='Type of change')
@click.option('--key', required=True, help='Config key to change')
@click.option('--value', required=True, help='New value')
@click.option('--reason', help='Reason for change')
def propose_update(election, change_type, key, value, reason):
    """Propose a config update to TAQ network."""
    try:
        manager = ConfigManager(election_id=election)
        
        # Create change proposal
        changes = {key: value}
        
        # Submit to TAQ
        result = manager.update_config_with_taq(
            changes=changes,
            update_type=change_type,
            node_id="cli_proposer",
            reason=reason or "CLI update"
        )
        
        if result.get("success"):
            click.echo(f"✅ Proposal submitted: {result.get('message')}")
            if result.get("transaction_hash"):
                click.echo(f"📝 Transaction: {result.get('transaction_hash')}")
        else:
            click.echo(f"❌ Failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}")
