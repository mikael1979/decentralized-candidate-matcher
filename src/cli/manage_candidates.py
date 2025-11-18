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
                if (candidate["candidate_id"] == identifier or 
                    candidate["basic_info"]["name"]["fi"] == identifier):
                    return candidate
        except Exception:
            pass
        
        return None

@click.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--add', is_flag=True, help='Lisää uusi ehdokas')
@click.option('--name', help='Ehdokkaan nimi')
@click.option('--party', help='Puolue')
@click.option('--description-fi', help='Kuvaus suomeksi')
@click.option('--description-en', help='Kuvaus englanniksi')
@click.option('--description-sv', help='Kuvaus ruotsiksi')
@click.option('--domain', default='divine_power', help='Toimialue (esim. divine_power)')
@click.option('--list', 'list_candidates', is_flag=True, help='Listaa kaikki ehdokkaat')
@click.option('--show', help='Näytä tietyn ehdokkaan tiedot')
@click.option('--remove', help='Poista ehdokas (ID)')
@click.option('--update', help='Päivitä ehdokas (ID)')
def manage_candidates(election, add, name, party, description_fi, description_en, description_sv, 
                     domain, list_candidates, show, remove, update):
    """Hallinnoi vaaliehdokkaita"""
    
    candidates_file = "data/runtime/candidates.json"
    
    # Varmista että data-hakemisto on olemassa
    ensure_directory("data/runtime")
    
    if add:
        if not name:
            click.echo("❌ Anna --name")
            return
        
        # Tarkista että ehdokas on uniikki
        if not validate_candidate_uniqueness(candidates_file, name):
            click.echo(f"❌ Ehdokas '{name}' on jo olemassa!")
            return
        
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
                    "last_updated": datetime.now().isoformat(),
                    "version": "1.0.0"
                }
            }
        
        # Luo uusi ehdokas uniikilla ID:llä
        new_candidate = {
            "candidate_id": f"cand_{str(uuid.uuid4())[:8]}",  # Uniikki ID
            "basic_info": {
                "name": {
                    "fi": name,
                    "en": description_en or f"[EN] {name}",
                    "sv": description_sv or f"[SV] {name}"
                },
                "party": party or "sitoutumaton",
                "domain": domain,
                "description": {
                    "fi": description_fi or f"{name} - ehdokas",
                    "en": description_en or f"{name} - candidate", 
                    "sv": description_sv or f"{name} - kandidat"
                }
            },
            "answers": [],
            "credentials": {
                "public_key": None,  # Täytetään myöhemmin
                "certificate_signed": False
            },
            "metadata": {
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "election_id": election,
                "active": True
            }
        }
        
        data["candidates"].append(new_candidate)
        data["metadata"]["last_updated"] = datetime.now().isoformat()
        data["metadata"]["total_candidates"] = len(data["candidates"])
        
        # Tallenna
        try:
            write_json_file(candidates_file, data)
            click.echo(f"✅ Ehdokas lisätty: {name}")
            click.echo(f"👑 Ehdokkaita yhteensä: {len(data['candidates'])}")
            click.echo(f"🆔 Ehdokas ID: {new_candidate['candidate_id']}")
            click.echo(f"📋 Puolue: {new_candidate['basic_info']['party']}")
            click.echo(f"🎯 Toimialue: {new_candidate['basic_info']['domain']}")
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
        
        candidates = data.get("candidates", [])
        
        click.echo(f"👑 REKISTERÖIDYT EHDOKKAAT - {election}")
        click.echo("=" * 60)
        
        if not candidates:
            click.echo("❌ Ei ehdokkaita")
            return
        
        # Ryhmittele puolueittain
        parties = {}
        for candidate in candidates:
            party_name = candidate['basic_info'].get('party', 'Sitoutumaton')
            if party_name not in parties:
                parties[party_name] = []
            parties[party_name].append(candidate)
        
        for party_name, party_candidates in parties.items():
            click.echo(f"\n🏛️  PUOLUE: {party_name}")
            click.echo("-" * 40)
            
            for candidate in party_candidates:
                status = "✅ AKTIIVINEN" if candidate.get('metadata', {}).get('active', True) else "❌ PASSIIVINEN"
                answers_count = len(candidate.get('answers', []))
                cert_status = "🔐 ALLEKIRJOITETTU" if candidate.get('credentials', {}).get('certificate_signed') else "⚠️  EI ALLEKIRJOITETTU"
                
                click.echo(f"   👤 {candidate['basic_info']['name']['fi']}")
                click.echo(f"      🆔 {candidate['candidate_id']}")
                click.echo(f"      {status} | {cert_status}")
                click.echo(f"      📝 Vastauksia: {answers_count}")
                click.echo(f"      🎯 Alue: {candidate['basic_info'].get('domain', 'divine_power')}")
        
        click.echo(f"\n📊 YHTEENVETO:")
        click.echo(f"   👥 Ehdokkaita: {len(candidates)}")
        click.echo(f"   🏛️  Puolueita: {len(parties)}")
        click.echo(f"   📝 Vastauksia yhteensä: {sum(len(c.get('answers', [])) for c in candidates)}")
    
    elif show:
        # Näytä tietyn ehdokkaan tiedot
        candidate = get_candidate_by_id_or_name(candidates_file, show)
        
        if not candidate:
            click.echo(f"❌ Ehdokasta ei löydy: {show}")
            return
        
        click.echo(f"👤 EHDOKKAAN TIEDOT: {candidate['basic_info']['name']['fi']}")
        click.echo("=" * 50)
        click.echo(f"🆔 ID: {candidate['candidate_id']}")
        click.echo(f"🏛️  Puolue: {candidate['basic_info'].get('party', 'Sitoutumaton')}")
        click.echo(f"🎯 Toimialue: {candidate['basic_info'].get('domain', 'divine_power')}")
        click.echo(f"📅 Luotu: {candidate['metadata']['created']}")
        click.echo(f"✏️  Päivitetty: {candidate['metadata']['last_updated']}")
        
        # Tila
        status = "✅ AKTIIVINEN" if candidate.get('metadata', {}).get('active', True) else "❌ PASSIIVINEN"
        cert_status = "🔐 ALLEKIRJOITETTU" if candidate.get('credentials', {}).get('certificate_signed') else "⚠️  EI ALLEKIRJOITETTU"
        click.echo(f"📊 Tila: {status} | {cert_status}")
        
        # Kuvaus
        click.echo(f"\n📖 KUVAUS:")
        click.echo(f"   🇫🇮 {candidate['basic_info']['description']['fi']}")
        click.echo(f"   🇬🇧 {candidate['basic_info']['description']['en']}")
        click.echo(f"   🇸🇪 {candidate['basic_info']['description']['sv']}")
        
        # Vastaukset
        answers = candidate.get('answers', [])
        click.echo(f"\n📝 VASTAUKSET: {len(answers)} kpl")
        if answers:
            for i, answer in enumerate(answers[:5], 1):  # Näytä max 5 ensimmäistä
                click.echo(f"   {i}. Kysymys ID: {answer.get('question_id', 'N/A')}")
                click.echo(f"      Arvo: {answer.get('answer_value', 'N/A')}")
                click.echo(f"      Luottamus: {answer.get('confidence', 'N/A')}/5")
        else:
            click.echo("   ❌ Ei vastauksia")
    
    elif remove:
        # Poista ehdokas
        if not os.path.exists(candidates_file):
            click.echo("❌ Ehdokasrekisteriä ei ole vielä luotu")
            return
        
        try:
            data = read_json_file(candidates_file, {"candidates": []})
        except Exception as e:
            click.echo(f"❌ Ehdokasrekisterin lukuvirhe: {e}")
            return
        
        candidate_index = None
        candidate_name = None
        
        for i, cand in enumerate(data.get("candidates", [])):
            if cand["candidate_id"] == remove or cand["basic_info"]["name"]["fi"] == remove:
                candidate_index = i
                candidate_name = cand["basic_info"]["name"]["fi"]
                break
        
        if candidate_index is None:
            click.echo(f"❌ Ehdokasta ei löydy: {remove}")
            return
        
        # Vahvista poisto
        if not click.confirm(f"Haluatko varmasti poistaa ehdokkaan '{candidate_name}'?"):
            click.echo("❌ Poisto peruutettu")
            return
        
        # Poista ehdokas
        removed_candidate = data["candidates"].pop(candidate_index)
        data["metadata"]["last_updated"] = datetime.now().isoformat()
        data["metadata"]["total_candidates"] = len(data["candidates"])
        
        try:
            write_json_file(candidates_file, data)
            click.echo(f"✅ Ehdokas poistettu: {candidate_name}")
            click.echo(f"📊 Ehdokkaita jäljellä: {len(data['candidates'])}")
        except Exception as e:
            click.echo(f"❌ Ehdokkaan poisto epäonnistui: {e}")
    
    elif update:
        # Päivitä ehdokas
        candidate = get_candidate_by_id_or_name(candidates_file, update)
        
        if not candidate:
            click.echo(f"❌ Ehdokasta ei löydy: {update}")
            return
        
        # Lataa koko data päivitystä varten
        if not os.path.exists(candidates_file):
            click.echo("❌ Ehdokasrekisteriä ei ole vielä luotu")
            return
        
        try:
            data = read_json_file(candidates_file, {"candidates": []})
        except Exception as e:
            click.echo(f"❌ Ehdokasrekisterin lukuvirhe: {e}")
            return
        
        # Etsi ehdokas indeksi
        candidate_index = None
        for i, cand in enumerate(data.get("candidates", [])):
            if (cand["candidate_id"] == candidate["candidate_id"] or 
                cand["basic_info"]["name"]["fi"] == candidate["basic_info"]["name"]["fi"]):
                candidate_index = i
                break
        
        if candidate_index is None:
            click.echo(f"❌ Ehdokasta ei löydy datassa: {update}")
            return
        
        click.echo(f"✏️  Päivitetään ehdokasta: {candidate['basic_info']['name']['fi']}")
        
        # Päivitä kentät jos annettu
        updated = False
        current_candidate = data["candidates"][candidate_index]
        
        if name and name != current_candidate['basic_info']['name']['fi']:
            # Tarkista uniikkius
            if validate_candidate_uniqueness(candidates_file, name):
                current_candidate['basic_info']['name']['fi'] = name
                updated = True
                click.echo(f"   ✅ Nimi päivitetty: {name}")
            else:
                click.echo(f"   ❌ Nimi '{name}' on jo käytössä")
        
        if party and party != current_candidate['basic_info'].get('party'):
            current_candidate['basic_info']['party'] = party
            updated = True
            click.echo(f"   ✅ Puolue päivitetty: {party}")
        
        if description_fi and description_fi != current_candidate['basic_info']['description']['fi']:
            current_candidate['basic_info']['description']['fi'] = description_fi
            updated = True
            click.echo(f"   ✅ Kuvaus (FI) päivitetty")
        
        if domain and domain != current_candidate['basic_info'].get('domain'):
            current_candidate['basic_info']['domain'] = domain
            updated = True
            click.echo(f"   ✅ Toimialue päivitetty: {domain}")
        
        if updated:
            current_candidate['metadata']['last_updated'] = datetime.now().isoformat()
            data["candidates"][candidate_index] = current_candidate
            data["metadata"]["last_updated"] = datetime.now().isoformat()
            
            try:
                write_json_file(candidates_file, data)
                click.echo(f"✅ Ehdokas päivitetty onnistuneesti")
            except Exception as e:
                click.echo(f"❌ Ehdokkaan päivitys epäonnistui: {e}")
        else:
            click.echo("ℹ️  Ei muutoksia")
    
    else:
        click.echo("💡 KÄYTTÖ:")
        click.echo("   --add --name 'Nimi' --party 'Puolue'        # Lisää ehdokas")
        click.echo("   --list                                      # Listaa ehdokkaat")
        click.echo("   --show 'Nimi tai ID'                        # Näytä ehdokkaan tiedot")
        click.echo("   --remove 'Nimi tai ID'                      # Poista ehdokas")
        click.echo("   --update 'Nimi tai ID' --name 'Uusi nimi'   # Päivitä ehdokas")
        click.echo("\n🎯 LISÄVALINNAT:")
        click.echo("   --description-fi 'Kuvaus suomeksi'")
        click.echo("   --description-en 'Kuvaus englanniksi'")
        click.echo("   --description-sv 'Kuvaus ruotsiksi'")
        click.echo("   --domain 'toimialue'")

if __name__ == '__main__':
    manage_candidates()
