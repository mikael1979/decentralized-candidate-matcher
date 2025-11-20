#!/usr/bin/env python3
import click
import json
from datetime import datetime
import os
import sys
import uuid
from pathlib import Path

# LISÄTTY: Lisää src hakemisto Python-polkuun
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config_manager import get_election_id, get_data_path
from core.file_utils import read_json_file, write_json_file, ensure_directory

# KORJATTU: Tarkista ensin jos data_validator on saatavilla
try:
    from core.data_validator import validate_candidate_uniqueness, get_candidate_by_id_or_name
except ImportError:
    # Fallback jos data_validator ei ole saatavilla
    def validate_candidate_uniqueness(candidates_file, new_candidate_name):
        """Yksinkertainen validointi jos data_validator puuttuu"""
        if not os.path.exists(candidates_file):
            return True
        
        try:
            data = read_json_file(candidates_file, {"candidates": []})
            existing_names = [
                c["basic_info"]["name"]["fi"].lower().strip() 
                for c in data.get("candidates", [])
                if "basic_info" in c and "name" in c["basic_info"] and "fi" in c["basic_info"]["name"]
            ]
            return new_candidate_name.lower().strip() not in existing_names
        except Exception:
            return True
    
    def get_candidate_by_id_or_name(candidates_file, identifier):
        """Yksinkertainen haku jos data_validator puuttuu"""
        if not os.path.exists(candidates_file):
            return None
        
        try:
            data = read_json_file(candidates_file, {"candidates": []})
            for candidate in data.get("candidates", []):
                if (candidate.get("id") == identifier or 
                    candidate.get("basic_info", {}).get("name", {}).get("fi") == identifier or
                    candidate.get("basic_info", {}).get("name", {}).get("en") == identifier):
                    return candidate
            return None
        except Exception:
            return None


class CandidateManager:
    """Ehdokkaiden hallinta config-järjestelmän kanssa"""
    
    def __init__(self, election_id=None):
        self.election_id = election_id or get_election_id()
        self.data_path = get_data_path(self.election_id)
        self.candidates_file = Path(self.data_path) / "candidates.json"
    
    def load_candidates(self):
        """Lataa ehdokkaat"""
        if not self.candidates_file.exists():
            return {"candidates": []}
        return read_json_file(self.candidates_file)
    
    def save_candidates(self, candidates_data):
        """Tallenna ehdokkaat"""
        ensure_directory(self.candidates_file.parent)
        write_json_file(self.candidates_file, candidates_data)
    
    def add_candidate(self, name_fi, name_en=None, party="sitoutumaton", domain="yleinen", is_active=True):
        """Lisää uusi ehdokas"""
        candidates_data = self.load_candidates()
        
        # Tarkista uniikkius
        if not validate_candidate_uniqueness(self.candidates_file, name_fi):
            return False, "Ehdokas samalla nimellä on jo olemassa"
        
        # Luo uusi ehdokas
        candidate_id = f"cand_{uuid.uuid4().hex[:8]}"
        new_candidate = {
            "id": candidate_id,
            "basic_info": {
                "name": {
                    "fi": name_fi,
                    "en": name_en or name_fi
                },
                "party": party,
                "domain": domain,
                "is_active": is_active,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            },
            "status": "active" if is_active else "inactive",
            "answers_count": 0
        }
        
        candidates_data["candidates"].append(new_candidate)
        self.save_candidates(candidates_data)
        
        return True, new_candidate
    
    def remove_candidate(self, candidate_identifier):
        """Poista ehdokas"""
        candidates_data = self.load_candidates()
        
        # Etsi ehdokas ID:llä tai nimellä
        candidate_to_remove = get_candidate_by_id_or_name(self.candidates_file, candidate_identifier)
        if not candidate_to_remove:
            return False, "Ehdokasta ei löydy"
        
        candidate_id = candidate_to_remove["id"]
        initial_count = len(candidates_data["candidates"])
        candidates_data["candidates"] = [
            candidate for candidate in candidates_data["candidates"]
            if candidate["id"] != candidate_id
        ]
        
        removed_count = initial_count - len(candidates_data["candidates"])
        if removed_count > 0:
            self.save_candidates(candidates_data)
            return True, f"Poistettu ehdokas: {candidate_to_remove['basic_info']['name']['fi']}"
        else:
            return False, "Ehdokasta ei löytynyt"
    
    def update_candidate(self, candidate_identifier, name_fi=None, name_en=None, party=None, domain=None, is_active=None):
        """Päivitä ehdokas"""
        candidates_data = self.load_candidates()
        updated = False
        
        # Etsi ehdokas
        candidate_to_update = None
        candidate_index = -1
        
        for i, candidate in enumerate(candidates_data["candidates"]):
            if (candidate["id"] == candidate_identifier or 
                candidate["basic_info"]["name"]["fi"] == candidate_identifier or
                candidate["basic_info"]["name"]["en"] == candidate_identifier):
                candidate_to_update = candidate
                candidate_index = i
                break
        
        if not candidate_to_update:
            return False, "Ehdokasta ei löydy"
        
        # Päivitä kentät
        if name_fi is not None:
            candidates_data["candidates"][candidate_index]["basic_info"]["name"]["fi"] = name_fi
            updated = True
        
        if name_en is not None:
            candidates_data["candidates"][candidate_index]["basic_info"]["name"]["en"] = name_en
            updated = True
        
        if party is not None:
            candidates_data["candidates"][candidate_index]["basic_info"]["party"] = party
            updated = True
        
        if domain is not None:
            candidates_data["candidates"][candidate_index]["basic_info"]["domain"] = domain
            updated = True
        
        if is_active is not None:
            candidates_data["candidates"][candidate_index]["basic_info"]["is_active"] = is_active
            candidates_data["candidates"][candidate_index]["status"] = "active" if is_active else "inactive"
            updated = True
        
        if updated:
            candidates_data["candidates"][candidate_index]["basic_info"]["updated_at"] = datetime.now().isoformat()
            self.save_candidates(candidates_data)
            return True, f"Ehdokas päivitetty: {candidate_to_update['basic_info']['name']['fi']}"
        else:
            return False, "Ei muutoksia"
    
    def list_candidates(self, party_filter=None):
        """Listaa ehdokkaat"""
        candidates_data = self.load_candidates()
        candidates = candidates_data.get("candidates", [])
        
        if party_filter:
            candidates = [c for c in candidates if c["basic_info"]["party"] == party_filter]
        
        return candidates
    
    def get_candidate_stats(self):
        """Hae ehdokastilastot"""
        candidates_data = self.load_candidates()
        candidates = candidates_data.get("candidates", [])
        
        # Puolueet
        parties = set(c["basic_info"]["party"] for c in candidates)
        
        # Aktiiviset vs. passiiviset
        active_count = sum(1 for c in candidates if c["basic_info"]["is_active"])
        inactive_count = len(candidates) - active_count
        
        # Lataa vastaustilastot
        answers_file = Path(self.data_path) / "candidate_answers.json"
        candidates_with_answers = 0
        if answers_file.exists():
            answers_data = read_json_file(answers_file)
            candidates_with_answers = len(set(a["candidate_id"] for a in answers_data.get("answers", [])))
        
        return {
            "total_candidates": len(candidates),
            "parties": len(parties),
            "active_candidates": active_count,
            "inactive_candidates": inactive_count,
            "candidates_with_answers": candidates_with_answers,
            "answer_coverage": round((candidates_with_answers / len(candidates) * 100) if candidates else 0, 1)
        }


@click.command()
@click.option('--election', required=False, help='Vaalin tunniste (valinnainen, käytetään configista)')
@click.option('--add', is_flag=True, help='Lisää uusi ehdokas')
@click.option('--remove', help='Poista ehdokas (ID tai nimi)')
@click.option('--update', help='Päivitä ehdokas (ID tai nimi)')
@click.option('--list', 'list_candidates', is_flag=True, help='Listaa kaikki ehdokkaat')
@click.option('--name-fi', help='Ehdokkaan nimi suomeksi')
@click.option('--name-en', help='Ehdokkaan nimi englanniksi')
@click.option('--party', help='Puolue')
@click.option('--domain', help='Alue/domain')
@click.option('--inactive', is_flag=True, help='Merkitse ehdokas epäaktiiviseksi')
@click.option('--active', is_flag=True, help='Merkitse ehdokas aktiiviseksi')
def manage_candidates(election, add, remove, update, list_candidates, name_fi, name_en, party, domain, inactive, active):
    """Ehdokkaiden hallinta"""
    
    # Hae election_id configista jos parametria ei annettu
    election_id = get_election_id(election)
    if not election_id:
        print("❌ Vaali-ID:tä ei annettu eikä config tiedostoa löydy.")
        print("💡 Käytä: --election VAALI_ID tai asenna järjestelmä ensin: python src/cli/install.py --first-install")
        return
    
    manager = CandidateManager(election_id)
    
    if add:
        if not name_fi:
            print("❌ --name-fi vaaditaan uuden ehdokkaan lisäämiseksi")
            return
        
        # Aktiivisuustila
        is_active = True
        if inactive:
            is_active = False
        if active:
            is_active = True
        
        success, result = manager.add_candidate(
            name_fi=name_fi,
            name_en=name_en,
            party=party or "sitoutumaton",
            domain=domain or "yleinen",
            is_active=is_active
        )
        
        if success:
            print("✅ Ehdokas lisätty!")
            print(f"👤 Nimi: {result['basic_info']['name']['fi']}")
            print(f"🆔 ID: {result['id']}")
            print(f"🏛️  Puolue: {result['basic_info']['party']}")
            print(f"🎯 Alue: {result['basic_info']['domain']}")
            print(f"📊 Tila: {'Aktiivinen' if result['basic_info']['is_active'] else 'Epäaktiivinen'}")
        else:
            print(f"❌ {result}")
    
    elif remove:
        success, result = manager.remove_candidate(remove)
        if success:
            print(f"✅ {result}")
        else:
            print(f"❌ {result}")
    
    elif update:
        if not any([name_fi, name_en, party, domain, inactive, active]):
            print("❌ Anna vähintään yksi päivitettävä kenttä (--name-fi, --name-en, --party, --domain, --active, --inactive)")
            return
        
        # Aktiivisuustila
        is_active = None
        if inactive:
            is_active = False
        if active:
            is_active = True
        
        success, result = manager.update_candidate(
            candidate_identifier=update,
            name_fi=name_fi,
            name_en=name_en,
            party=party,
            domain=domain,
            is_active=is_active
        )
        
        if success:
            print(f"✅ {result}")
        else:
            print(f"❌ {result}")
    
    elif list_candidates:
        candidates = manager.list_candidates(party)
        stats = manager.get_candidate_stats()
        
        print(f"👑 REKISTERÖIDYT EHDOKKAAT - {election_id}")
        print("=" * 60)
        
        # Ryhmittele puolueittain
        parties = {}
        for candidate in candidates:
            party_name = candidate["basic_info"]["party"]
            if party_name not in parties:
                parties[party_name] = []
            parties[party_name].append(candidate)
        
        for party_name, party_candidates in parties.items():
            print(f"\n🏛️  PUOLUE: {party_name}")
            print("-" * 40)
            
            for candidate in party_candidates:
                basic_info = candidate["basic_info"]
                status_icon = "✅" if basic_info["is_active"] else "❌"
                signed_icon = "⚠️ " if candidate.get("status") != "signed" else "✅"
                
                print(f"   {status_icon} {basic_info['name']['fi']}")
                print(f"      🆔 {candidate['id']}")
                print(f"      {signed_icon} {candidate.get('status', 'AKTIIVINEN').upper()} | {signed_icon} EI ALLEKIRJOITETTU")
                print(f"      📝 Vastauksia: {candidate.get('answers_count', 0)}")
                print(f"      🎯 Alue: {basic_info['domain']}")
        
        print(f"\n📊 YHTEENVETO:")
        print(f"   👥 Ehdokkaita: {stats['total_candidates']}")
        print(f"   🏛️  Puolueita: {stats['parties']}")
        print(f"   📝 Vastanneita: {stats['candidates_with_answers']}")
        print(f"   📈 Vastauskattavuus: {stats['answer_coverage']}%")
    
    else:
        print("❌ Anna komento: --add, --remove, --update tai --list")
        print("💡 Kokeile: python src/cli/manage_candidates.py --list")


if __name__ == "__main__":
    manage_candidates()
