"""
update_command.py - Update candidate command
"""
import click
from datetime import datetime
from src.cli.candidates.utils.candidate_manager import CandidateManager

def update_candidate(election_id, candidate_identifier, name_fi=None, name_en=None, party=None, domain=None):
    """Update candidate information"""
    
    try:
        manager = CandidateManager(election_id)
        
        # Validate input
        if not candidate_identifier:
            click.echo("❌ Ehdokas-ID tai nimi on pakollinen")
            return False
        
        # Load candidates and find the one to update
        data = manager.load_candidates()
        candidates = data.get("candidates", [])
        
        candidate_updated = False
        
        for candidate in candidates:
            candidate_found = False
            
            # Check by ID
            if candidate.get("id") == candidate_identifier:
                candidate_found = True
            # Check by Finnish name
            elif candidate.get("basic_info", {}).get("name", {}).get("fi", "").lower() == candidate_identifier.lower():
                candidate_found = True
            
            if candidate_found:
                # Update fields if provided
                if name_fi:
                    # Check name uniqueness if changing name
                    if name_fi != candidate.get("basic_info", {}).get("name", {}).get("fi", ""):
                        if not manager.validate_candidate_name(name_fi):
                            click.echo(f"❌ Ehdokas nimellä '{name_fi}' on jo olemassa")
                            return False
                    candidate["basic_info"]["name"]["fi"] = name_fi.strip()
                
                if name_en:
                    candidate["basic_info"]["name"]["en"] = name_en.strip()
                
                if party is not None:  # Allow empty string
                    candidate["basic_info"]["party"] = party.strip()
                
                if domain is not None:  # Allow empty string
                    candidate["basic_info"]["domain"] = domain.strip()
                
                # Update metadata
                candidate["metadata"]["last_updated"] = datetime.now().isoformat()
                candidate_updated = True
                break
        
        if not candidate_updated:
            click.echo(f"❌ Ehdokasta '{candidate_identifier}' ei löydy")
            return False
        
        # Save updated data
        data["candidates"] = candidates
        
        if manager.save_candidates(data):
            click.echo(f"✅ Ehdokas '{candidate_identifier}' päivitetty onnistuneesti!")
            return True
        else:
            click.echo("❌ Ehdokkaan päivittäminen epäonnistui")
            return False
            
    except Exception as e:
        click.echo(f"❌ Ehdokkaan päivittäminen epäonnistui: {e}")
        return False
