#!/usr/bin/env python3
import click
import json
from datetime import datetime
import os
from pathlib import Path

# KORJATTU: Käytetään yhteisiä file_utils-funktioita
try:
    from src.core.file_utils import read_json_file, write_json_file, ensure_directory
except ImportError:
    from core.file_utils import read_json_file, write_json_file, ensure_directory

@click.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--add', is_flag=True, help='Lisää uusi ehdokas')
@click.option('--name', help='Ehdokkaan nimi')
@click.option('--party', help='Puolue')
@click.option('--list', 'list_candidates', is_flag=True, help='Listaa kaikki ehdokkaat')
def manage_candidates(election, add, name, party, list_candidates):
    """Hallinnoi vaaliehdokkaita"""
    
    candidates_file = f"data/runtime/candidates.json"
    
    if add:
        if not name:
            click.echo("❌ Anna --name")
            return
        
        # KORJATTU: Varmistetaan hakemisto
        ensure_directory("data/runtime")
        
        # Lataa nykyiset ehdokkaat
        if os.path.exists(candidates_file):
            try:
                data = read_json_file(candidates_file, {"candidates": []})
            except Exception as e:
                click.echo(f"❌ Ehdokasrekisterin lukuvirhe: {e}")
                return
        else:
            data = {
                "candidates": [], 
                "metadata": {
                    "election_id": election,
                    "created": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat()
                }
            }
        
        # Tarkista onko ehdokas jo olemassa
        existing_candidate = next(
            (c for c in data["candidates"] 
             if c["basic_info"]["name"]["fi"].lower() == name.lower()),
            None
        )
        
        if existing_candidate:
            click.echo(f"❌ Ehdokas '{name}' on jo olemassa! (ID: {existing_candidate['candidate_id']})")
            return
        
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
            "answers": [],
            "metadata": {
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
        }
        
        data["candidates"].append(new_candidate)
        data["metadata"]["last_updated"] = datetime.now().isoformat()
        
        # Tallenna
        try:
            write_json_file(candidates_file, data)
            click.echo(f"✅ Ehdokas lisätty: {name}")
            click.echo(f"👑 Ehdokkaita yhteensä: {len(data['candidates'])}")
            click.echo(f"🆔 Ehdokas ID: {new_candidate['candidate_id']}")
        except Exception as e:
            click.echo(f"❌ Ehdokkaan tallennus epäonnistui: {e}")
    
    elif list_candidates:
        # Listaa ehdokkaat
        if not os.path.exists(candidates_file):
            click.echo("❌ Ehdokasrekisteriä ei ole vielä luotu")
            return
        
        try:
            data = read_json_file(candidates_file, {"candidates": []})
        except Exception as e:
            click.echo(f"❌ Ehdokasrekisterin lukuvirhe: {e}")
            return
        
        click.echo("👑 REKISTERÖIDYT EHDOKKAAT")
        click.echo("=" * 50)
        
        if not data.get("candidates"):
            click.echo("❌ Ei ehdokkaita")
            return
        
        for candidate in data["candidates"]:
            click.echo(f"🏛️  {candidate['basic_info']['name']['fi']} ({candidate['candidate_id']})")
            click.echo(f"   📋 Puolue: {candidate['basic_info'].get('party', 'Sitoutumaton')}")
            click.echo(f"   📝 Vastauksia: {len(candidate.get('answers', []))}")
            click.echo()
    
    else:
        click.echo("💡 Käytä --add lisätäksesi ehdokkaan tai --list listataksesi ehdokkaat")

if __name__ == '__main__':
    manage_candidates()
