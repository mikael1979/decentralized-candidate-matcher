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
import os

@click.command()
@click.option('--election', required=True, help='Vaalin tunniste')
def party_stats(election):
    """Näytä puolueiden tilastot"""
    
    parties_file = f"data/runtime/parties.json"
    candidates_file = f"data/runtime/candidates.json"
    
    if not os.path.exists(parties_file):
        click.echo("❌ Puoluerekisteriä ei löydy")
        return
    
    with open(parties_file, 'r') as f:
        parties_data = json.load(f)
    
    # Lataa ehdokkaat jos saatavilla
    candidates_data = {}
    if os.path.exists(candidates_file):
        with open(candidates_file, 'r') as f:
            candidates_data = json.load(f)
    
    click.echo("📊 PUOLUETILASTOT")
    click.echo("=" * 50)
    
    verified_parties = [p for p in parties_data["parties"] if p["registration"]["verification_status"] == "verified"]
    
    if not verified_parties:
        click.echo("❌ Ei vahvistettuja puolueita")
        return
    
    for party in verified_parties:
        click.echo(f"🏛️  {party['name']['fi']} ({party['party_id']})")
        click.echo(f"   📧 {party['metadata'].get('contact_email', 'Ei sähköpostia')}")
        click.echo(f"   🌐 {party['metadata'].get('website', 'Ei verkkosivua')}")
        click.echo(f"   👑 Ehdokkaita: {len(party['candidates'])}")
        
        # Näytä ehdokkaat
        if candidates_data and "candidates" in candidates_data:
            party_candidates = [c for c in candidates_data["candidates"] if c["candidate_id"] in party["candidates"]]
            for cand in party_candidates:
                click.echo(f"     • {cand['basic_info']['name']['fi']}")
        
        click.echo()

if __name__ == '__main__':
    party_stats()
