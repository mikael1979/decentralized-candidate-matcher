#!/usr/bin/env python3
import click
import json
from datetime import datetime
import os
import sys
from pathlib import Path

# LISÄTTY: Lisää src hakemisto Python-polkuun
sys.path.insert(0, str(Path(__file__).parent.parent))

# src/cli/enhanced_party_verification.py
import click
import json
from datetime import datetime

@click.group()
def party_verification():
    """Parannettu puoluevahvistus julkisilla avaimilla"""
    pass

@party_verification.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--name-fi', required=True, help='Puolueen nimi suomeksi')
@click.option('--contact-email', required=True, help='Yhteysemail')
@click.option('--principles', help='Puolueen periaatteet')
def propose_with_keys(election, name_fi, contact_email, principles):
    """Ehdotta uutta puoluetta julkisella avaimella"""
    
    from managers.enhanced_party_manager import EnhancedPartyManager
    
    manager = EnhancedPartyManager(election)
    
    party_data = {
        "name": {
            "fi": name_fi,
            "en": f"[EN] {name_fi}",
            "sv": f"[SV] {name_fi}"
        },
        "description": {
            "fi": f"{name_fi} - puolue",
            "en": f"{name_fi} - party",
            "sv": f"{name_fi} - parti"
        },
        "metadata": {
            "contact_email": contact_email,
            "founding_year": datetime.now().year
        },
        "principles": principles or "Ei periaatteita määritelty"
    }
    
    new_party = manager.propose_party_with_keys(party_data)
    
    click.echo(f"✅ Puolue ehdotettu: {name_fi}")
    click.echo(f"🔑 Julkinen avain luotu: {new_party['crypto_identity']['key_fingerprint']}")
    click.echo("💡 Seuraava vaihe: Julkaise julkisen avaimen tiedote mediassa")
    click.echo("   Käytä: python src/cli/enhanced_party_verification.py publish-media")

@party_verification.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--party-id', required=True, help='Puolueen tunniste')
@click.option('--media-url', required=True, help='Median URL jossa avain julkaistu')
def publish_media(election, party_id, media_url):
    """Rekisteröi mediassa julkaistu julkisen avaimen tiedote"""
    
    from managers.enhanced_party_manager import EnhancedPartyManager
    
    manager = EnhancedPartyManager(election)
    publication_id = manager.publish_public_key_to_media(party_id, media_url)
    
    click.echo(f"✅ Mediajulkaisu rekisteröity: {publication_id}")
    click.echo(f"📰 Media: {media_url}")
    click.echo("💡 Odota nyt että muut nodet vahvistavat julkaisun")

@party_verification.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--party-id', required=True, help='Puolueen tunniste')
@click.option('--publication-id', required=True, help='Julkaisun tunniste')
@click.option('--node-id', required=True, help='Noden tunniste')
def verify_media(election, party_id, publication_id, node_id):
    """Vahvista mediassa julkaistu julkisen avaimen tiedote"""
    
    from managers.enhanced_party_manager import EnhancedPartyManager
    
    manager = EnhancedPartyManager(election)
    
    # Oikeassa järjestelmässä haettaisiin todisteet media-API:sta
    verification_proof = {
        "screenshot_url": "https://example.com/screenshot.jpg",
        "archive_url": "https://archive.org/example",
        "verification_timestamp": datetime.now().isoformat()
    }
    
    success = manager.verify_media_publication(
        party_id, publication_id, node_id, verification_proof
    )
    
    if success:
        click.echo("✅ Mediajulkaisu vahvistettu!")
    else:
        click.echo("❌ Mediajulkaisun vahvistus epäonnistui")

@party_verification.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--party-id', required=True, help='Puolueen tunniste')
@click.option('--node-id', required=True, help='Noden tunniste')
@click.option('--vote', type=click.Choice(['approve', 'reject']), required=True)
@click.option('--node-public-key-file', required=True, help='Noden julkinen avaintiedosto')
def quorum_vote(election, party_id, node_id, vote, node_public_key_file):
    """Äänestä puolueen hyväksymisestä kvoorumissa"""
    
    from managers.enhanced_party_manager import EnhancedPartyManager
    
    # Lataa noden julkinen avain
    with open(node_public_key_file, 'r') as f:
        node_public_key = f.read()
    
    manager = EnhancedPartyManager(election)
    success = manager.vote_on_party_verification(
        party_id, node_id, vote, node_public_key
    )
    
    if success:
        click.echo(f"✅ Ääni annettu: {vote}")
        click.echo("🎉 Puolue VAHVISTETTU kvoorumin toimesta!")
    else:
        click.echo(f"✅ Ääni annettu: {vote}")
        click.echo("⏳ Odotetaan lisää ääniä...")
