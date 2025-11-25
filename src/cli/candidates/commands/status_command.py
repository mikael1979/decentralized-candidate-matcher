"""
status_command.py - Change candidate status command
"""
import click
from datetime import datetime
from src.cli.candidates.utils.candidate_manager import CandidateManager

def change_candidate_status(election_id, candidate_identifier, active=True):
    """Change candidate active/inactive status"""
    
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
        candidate_name = ""
        
        for candidate in candidates:
            candidate_found = False
            
            # Check by ID
            if candidate.get("id") == candidate_identifier:
                candidate_found = True
            # Check by Finnish name
            elif candidate.get("basic_info", {}).get("name", {}).get("fi", "").lower() == candidate_identifier.lower():
                candidate_found = True
            
            if candidate_found:
                current_status = candidate.get("basic_info", {}).get("status", "active")
                new_status = "active" if active else "inactive"
                
                # Only update if status actually changes
                if current_status != new_status:
                    candidate["basic_info"]["status"] = new_status
                    candidate["metadata"]["last_updated"] = datetime.now().isoformat()
                    candidate_updated = True
                    candidate_name = candidate.get("basic_info", {}).get("name", {}).get("fi", candidate_identifier)
                else:
                    status_text = "aktiivinen" if active else "epäaktiivinen"
                    click.echo(f"ℹ️  Ehdokas '{candidate_identifier}' on jo {status_text}")
                    return True
                break
        
        if not candidate_updated:
            click.echo(f"❌ Ehdokasta '{candidate_identifier}' ei löydy")
            return False
        
        # Save updated data
        data["candidates"] = candidates
        
        if manager.save_candidates(data):
            status_text = "aktiiviseksi" if active else "epäaktiiviseksi"
            click.echo(f"✅ Ehdokas '{candidate_name}' merkitty {status_text}!")
            return True
        else:
            click.echo("❌ Ehdokkaan statuksen muuttaminen epäonnistui")
            return False
            
    except Exception as e:
        click.echo(f"❌ Ehdokkaan statuksen muuttaminen epäonnistui: {e}")
        return False
