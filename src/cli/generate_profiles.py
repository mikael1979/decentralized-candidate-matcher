#!/usr/bin/env python3
"""
CLI-työkalu profiilisivujen generointiin ja IPFS-julkaisuun
"""
import json
import os
import click
from pathlib import Path
from typing import Dict, List, Optional

# Lisää projektin juurihakemisto Python-polkuun
import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))



def load_parties() -> List[Dict]:
    """Lataa puolueet JSON-tiedostosta"""
    parties_file = Path("data/runtime/parties.json")
    if parties_file.exists():
        with open(parties_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("parties", [])
    return []

def load_candidates() -> List[Dict]:
    """Lataa ehdokkaat JSON-tiedostosta"""
    candidates_file = Path("data/runtime/candidates.json")
    if candidates_file.exists():
        with open(candidates_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("candidates", [])
    return []

def load_theme(theme_name: str) -> Optional[Dict]:
    """Lataa väriteema"""
    return CSSGenerator.get_color_themes().get(theme_name)

@click.group()
def profile_generator():
    """Profiilisivujen generointi- ja julkaisutyökalu"""
    pass

@profile_generator.command()
def list_themes():
    """Listaa kaikki saatavilla olevat väriteemat"""
    click.echo("✅ Käytettävissä olevat teemat:")
    for theme_name in CSSGenerator.get_color_themes().keys():
        click.echo(f"- {theme_name}")

@profile_generator.command()
@click.option('--party-id', help='Yksittäisen puolueen ID')
@click.option('--all-parties', is_flag=True, help='Generoi kaikkien puolueiden profiilit')
@click.option('--theme', default='default', help='Väriteeman nimi')
def generate_party_profiles(party_id, all_parties, theme):
    """Generoi puolueiden profiilit HTML-muodossa"""
    generator = HTMLProfileGenerator()
    
    # Hae väriteema
    colors = load_theme(theme)
    if not colors:
        click.echo(f"❌ Teemaa '{theme}' ei löytynyt")
        return
    
    if all_parties:
        # Generoi kaikkien puolueiden profiilit
        parties = load_parties()
        for party in parties:
            # Käytä generate_and_publish_party_profile metodia
            metadata = generator.generate_and_publish_party_profile(party, custom_colors=colors)
            click.echo(f"   ✅ {party['name']['fi']}: {metadata['ipfs_cid']}")
            
    elif party_id:
        # Generoi yhden puolueen profiili
        party = next((p for p in load_parties() if p['party_id'] == party_id), None)
        if party:
            metadata = generator.generate_and_publish_party_profile(party, custom_colors=colors)
            click.echo(f"   ✅ {party['name']['fi']}: {metadata['ipfs_cid']}")
        else:
            click.echo(f"❌ Puoluetta ID:llä '{party_id}' ei löytynyt")
    else:
        click.echo("❌ Valitse joko --party-id tai --all-parties")

@profile_generator.command()
@click.option('--candidate-id', help='Yksittäisen ehdokkaan ID')
@click.option('--all-candidates', is_flag=True, help='Generoi kaikkien ehdokkaiden profiilit')
@click.option('--theme', default='default', help='Väriteeman nimi')
def generate_candidate_profiles(candidate_id, all_candidates, theme):
    """Generoi ehdokkaiden profiilit HTML-muodossa"""
    generator = HTMLProfileGenerator()
    
    # Hae väriteema
    colors = load_theme(theme)
    if not colors:
        click.echo(f"❌ Teemaa '{theme}' ei löytynyt")
        return
    
    # Lataa puolueet ehdokkaiden yhteyttä varten
    parties = {p['party_id']: p for p in load_parties()}
    
    if all_candidates:
        # Generoi kaikkien ehdokkaiden profiilit
        candidates = load_candidates()
        for candidate in candidates:
            party_data = parties.get(candidate['basic_info'].get('party'))
            metadata = generator.generate_and_publish_candidate_profile(
                candidate, party_data, custom_colors=colors
            )
            click.echo(f"   ✅ {candidate['basic_info']['name']['fi']}: {metadata['ipfs_cid']}")
            
    elif candidate_id:
        # Generoi yhden ehdokkaan profiili
        candidate = next((c for c in load_candidates() if c['candidate_id'] == candidate_id), None)
        if candidate:
            party_data = parties.get(candidate['basic_info'].get('party'))
            metadata = generator.generate_and_publish_candidate_profile(
                candidate, party_data, custom_colors=colors
            )
            click.echo(f"   ✅ {candidate['basic_info']['name']['fi']}: {metadata['ipfs_cid']}")
        else:
            click.echo(f"❌ Ehdokasta ID:llä '{candidate_id}' ei löytynyt")
    else:
        click.echo("❌ Valitse joko --candidate-id tai --all-candidates")

@profile_generator.command()
@click.option('--election', default='Jumaltenvaalit2026', help='Vaalin tunniste')
def publish_all_to_ipfs(election):
    """Generoi ja julkaise kaikki profiilit IPFS:ään"""
    generator = HTMLProfileGenerator(election_id=election)
    
    click.echo("🚀 GENEROIDAAN JA JULKAISTAAN KAIKKI PROFIILIT IPFS:ÄÄN")
    click.echo("=" * 50)
    
    # Lataa data
    parties = load_parties()
    candidates = load_candidates()
    party_map = {p['party_id']: p for p in parties}
    
    # Julkaise puolueet
    click.echo(f"📄 Julkaistaan {len(parties)} puoluetta...")
    party_metadata = []
    for party in parties:
        metadata = generator.generate_and_publish_party_profile(party)
        party_metadata.append(metadata)
        click.echo(f"   ✅ {party['name']['fi']}: {metadata['ipfs_cid']}")
    
    # Julkaise ehdokkaat
    click.echo(f"👑 Julkaistaan {len(candidates)} ehdokasta...")
    candidate_metadata = []
    for candidate in candidates:
        party_data = party_map.get(candidate['basic_info'].get('party'))
        metadata = generator.generate_and_publish_candidate_profile(candidate, party_data)
        candidate_metadata.append(metadata)
        click.echo(f"   ✅ {candidate['basic_info']['name']['fi']}: {metadata['ipfs_cid']}")
    
    # Generoi base.json
    base_file = generator.save_base_json()
    click.echo(f"📊 base.json generoitu: {base_file}")
    
    click.echo("🎉 KAIKKI PROFIILIT JULKAISTU IPFS:ÄÄN!")

@profile_generator.command()
@click.option('--election', default='Jumaltenvaalit2026', help='Vaalin tunniste')
def generate_base_json(election):
    """Generoi base.json tiedosto kaikista resursseista"""
    generator = HTMLProfileGenerator(election_id=election)
    base_file = generator.save_base_json()
    click.echo(f"✅ base.json tallennettu: {base_file}")

@profile_generator.command()
@click.option('--election', default='Jumaltenvaalit2026', help='Vaalin tunniste')
def status(election):
    """Näytä profiilien nykyinen tila"""
    generator = HTMLProfileGenerator(election_id=election)
    base_data = generator.get_base_json()
    
    stats = base_data['statistics']
    click.echo(f"📊 Profiilien tila: {stats['total_profiles']} profiilia, "
               f"{stats['party_profiles']} puoluetta, "
               f"{stats['candidate_profiles']} ehdokasta")
    
    # Näytä viimeisimmät profiilit
    profiles = base_data['profiles']
    if profiles:
        click.echo("📋 Viimeisimmät profiilit:")
        for profile_id, profile in list(profiles.items())[-5:]:  # Viimeiset 5
            click.echo(f"  • {profile['entity_name']} ({profile['entity_type']}) - {profile['ipfs_cid']}")

if __name__ == '__main__':
    profile_generator()
