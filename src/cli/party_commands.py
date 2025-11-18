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
Puolueiden peruskomentojen hallinta - UUSI MODULAARINEN
"""
import click
import json
from datetime import datetime
from pathlib import Path
from typing import Dict

# KORJATTU: Käytetään yhteisiä file_utils-funktioita
try:
    from core.file_utils import read_json_file, write_json_file, ensure_directory
    from core.validators import DataValidator, validate_party_id
except ImportError:
    from core.file_utils import read_json_file, write_json_file, ensure_directory
    from core.validators import DataValidator, validate_party_id

class PartyCommands:
    """Puolueiden peruskomentojen hallinta"""
    
    def __init__(self, election_id: str):
        self.election_id = election_id
        self.parties_file = f"data/runtime/parties.json"
        ensure_directory("data/runtime")
    
    def propose_party(self, name_fi: str, name_en: str = None, name_sv: str = None,
                     description_fi: str = None, email: str = None, website: str = None, 
                     founding_year: str = "2024") -> bool:
        """Ehdotta uutta puoluetta"""
        
        # Validoi syötteet
        if not name_fi:
            click.echo("❌ Puolueen nimi (suomeksi) on pakollinen")
            return False
        
        if email and not DataValidator.validate_email(email):
            click.echo("❌ Virheellinen sähköpostiosoite")
            return False
        
        if website and not DataValidator.validate_url(website):
            click.echo("❌ Virheellinen URL-osoite")
            return False
        
        # Lataa nykyiset puolueet
        if Path(self.parties_file).exists():
            try:
                data = read_json_file(self.parties_file, {"parties": []})
            except Exception as e:
                click.echo(f"❌ Puoluerekisterin lukuvirhe: {e}")
                return False
        else:
            # Luo uusi puoluerekisteri
            data = {
                "metadata": {
                    "version": "1.0.0",
                    "created": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "election_id": self.election_id,
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
            return False
        
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
                "proposed_by": "system",
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
        try:
            write_json_file(self.parties_file, data)
            click.echo(f"✅ Puolue ehdotettu: {name_fi} ({party_id})")
            click.echo(f"📋 Tila: Odottaa vahvistusta ({data['quorum_config']['min_nodes_for_verification']} nodelta)")
            return True
        except Exception as e:
            click.echo(f"❌ Puolueen tallennus epäonnistui: {e}")
            return False
    
    def list_parties(self, show_pending: bool = False, show_rejected: bool = False) -> bool:
        """Listaa puolueet"""
        
        if not Path(self.parties_file).exists():
            click.echo("❌ Puoluerekisteriä ei ole vielä luotu")
            click.echo("💡 Käytä: python src/cli/manage_parties.py propose --election Jumaltenvaalit2026 --name-fi 'Nimi'")
            return False
        
        try:
            data = read_json_file(self.parties_file, {"parties": []})
        except Exception as e:
            click.echo(f"❌ Puoluerekisterin lukuvirhe: {e}")
            return False
        
        click.echo("🏛️  REKISTERÖIDYT PUOLUEET")
        click.echo("=" * 60)
        
        verified_parties = [p for p in data.get("parties", []) if p["registration"]["verification_status"] == "verified"]
        pending_parties = [p for p in data.get("parties", []) if p["registration"]["verification_status"] == "pending"]
        rejected_parties = [p for p in data.get("parties", []) if p["registration"]["verification_status"] == "rejected"]
        
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
        
        return True
    
    def get_party_info(self, party_id: str) -> bool:
        """Näytä yksittäisen puolueen tiedot"""
        
        if not validate_party_id(party_id):
            click.echo(f"❌ Virheellinen puolue ID: {party_id}")
            return False
        
        if not Path(self.parties_file).exists():
            click.echo("❌ Puoluerekisteriä ei ole vielä luotu")
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
        
        return True
