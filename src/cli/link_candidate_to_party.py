#!/usr/bin/env python3
import click
import json
from datetime import datetime
import os
import sys
from pathlib import Path

# LISÄTTY: Lisää src hakemisto Python-polkuun
sys.path.insert(0, str(Path(__file__).parent.parent))

import click
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

@click.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--candidate-id', required=True, help='Ehdokkaan tunniste')
@click.option('--party-id', required=True, help='Puolueen tunniste')
def link_candidate(election, candidate_id, party_id):
    """Liitä ehdokas puolueeseen"""
    
    # Tarkista että puolue on olemassa ja vahvistettu
    parties_file = f"data/runtime/parties.json"
    if not os.path.exists(parties_file):
        click.echo("❌ Puoluerekisteriä ei ole vielä luotu")
        return
    
    with open(parties_file, 'r') as f:
        parties_data = json.load(f)
    
    party = next((p for p in parties_data["parties"] if p["party_id"] == party_id), None)
    if not party:
        click.echo(f"❌ Puoluetta '{party_id}' ei löydy")
        click.echo("💡 Käytä: python src/cli/manage_parties.py list --election Jumaltenvaalit2026")
        return
    
    if party["registration"]["verification_status"] != "verified":
        click.echo(f"❌ Puolue '{party_id}' ei ole vahvistettu")
        click.echo(f"💡 Tila: {party['registration']['verification_status']}")
        if party["registration"]["verification_status"] == "pending":
            verified_count = len(party["registration"]["verified_by"])
            needed = parties_data["quorum_config"]["min_nodes_for_verification"]
            click.echo(f"💡 Vahvistuksia: {verified_count}/{needed}")
        return
    
    # Tarkista että ehdokas on olemassa
    candidates_file = f"data/runtime/candidates.json"
    if not os.path.exists(candidates_file):
        click.echo("❌ Ehdokasrekisteriä ei ole vielä luotu")
        return
    
    with open(candidates_file, 'r') as f:
        candidates_data = json.load(f)
    
    candidate = next((c for c in candidates_data["candidates"] if c["candidate_id"] == candidate_id), None)
    if not candidate:
        click.echo(f"❌ Ehdokasta '{candidate_id}' ei löydy")
        click.echo("💡 Käytä: python src/cli/manage_candidates.py --election Jumaltenvaalit2026 --add")
        return
    
    # Päivitä ehdokkaan puolue
    old_party = candidate["basic_info"].get("party", "ei puoluetta")
    candidate["basic_info"]["party"] = party_id
    
    # Lisää ehdokas puolueen listalle
    if candidate_id not in party["candidates"]:
        party["candidates"].append(candidate_id)
    
    # Tallenna molemmat tiedostot
    with open(candidates_file, 'w') as f:
        json.dump(candidates_data, f, indent=2)
    
    with open(parties_file, 'w') as f:
        json.dump(parties_data, f, indent=2)
    
    click.echo(f"✅ Ehdokas {candidate_id} liitetty puolueeseen {party_id}")
    click.echo(f"📝 Aiempi puolue: {old_party}")
    click.echo(f"👑 Puolueessa nyt {len(party['candidates'])} ehdokasta")

if __name__ == '__main__':
    link_candidate()
