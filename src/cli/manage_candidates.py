#!/usr/bin/env python3
import click
import json
from datetime import datetime
import os

@click.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--add', is_flag=True, help='Lisää uusi ehdokas')
@click.option('--name', help='Ehdokkaan nimi')
@click.option('--party', help='Puolue')
def manage_candidates(election, add, name, party):
    """Hallinnoi vaaliehdokkaita"""
    
    if add:
        if not name:
            click.echo("❌ Anna --name")
            return
        
        # Lataa nykyiset ehdokkaat
        candidates_file = f"data/runtime/candidates.json"
        if os.path.exists(candidates_file):
            with open(candidates_file, 'r') as f:
                data = json.load(f)
        else:
            data = {"candidates": [], "metadata": {"election_id": election}}
        
        # Lisää uusi ehdokas
        new_candidate = {
            "candidate_id": f"cand_{len(data['candidates']) + 1}",
            "basic_info": {
                "name": {
                    "fi": name,
                    "en": f"[EN] {name}",
                    "sv": f"[SV] {name}"
                },
                "party": party or "sitoutumaton",
                "domain": "divine_power"  # Jumaltenvaalien erikoisala
            },
            "answers": []
        }
        
        data["candidates"].append(new_candidate)
        
        # Tallenna
        with open(candidates_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        click.echo(f"✅ Ehdokas lisätty: {name}")
        click.echo(f"👑 Ehdokkaita yhteensä: {len(data['candidates'])}")

if __name__ == '__main__':
    manage_candidates()
