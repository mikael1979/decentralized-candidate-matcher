"""
list_command.py - List candidates command
"""
import click
from src.cli.candidates.utils.candidate_manager import CandidateManager

def list_candidates(election_id, verbose=False):
    """List all candidates"""
    
    try:
        manager = CandidateManager(election_id)
        
        # Load candidates
        data = manager.load_candidates()
        candidates = data.get("candidates", [])
        
        if not candidates:
            click.echo("ℹ️  Ei ehdokkaita")
            return True
        
        click.echo("📋 EHDOKKAAT")
        click.echo("=" * 60)
        
        for i, candidate in enumerate(candidates, 1):
            basic_info = candidate.get("basic_info", {})
            name_info = basic_info.get("name", {})
            
            name_fi = name_info.get("fi", "Nimetön")
            name_en = name_info.get("en", "")
            party = basic_info.get("party", "")
            domain = basic_info.get("domain", "")
            status = basic_info.get("status", "active")
            
            status_icon = "✅" if status == "active" else "⏸️"
            
            click.echo(f"{i}. {status_icon} {name_fi}")
            click.echo(f"   🆔 {candidate.get('id', 'N/A')}")
            
            if verbose:
                if name_en:
                    click.echo(f"   🇬🇧 {name_en}")
                if party:
                    click.echo(f"   🏛️  {party}")
                if domain:
                    click.echo(f"   🗺️  {domain}")
                click.echo(f"   📅 Luotu: {basic_info.get('created', 'N/A')}")
                click.echo()
            else:
                if party:
                    click.echo(f"   🏛️  {party}")
                if domain:
                    click.echo(f"   🗺️  {domain}")
                click.echo()
        
        click.echo(f"📊 Yhteensä: {len(candidates)} ehdokasta")
        return True
            
    except Exception as e:
        click.echo(f"❌ Ehdokkaiden listaus epäonnistui: {e}")
        return False
