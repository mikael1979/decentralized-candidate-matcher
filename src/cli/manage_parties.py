#!/usr/bin/env python3
import click
import json
import sys
import os
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

@click.group()
def manage_parties():
    """Puolueiden hajautettu hallinta"""
    pass

@manage_parties.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--name-fi', required=True, help='Puolueen nimi suomeksi')
@click.option('--name-en', help='Puolueen nimi englanniksi')
@click.option('--name-sv', help='Puolueen nimi ruotsiksi')
@click.option('--description-fi', help='Puolueen kuvaus suomeksi')
@click.option('--email', help='Yhteysemail')
@click.option('--website', help='Verkkosivusto')
@click.option('--founding-year', default='2024', help='Perustamisvuosi')
def propose(election, name_fi, name_en, name_sv, description_fi, email, website, founding_year):
    """Ehdotta uutta puoluetta"""
    
    # Lataa nykyiset puolueet
    parties_file = f"data/runtime/parties.json"
    if os.path.exists(parties_file):
        with open(parties_file, 'r') as f:
            data = json.load(f)
    else:
        # Luo uusi puoluerekisteri base templatesta
        data = {
            "metadata": {
                "version": "1.0.0",
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "election_id": election,
                "description": {
                    "fi": "Puolueiden hajautettu rekisteri",
                    "en": "Decentralized party registry",
                    "sv": "Decentraliserat partiregister"
                }
            },
            "quorum_config": {
                "min_nodes_for_verification": 3,
                "approval_threshold_percent": 60,
                "verification_timeout_hours": 24,
                "rejection_quorum_percent": 40
            },
            "parties": [],
            "verification_history": []
        }
    
    # Tarkista onko puoluetta jo olemassa
    existing_party = next((p for p in data["parties"] if p["name"]["fi"].lower() == name_fi.lower()), None)
    if existing_party:
        click.echo(f"❌ Puolue '{name_fi}' on jo olemassa! (ID: {existing_party['party_id']})")
        return
    
    # Luo uusi puolue
    party_id = f"party_{len(data['parties']) + 1:03d}"
    new_party = {
        "party_id": party_id,
        "name": {
            "fi": name_fi,
            "en": name_en or f"[EN] {name_fi}",
            "sv": name_sv or f"[SV] {name_fi}"
        },
        "description": {
            "fi": description_fi or f"{name_fi} - puolue",
            "en": description_fi or f"{name_fi} - party", 
            "sv": description_fi or f"{name_fi} - parti"
        },
        "registration": {
            "proposed_by": "system",  # Aluksi järjestelmä, nodet korvaavat
            "proposed_at": datetime.now().isoformat(),
            "verification_status": "pending",
            "verified_by": [],
            "verification_timestamp": None,
            "rejection_reason": None
        },
        "candidates": [],
        "metadata": {
            "official_registration": False,
            "contact_email": email,
            "website": website,
            "founding_year": founding_year
        }
    }
    
    data["parties"].append(new_party)
    data["metadata"]["last_updated"] = datetime.now().isoformat()
    
    # Lisää historiaan
    data["verification_history"].append({
        "party_id": party_id,
        "timestamp": datetime.now().isoformat(),
        "action": "proposed",
        "by_node": "system",
        "reason": "Uusi puolue ehdotettu"
    })
    
    # Tallenna
    os.makedirs(os.path.dirname(parties_file), exist_ok=True)
    with open(parties_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    click.echo(f"✅ Puolue ehdotettu: {name_fi} ({party_id})")
    click.echo(f"📋 Tila: Odottaa vahvistusta ({data['quorum_config']['min_nodes_for_verification']} nodelta)")

@manage_parties.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--show-pending', is_flag=True, help='Näytä myös odottavat puolueet')
@click.option('--show-rejected', is_flag=True, help='Näytä myös hylätyt puolueet')
def list(election, show_pending, show_rejected):
    """Listaa kaikki puolueet"""
    
    parties_file = f"data/runtime/parties.json"
    if not os.path.exists(parties_file):
        click.echo("❌ Puoluerekisteriä ei ole vielä luotu")
        click.echo("💡 Käytä: python src/cli/manage_parties.py propose --election Jumaltenvaalit2026 --name-fi 'Nimi'")
        return
    
    with open(parties_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    click.echo("🏛️  REKISTERÖIDYT PUOLUEET")
    click.echo("=" * 60)
    
    verified_parties = [p for p in data["parties"] if p["registration"]["verification_status"] == "verified"]
    pending_parties = [p for p in data["parties"] if p["registration"]["verification_status"] == "pending"]
    rejected_parties = [p for p in data["parties"] if p["registration"]["verification_status"] == "rejected"]
    
    # Näytä vahvistetut puolueet
    if verified_parties:
        click.echo("\n✅ VAHVISTETUT PUOLUEET:")
        for party in verified_parties:
            click.echo(f"  🏛️  {party['name']['fi']} ({party['party_id']})")
            click.echo(f"     📧 {party['metadata'].get('contact_email', 'Ei sähköpostia')}")
            click.echo(f"     👑 Ehdokkaita: {len(party['candidates'])}")
            click.echo(f"     🕒 Vahvistettu: {party['registration']['verification_timestamp'][:16]}")
            click.echo(f"     ✅ Vahvistajat: {', '.join(party['registration']['verified_by'])}")
    
    # Näytä odottavat puolueet
    if pending_parties and show_pending:
        click.echo("\n⏳ ODOTTAA VAHVISTUSTA:")
        for party in pending_parties:
            verified_count = len(party["registration"]["verified_by"])
            needed = data["quorum_config"]["min_nodes_for_verification"]
            click.echo(f"  ⏳ {party['name']['fi']} ({party['party_id']})")
            click.echo(f"     📧 {party['metadata'].get('contact_email', 'Ei sähköpostia')}")
            click.echo(f"     👑 Ehdokkaita: {len(party['candidates'])}")
            click.echo(f"     ✅ Vahvistuksia: {verified_count}/{needed}")
    
    elif pending_parties:
        click.echo(f"\n⏳ {len(pending_parties)} puoluetta odottaa vahvistusta")
        click.echo("💡 Näytä kaikki: --show-pending")
    
    # Näytä hylätyt puolueet
    if rejected_parties and show_rejected:
        click.echo("\n❌ HYLÄTYT PUOLUEET:")
        for party in rejected_parties:
            click.echo(f"  ❌ {party['name']['fi']} ({party['party_id']})")
            click.echo(f"     📧 {party['metadata'].get('contact_email', 'Ei sähköpostia')}")
            click.echo(f"     💬 Syy: {party['registration']['rejection_reason']}")
    
    elif rejected_parties:
        click.echo(f"\n❌ {len(rejected_parties)} puoluetta hylätty")
        click.echo("💡 Näytä kaikki: --show-rejected")
    
    if not verified_parties and not pending_parties and not rejected_parties:
        click.echo("❌ Ei puolueita rekisterissä")

@manage_parties.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--party-id', required=True, help='Puolueen tunniste')
@click.option('--node-id', required=True, help='Vahvistavan noden tunniste')
@click.option('--verify', is_flag=True, help='Vahvista puolue')
@click.option('--reject', is_flag=True, help='Hylkää puolue')
@click.option('--reason', help='Syy vahvistukseen/hylkäämiseen')
def verify(election, party_id, node_id, verify, reject, reason):
    """Vahvista tai hylkää puolue"""
    
    if verify and reject:
        click.echo("❌ Valitse joko --verify tai --reject, ei molempia")
        return
    
    if not verify and not reject:
        click.echo("❌ Valitse joko --verify tai --reject")
        return
    
    parties_file = f"data/runtime/parties.json"
    if not os.path.exists(parties_file):
        click.echo("❌ Puoluerekisteriä ei ole vielä luotu")
        return
    
    with open(parties_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Etsi puolue
    party = next((p for p in data["parties"] if p["party_id"] == party_id), None)
    if not party:
        click.echo(f"❌ Puoluetta '{party_id}' ei löydy")
        click.echo("💡 Käytä: python src/cli/manage_parties.py list --election Jumaltenvaalit2026")
        return
    
    # Tarkista että node_id on annettu
    if not node_id:
        click.echo("❌ Anna --node-id parametri")
        return
    
    if verify:
        # Tarkista onko jo vahvistettu
        if party["registration"]["verification_status"] == "verified":
            click.echo("❌ Puolue on jo vahvistettu")
            return
        
        # Tarkista onko jo vahvistanut
        if node_id in party["registration"]["verified_by"]:
            click.echo("❌ Olet jo vahvistanut tämän puolueen")
            return
        
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
        
    else:  # reject
        if party["registration"]["verification_status"] == "rejected":
            click.echo("❌ Puolue on jo hylätty")
            return
            
        party["registration"]["verification_status"] = "rejected"
        party["registration"]["rejection_reason"] = reason or "Ei syytä annettu"
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
        "reason": reason or "Ei syytä annettu"
    })
    
    # Tallenna
    with open(parties_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    click.echo(message)

@manage_parties.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--party-id', required=True, help='Puolueen tunniste')
def info(election, party_id):
    """Näytä yksittäisen puolueen tiedot"""
    
    parties_file = f"data/runtime/parties.json"
    if not os.path.exists(parties_file):
        click.echo("❌ Puoluerekisteriä ei ole vielä luotu")
        return
    
    with open(parties_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Etsi puolue
    party = next((p for p in data["parties"] if p["party_id"] == party_id), None)
    if not party:
        click.echo(f"❌ Puoluetta '{party_id}' ei löydy")
        return
    
    click.echo(f"🏛️  PUOLUETIEDOT: {party['name']['fi']}")
    click.echo("=" * 50)
    
    # Perustiedot
    click.echo(f"📛 Nimi:")
    click.echo(f"   🇫🇮 {party['name']['fi']}")
    click.echo(f"   🇬🇧 {party['name']['en']}")
    click.echo(f"   🇸🇪 {party['name']['sv']}")
    
    click.echo(f"📝 Kuvaus:")
    click.echo(f"   🇫🇮 {party['description']['fi']}")
    click.echo(f"   🇬🇧 {party['description']['en']}")
    click.echo(f"   🇸🇪 {party['description']['sv']}")
    
    # Yhteystiedot
    click.echo(f"📧 Yhteystiedot:")
    click.echo(f"   Sähköposti: {party['metadata'].get('contact_email', 'Ei asetettu')}")
    click.echo(f"   Verkkosivu: {party['metadata'].get('website', 'Ei asetettu')}")
    click.echo(f"   Perustamisvuosi: {party['metadata'].get('founding_year', 'Ei asetettu')}")
    
    # Rekisteröintitiedot
    status = party["registration"]["verification_status"]
    status_icon = "✅" if status == "verified" else "⏳" if status == "pending" else "❌"
    
    click.echo(f"📋 Rekisteröinti:")
    click.echo(f"   Tila: {status_icon} {status}")
    click.echo(f"   Ehdotettu: {party['registration']['proposed_at'][:16]}")
    click.echo(f"   Ehdottaja: {party['registration']['proposed_by']}")
    
    if status == "verified":
        click.echo(f"   Vahvistettu: {party['registration']['verification_timestamp'][:16]}")
        click.echo(f"   Vahvistajat: {', '.join(party['registration']['verified_by'])}")
    elif status == "rejected":
        click.echo(f"   Hylkäyssyyt: {party['registration']['rejection_reason']}")
    else:  # pending
        verified_count = len(party["registration"]["verified_by"])
        needed = data["quorum_config"]["min_nodes_for_verification"]
        click.echo(f"   Vahvistuksia: {verified_count}/{needed}")
        if party["registration"]["verified_by"]:
            click.echo(f"   Vahvistaneet: {', '.join(party['registration']['verified_by'])}")
    
    # Ehdokkaat
    click.echo(f"👑 Ehdokkaat ({len(party['candidates'])}):")
    if party["candidates"]:
        for cand_id in party["candidates"]:
            click.echo(f"   • {cand_id}")
    else:
        click.echo("   Ei ehdokkaita")

@manage_parties.command()
@click.option('--election', required=True, help='Vaalin tunniste')
def stats(election):
    """Näytä puolueiden tilastot"""
    
    parties_file = f"data/runtime/parties.json"
    if not os.path.exists(parties_file):
        click.echo("❌ Puoluerekisteriä ei ole vielä luotu")
        return
    
    with open(parties_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    click.echo("📊 PUOLUETILASTOT")
    click.echo("=" * 50)
    
    total_parties = len(data["parties"])
    verified_parties = [p for p in data["parties"] if p["registration"]["verification_status"] == "verified"]
    pending_parties = [p for p in data["parties"] if p["registration"]["verification_status"] == "pending"]
    rejected_parties = [p for p in data["parties"] if p["registration"]["verification_status"] == "rejected"]
    
    click.echo(f"🏛️  Puolueita yhteensä: {total_parties}")
    click.echo(f"✅  Vahvistettuja: {len(verified_parties)}")
    click.echo(f"⏳  Odottaa vahvistusta: {len(pending_parties)}")
    click.echo(f"❌  Hylättyjä: {len(rejected_parties)}")
    
    # Ehdokastilastot
    total_candidates = sum(len(p["candidates"]) for p in data["parties"])
    click.echo(f"👑  Ehdokkaita yhteensä: {total_candidates}")
    
    if verified_parties:
        click.echo(f"📈  Keskimäärin ehdokkaita/vahvistettu puolue: {total_candidates/len(verified_parties):.1f}")
    
    # Kvoorumitilanne
    click.echo(f"🔢  Vahvistus kvoorumi: {data['quorum_config']['min_nodes_for_verification']} nodea")
    
    # Viimeisimmät tapahtumat
    click.echo(f"\n📜 Viimeisimmät tapahtumat:")
    recent_events = data["verification_history"][-5:]
    for event in reversed(recent_events):
        action_icon = "✅" if event["action"] == "verified" else "❌" if event["action"] == "rejected" else "📝"
        click.echo(f"   {action_icon} {event['timestamp'][11:16]} - {event['party_id']}: {event['action']} ({event['by_node']})")

@manage_parties.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--party-id', required=True, help='Puolueen tunniste')
@click.confirmation_option(prompt='Haluatko varmasti poistaa tämän puolueen?')
def remove(election, party_id):
    """Poista puolue rekisteristä"""
    
    parties_file = f"data/runtime/parties.json"
    if not os.path.exists(parties_file):
        click.echo("❌ Puoluerekisteriä ei ole vielä luotu")
        return
    
    with open(parties_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Etsi puolue
    party_index = next((i for i, p in enumerate(data["parties"]) if p["party_id"] == party_id), None)
    if party_index is None:
        click.echo(f"❌ Puoluetta '{party_id}' ei löydy")
        return
    
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
    with open(parties_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    click.echo(f"✅ Puolue poistettu: {removed_party['name']['fi']} ({party_id})")
    click.echo(f"📝 Puolueessa oli {len(removed_party['candidates'])} ehdokasta")

if __name__ == '__main__':
    manage_parties()
