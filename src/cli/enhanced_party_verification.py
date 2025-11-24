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
@click.option('--enable-taq-bonus', is_flag=True, help='Ota käyttöön TAQ media-bonus')
def publish_media(election, party_id, media_url, enable_taq_bonus):
    """Rekisteröi mediassa julkaistu julkisen avaimen tiedote - Laajennettu TAQ:lla"""
    
    from managers.enhanced_party_manager import EnhancedPartyManager
    
    # KORJATTU: Lataa puolueen tiedot ensin
    manager = EnhancedPartyManager(election)
    
    # SIMULOIDAAN puolueen data - oikeassa järjestelmässä haettaisiin tietokannasta
    party_data = {
        "party_id": party_id,
        "name": {"fi": f"Testipuolue {party_id}"},
        "crypto_identity": {
            "key_fingerprint": f"fp_{party_id}_12345"
        },
        "media_publications": []
    }
    
    # NYKYINEN TOIMINTA (aina)
    publication = manager.publish_party_key_to_media(party_data, media_url)
    
    # UUSI TAQ-BONUS (opt-in)
    taq_bonus_info = {}
    if enable_taq_bonus:
        click.echo("🔍 Tarkistetaan TAQ media-bonusta...")
        taq_bonus = manager.get_taq_media_bonus(party_data)
        
        if taq_bonus:
            taq_bonus_info = {
                "taq_enabled": True,
                "trust_level": taq_bonus.get("trust_level", "unknown"),
                "time_saving": taq_bonus.get("time_saving", "0%"),
                "required_approvals": taq_bonus.get("required_approvals", 3),  # KORJATTU
                "source_type": taq_bonus.get("source_type", "unknown")
            }
            click.echo("✅ TAQ bonus saatavilla!")
        else:
            click.echo("ℹ️  TAQ bonus ei saatavilla tälle medialle")
    
    click.echo(f"✅ Mediajulkaisu rekisteröity: {publication['publication_id']}")
    click.echo(f"📰 Media: {media_url}")
    click.echo(f"🏷️  Domain: {publication['media_domain']}")
    click.echo(f"⭐ Luotettavuuspisteet: {publication['trust_score']}/10")
    
    if taq_bonus_info:
        click.echo("\n🚀 TAQ MEDIA-BONUS AKTIIVINEN!")
        click.echo(f"   📊 Lähdetyyppi: {taq_bonus_info['source_type']}")
        click.echo(f"   📈 Luotettavuustaso: {taq_bonus_info['trust_level']}")
        click.echo(f"   ⚡ Nopeutus: {taq_bonus_info['time_saving']}")
        click.echo(f"   👥 Vaaditut vahvistukset: {taq_bonus_info['required_approvals']}/3")
        click.echo("   💡 Vahvistusprosessi nopeutuu automaattisesti!")
    elif enable_taq_bonus:
        click.echo("\n💡 Media ei ole TAQ-luotettujen lähteiden listalla")
        click.echo("   Käytä luotettua mediaa (esim. Yle, HS, BBC) saadaksesi bonuksen!")
    else:
        click.echo("\n💡 Vinkki: Käytä --enable-taq-bonus nopeuttaaksesi vahvistusta!")
    
    click.echo("\n⏳ Odota nyt että muut nodet vahvistavat julkaisun")

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

if __name__ == '__main__':
    party_verification()
