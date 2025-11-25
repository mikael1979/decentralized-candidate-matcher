"""
remove_command.py - Remove candidate command
"""
import click
from src.cli.candidates.utils.candidate_manager import CandidateManager

def remove_candidate(election_id, candidate_identifier):
    """Remove candidate by ID or name"""
    
    try:
        manager = CandidateManager(election_id)
        
        # Validate input
        if not candidate_identifier:
            click.echo("❌ Ehdokas-ID tai nimi on pakollinen")
            return False
        
        # Load candidates and find the one to remove
        data = manager.load_candidates()
        candidates = data.get("candidates", [])
        
        candidate_to_remove = None
        remaining_candidates = []
        
        for candidate in candidates:
            # Check by ID
            if candidate.get("id") == candidate_identifier:
                candidate_to_remove = candidate
            # Check by Finnish name
            elif candidate.get("basic_info", {}).get("name", {}).get("fi", "").lower() == candidate_identifier.lower():
                candidate_to_remove = candidate
            else:
                remaining_candidates.append(candidate)
        
        if not candidate_to_remove:
            click.echo(f"❌ Ehdokasta '{candidate_identifier}' ei löydy")
            return False
        
        # Confirm removal
        candidate_name = candidate_to_remove.get("basic_info", {}).get("name", {}).get("fi", "tuntematon")
        if not click.confirm(f"Haluatko varmasti poistaa ehdokkaan '{candidate_name}'?"):
            click.echo("❌ Poisto peruutettu")
            return False
        
        # Save updated list
        data["candidates"] = remaining_candidates
        
        if manager.save_candidates(data):
            click.echo(f"✅ Ehdokas '{candidate_name}' poistettu onnistuneesti!")
            return True
        else:
            click.echo("❌ Ehdokkaan poistaminen epäonnistui")
            return False
            
    except Exception as e:
        click.echo(f"❌ Ehdokkaan poistaminen epäonnistui: {e}")
        return False
