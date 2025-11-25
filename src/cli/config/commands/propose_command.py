"""
propose_command.py - propose komento config-hallinnalle
"""
import json
import click
from pathlib import Path
from ....core.config_manager import ConfigManager
from ....core.file_utils import read_json_file, write_json_file

# Lisää get_election_id import
try:
    from ....core.config_manager import get_election_id
except ImportError:
    # Fallback jos ei löydy config_managerista
    def get_election_id(election_param: str = None) -> str:
        """Hae vaalitunniste parametrista tai configista"""
        if election_param:
            return election_param
        return "Jumaltenvaalit2026"

def propose_update(election, key, value, update_type, justification, node_id):
    """Ehdotta config-päivitystä TAQ-kvoorumille"""
    
    election_id = get_election_id(election)
    if not election_id:
        click.echo("❌ Vaalia ei ole asetettu")
        return
    
    try:
        # Varmista että config-hakemisto on olemassa
        config_dir = Path(f"config/elections/{election_id}")
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Jäsennä arvo oikein
        try:
            parsed_value = json.loads(value)
        except json.JSONDecodeError:
            if value.lower() in ['true', 'false']:
                parsed_value = value.lower() == 'true'
            elif value.isdigit():
                parsed_value = int(value)
            elif value.replace('.', '').isdigit():
                parsed_value = float(value)
            else:
                parsed_value = value.strip('"\'')
        
        changes = {key: parsed_value}
        
        click.echo(f"🔄 Aloitetaan config-päivitys...")
        click.echo(f"🏛️  Vaali: {election_id}")
        
        config_mgr = ConfigManager()
        
        result = config_mgr.update_config_with_taq(
            changes, update_type, justification, node_id, election_id
        )
        
        if result["status"] == "proposed":
            click.echo("")
            click.echo("✅ CONFIG-PÄIVITYS EHOTETTU ONNISTUNEESTI!")
            click.echo("=" * 50)
            click.echo(f"📋 Proposal ID: {result['proposal_id']}")
            click.echo(f"🔑 Muutos: {key} = {parsed_value}")
            click.echo("⏳ Odota kvoorumin hyväksyntää...")
            
        else:
            click.echo(f"❌ {result['message']}")
            
    except Exception as e:
        click.echo(f"❌ Config-päivitys epäonnistui: {e}")
