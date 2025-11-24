#!/usr/bin/env python3
"""
Config-tiedostojen hallinta TAQ-kvoorumilla - VIIMEINEN KORJAUS
"""
import click
import json
from pathlib import Path
import sys
from typing import Dict, List, Optional

# Lisää src hakemisto Python-polkuun
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config_manager import get_election_id, get_data_path

@click.group()
def manage_config():
    """Config-tiedostojen hallinta TAQ-kvoorumilla"""
    pass

@manage_config.command()
@click.option('--election', required=False, help='Vaalitunniste')
@click.option('--key', required=True, help='Päivitettävä config-avain')
@click.option('--value', required=True, help='Uusi arvo')
@click.option('--type', 'update_type', required=True, 
              type=click.Choice(['minor', 'major', 'emergency']),
              help='Päivitystyyppi')
@click.option('--justification', required=True, help='Muutoksen perustelu')
@click.option('--node-id', required=True, help='Ehdotuksen tekijän node-id')
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
        
        from core.config_manager import ConfigManager
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

@manage_config.command()
@click.option('--election', required=False, help='Vaalitunniste')
@click.option('--proposal-id', required=True, help='Päivitysehdotuksen ID')
@click.option('--vote', type=click.Choice(['approve', 'reject', 'abstain']), required=True)
@click.option('--node-id', required=True, help='Äänestäjän node-id')
@click.option('--justification', help='Äänestysperustelu')
def vote(election, proposal_id, vote, node_id, justification):
    """Äänestä config-päivitysehdotuksesta"""
    
    election_id = get_election_id(election)
    if not election_id:
        click.echo("❌ Vaalia ei ole asetettu")
        return
    
    try:
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

@manage_config.command()
@click.option('--election', required=False, help='Vaalitunniste')
@click.option('--proposal-id', help='Näytä tietyn ehdotuksen tila')
@click.option('--verbose', '-v', is_flag=True, help='Näytä yksityiskohtainen tila')
def status(election, proposal_id, verbose):
    """Näytä config-päivitysten tila - KORJATTU"""
    
    election_id = get_election_id(election)
    if not election_id:
        click.echo("❌ Vaalia ei ole asetettu")
        return
    
    try:
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

@manage_config.command()
@click.option('--election', required=False, help='Vaalitunniste')
def list(election):
    """Listaa kaikki config-päivitysehdotukset"""
    
    election_id = get_election_id(election)
    if not election_id:
        click.echo("❌ Vaalia ei ole asetettu")
        return
    
    try:
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

@manage_config.command()
@click.option('--election', required=False, help='Vaalitunniste')
def config_info(election):
    """Näytä nykyisen configin tiedot"""
    
    election_id = get_election_id(election)
    if not election_id:
        click.echo("❌ Vaalia ei ole asetettu")
        return
    
    try:
        from core.config_manager import ConfigManager
        config_mgr = ConfigManager(election_id)
        
        # Yritä lukea config suoraan tiedostosta
        config_path = Path(f"config/elections/{election_id}/election_config.json")
        if config_path.exists():
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            click.echo("📄 NYKYINEN CONFIG-TIEDOSTO")
            click.echo(f"🏛️  Vaali: {election_id}")
            click.echo(f"📁 Polku: {config_path}")
            
            # Näytä tärkeimmät asetukset
            if 'ui' in config_data:
                click.echo(f"🎨 UI-teema: {config_data['ui'].get('default_theme', 'ei asetettu')}")
            
        else:
            click.echo("❌ Config-tiedostoa ei löydy")
            click.echo("💡 Luo ensin config-tiedosto:")
            click.echo(f"   python src/cli/manage_config.py propose-update --key 'ui.default_theme' --value '\"light\"' --type minor --node-id node_zeus")
        
    except Exception as e:
        click.echo(f"❌ Config-tiedon haku epäonnistui: {e}")

@manage_config.command()
@click.option('--election', required=False, help='Vaalitunniste')
def history(election):
    """Näytä config-päivityshistoria"""
    
    election_id = get_election_id(election)
    if not election_id:
        click.echo("❌ Vaalia ei ole asetettu")
        return
    
    try:
        from core.config_manager import ConfigManager
        config_mgr = ConfigManager(election_id)
        history = config_mgr.get_config_update_history()
        
        if not history:
            click.echo("ℹ️  Ei config-päivityshistoriaa")
            click.echo("💡 Historia luodaan automaattisesti config-päivitysten yhteydessä")
            return
            
        click.echo("📜 CONFIG-PÄIVITYSHISTORIA")
        
        for i, entry in enumerate(reversed(history[-5:]), 1):
            click.echo(f"{i}. {entry.get('timestamp', 'N/A')}")
            click.echo(f"   Proposal: {entry.get('proposal_id', 'N/A')}")
            click.echo()
            
    except Exception as e:
        click.echo(f"❌ Historian haku epäonnistui: {e}")

@manage_config.command()
def help():
    """Näytä käyttöohjeet"""
    click.echo("🎯 CONFIG-HALLINNAN KÄYTTÖOHJEET")
    click.echo("=" * 40)
    click.echo("📋 propose-update - Ehdotta config-muutosta")
    click.echo("📋 vote          - Äänestä ehdotuksesta")
    click.echo("📋 status        - Näytä ehdotusten tila")
    click.echo("📋 list          - Listaa kaikki ehdotukset")
    click.echo("📋 config-info   - Näytä nykyinen config")
    click.echo("📋 history       - Näytä päivityshistoria")

if __name__ == '__main__':
    manage_config()
