"""
add_command.py - Add candidate command
"""
import click
from datetime import datetime
from src.cli.candidates.utils.candidate_manager import CandidateManager

def add_candidate(election_id, name_fi, name_en=None, party=None, domain=None):
    """Add new candidate"""
    
    try:
        manager = CandidateManager(election_id)
        
        # Validate required fields
        if not name_fi:
            click.echo("❌ Ehdokkaan nimi (suomeksi) on pakollinen")
            return False
        
        # Validate name uniqueness
        if not manager.validate_candidate_name(name_fi):
            click.echo(f"❌ Ehdokas nimellä '{name_fi}' on jo olemassa")
            return False
        
        # Load existing candidates
        data = manager.load_candidates()
        candidates = data.get("candidates", [])
        
        # Create new candidate
        new_candidate = {
            "id": manager.generate_candidate_id(),
            "basic_info": {
                "name": {
                    "fi": name_fi.strip(),
                    "en": name_en.strip() if name_en else ""
                },
                "party": party.strip() if party else "",
                "domain": domain.strip() if domain else "",
                "status": "active",
                "created": datetime.now().isoformat()
            },
            "answers": {},
            "media": {},
            "metadata": {
                "last_updated": datetime.now().isoformat()
            }
        }
        
        # Add to list and save
        candidates.append(new_candidate)
        data["candidates"] = candidates
        
        if manager.save_candidates(data):
            click.echo(f"✅ Ehdokas '{name_fi}' lisätty onnistuneesti!")
            click.echo(f"📋 ID: {new_candidate['id']}")
            return True
        else:
            click.echo("❌ Ehdokkaan tallentaminen epäonnistui")
            return False
            
    except Exception as e:
        click.echo(f"❌ Ehdokkaan lisääminen epäonnistui: {e}")
        return False
