#!/usr/bin/env python3
"""
Puolueiden tilastot ja analytiikka - UUSI MODULAARINEN
"""
import click
from datetime import datetime
from typing import Dict

# KORJATTU: Käytetään yhteisiä file_utils-funktioita
try:
    from src.core.file_utils import read_json_file
except ImportError:
    from core.file_utils import read_json_file

class PartyAnalytics:
    """Puolueiden tilastot ja analytiikka"""
    
    def __init__(self, election_id: str):
        self.election_id = election_id
        self.parties_file = f"data/runtime/parties.json"
    
    def show_stats(self) -> bool:
        """Näytä puolueiden tilastot"""
        
        if not Path(self.parties_file).exists():
            click.echo("❌ Puoluerekisteriä ei ole vielä luotu")
            return False
        
        try:
            data = read_json_file(self.parties_file, {"parties": []})
        except Exception as e:
            click.echo(f"❌ Puoluerekisterin lukuvirhe: {e}")
            return False
        
        click.echo("📊 PUOLUETILASTOT")
        click.echo("=" * 50)
        
        total_parties = len(data.get("parties", []))
        verified_parties = [p for p in data.get("parties", []) if p["registration"]["verification_status"] == "verified"]
        pending_parties = [p for p in data.get("parties", []) if p["registration"]["verification_status"] == "pending"]
        rejected_parties = [p for p in data.get("parties", []) if p["registration"]["verification_status"] == "rejected"]
        
        click.echo(f"🏛️  Puolueita yhteensä: {total_parties}")
        click.echo(f"✅  Vahvistettuja: {len(verified_parties)}")
        click.echo(f"⏳  Odottaa vahvistusta: {len(pending_parties)}")
        click.echo(f"❌  Hylättyjä: {len(rejected_parties)}")
        
        # Ehdokastilastot
        total_candidates = sum(len(p["candidates"]) for p in data.get("parties", []))
        click.echo(f"👑  Ehdokkaita yhteensä: {total_candidates}")
        
        if verified_parties:
            click.echo(f"📈  Keskimäärin ehdokkaita/vahvistettu puolue: {total_candidates/len(verified_parties):.1f}")
        
        # Kvoorumitilanne
        click.echo(f"🔢  Vahvistus kvoorumi: {data['quorum_config']['min_nodes_for_verification']} nodea")
        
        # Viimeisimmät tapahtumat
        click.echo(f"\n📜 Viimeisimmät tapahtumat:")
        recent_events = data.get("verification_history", [])[-5:]
        for event in reversed(recent_events):
            action_icon = "✅" if event["action"] == "verified" else "❌" if event["action"] == "rejected" else "📝"
            click.echo(f"   {action_icon} {event['timestamp'][11:16]} - {event['party_id']}: {event['action']} ({event['by_node']})")
        
        return True
    
    def remove_party(self, party_id: str) -> bool:
        """Poista puolue rekisteristä"""
        
        if not Path(self.parties_file).exists():
            click.echo("❌ Puoluerekisteriä ei ole vielä luotu")
            return False
        
        try:
            data = read_json_file(self.parties_file, {"parties": []})
        except Exception as e:
            click.echo(f"❌ Puoluerekisterin lukuvirhe: {e}")
            return False
        
        # Etsi puolue
        party_index = next((i for i, p in enumerate(data.get("parties", [])) if p["party_id"] == party_id), None)
        if party_index is None:
            click.echo(f"❌ Puoluetta '{party_id}' ei löydy")
            return False
        
        party = data["parties"][party_index]
        
        # Poista puolue
        removed_party = data["parties"].pop(party_index)
        data["metadata"]["last_updated"] = datetime.now().isoformat()
        
        # Lisää historiaan
        data["verification_history"].append({
            "party_id": party_id,
            "timestamp": datetime.now().isoformat(),
            "action": "removed",
            "by_node": "system",
            "reason": "Puolue poistettu manuaalisesti"
        })
        
        # Tallenna
        try:
            write_json_file(self.parties_file, data)
            click.echo(f"✅ Puolue poistettu: {removed_party['name']['fi']} ({party_id})")
            click.echo(f"📝 Puolueessa oli {len(removed_party['candidates'])} ehdokasta")
            return True
        except Exception as e:
            click.echo(f"❌ Puolueen poisto epäonnistui: {e}")
            return False
