#!/usr/bin/env python3
import click
import json
from datetime import datetime
import os
import sys
from pathlib import Path

# LISÄTTY: Lisää src hakemisto Python-polkuun
sys.path.insert(0, str(Path(__file__).parent.parent))

"""
Puolueiden vahvistuslogiikka - UUSI MODULAARINEN
"""
import click
from datetime import datetime
from typing import Dict

# KORJATTU: Käytetään yhteisiä file_utils-funktioita
try:
    from core.file_utils import read_json_file, write_json_file
    from core.validators import validate_party_id
except ImportError:
    from core.file_utils import read_json_file, write_json_file
    from core.validators import validate_party_id

class PartyVerification:
    """Puolueiden vahvistuslogiikka"""
    
    def __init__(self, election_id: str):
        self.election_id = election_id
        self.parties_file = f"data/runtime/parties.json"
    
    def verify_party(self, party_id: str, node_id: str, reason: str = "") -> bool:
        """Vahvista puolue"""
        
        if not validate_party_id(party_id):
            click.echo(f"❌ Virheellinen puolue ID: {party_id}")
            return False
        
        if not node_id:
            click.echo("❌ Anna --node-id parametri")
            return False
        
        try:
            data = read_json_file(self.parties_file, {"parties": []})
        except Exception as e:
            click.echo(f"❌ Puoluerekisterin lukuvirhe: {e}")
            return False
        
        # Etsi puolue
        party = next((p for p in data.get("parties", []) if p["party_id"] == party_id), None)
        if not party:
            click.echo(f"❌ Puoluetta '{party_id}' ei löydy")
            return False
        
        # Tarkista onko jo vahvistettu
        if party["registration"]["verification_status"] == "verified":
            click.echo("❌ Puolue on jo vahvistettu")
            return False
        
        # Tarkista onko jo vahvistanut
        if node_id in party["registration"]["verified_by"]:
            click.echo("❌ Olet jo vahvistanut tämän puolueen")
            return False
        
        # Lisää vahvistus
        party["registration"]["verified_by"].append(node_id)
        
        # Tarkista saadaanko kvoorumi
        verified_count = len(party["registration"]["verified_by"])
        needed = data["quorum_config"]["min_nodes_for_verification"]
        
        if verified_count >= needed:
            party["registration"]["verification_status"] = "verified"
            party["registration"]["verification_timestamp"] = datetime.now().isoformat()
            party["metadata"]["official_registration"] = True
            message = f"🎉 PUOLUE VAHVISTETTU! ({verified_count}/{needed} kvoorumi saavutettu)"
        else:
            message = f"✅ Puolue vahvistettu ({verified_count}/{needed})"
        
        action = "verified"
        
        # Päivitä viimeisin muokkausaika
        data["metadata"]["last_updated"] = datetime.now().isoformat()
        
        # Lisää historiaan
        data["verification_history"].append({
            "party_id": party_id,
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "by_node": node_id,
            "reason": reason or "Ei syytä annettu"
        })
        
        # Tallenna
        try:
            write_json_file(self.parties_file, data)
            click.echo(message)
            return True
        except Exception as e:
            click.echo(f"❌ Vahvistuksen tallennus epäonnistui: {e}")
            return False
    
    def reject_party(self, party_id: str, node_id: str, reason: str) -> bool:
        """Hylkää puolue"""
        
        if not validate_party_id(party_id):
            click.echo(f"❌ Virheellinen puolue ID: {party_id}")
            return False
        
        if not node_id:
            click.echo("❌ Anna --node-id parametri")
            return False
        
        if not reason:
            click.echo("❌ Anna --reason parametri hylkäykselle")
            return False
        
        try:
            data = read_json_file(self.parties_file, {"parties": []})
        except Exception as e:
            click.echo(f"❌ Puoluerekisterin lukuvirhe: {e}")
            return False
        
        # Etsi puolue
        party = next((p for p in data.get("parties", []) if p["party_id"] == party_id), None)
        if not party:
            click.echo(f"❌ Puoluetta '{party_id}' ei löydy")
            return False
            
        if party["registration"]["verification_status"] == "rejected":
            click.echo("❌ Puolue on jo hylätty")
            return False
            
        party["registration"]["verification_status"] = "rejected"
        party["registration"]["rejection_reason"] = reason
        action = "rejected"
        message = f"❌ Puolue hylätty: {reason}"
        
        # Päivitä viimeisin muokkausaika
        data["metadata"]["last_updated"] = datetime.now().isoformat()
        
        # Lisää historiaan
        data["verification_history"].append({
            "party_id": party_id,
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "by_node": node_id,
            "reason": reason
        })
        
        # Tallenna
        try:
            write_json_file(self.parties_file, data)
            click.echo(message)
            return True
        except Exception as e:
            click.echo(f"❌ Hylkäyksen tallennus epäonnistui: {e}")
            return False
