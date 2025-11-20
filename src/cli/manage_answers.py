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
Ehdokkaiden vastausten hallinta - PÄIVITETTY CONFIG-VERSIO
Käyttää config-järjestelmää ja sisältää remove/update toiminnot
"""
from core.config_manager import get_election_id, get_data_path
from core.file_utils import read_json_file, write_json_file, ensure_directory


class AnswerManager:
    """Vastausten hallinta config-järjestelmän kanssa"""
    
    def __init__(self, election_id=None):
        self.election_id = election_id or get_election_id()
        self.data_path = get_data_path(self.election_id)
        self.answers_file = Path(self.data_path) / "candidate_answers.json"
    
    def load_answers(self):
        """Lataa vastaukset"""
        if not self.answers_file.exists():
            return {"answers": []}
        return read_json_file(self.answers_file)
    
    def save_answers(self, answers_data):
        """Tallenna vastaukset"""
        ensure_directory(self.answers_file.parent)
        write_json_file(self.answers_file, answers_data)
    
    def add_answer(self, candidate_id, question_id, value, confidence, explanation_fi=None, explanation_en=None):
        """Lisää uusi vastaus"""
        answers_data = self.load_answers()
        
        # Tarkista onko vastaus jo olemassa
        for answer in answers_data["answers"]:
            if (answer.get("candidate_id") == candidate_id and 
                answer.get("question_id") == question_id):
                return False, "Ehdokkaalla on jo vastaus kysymykseen"
        
        # Luo uusi vastaus
        new_answer = {
            "id": f"ans_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "candidate_id": candidate_id,
            "question_id": question_id,
            "value": value,
            "confidence": confidence,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        if explanation_fi:
            new_answer["explanation_fi"] = explanation_fi
        if explanation_en:
            new_answer["explanation_en"] = explanation_en
        
        answers_data["answers"].append(new_answer)
        self.save_answers(answers_data)
        
        return True, new_answer
    
    def remove_answer(self, candidate_id, question_id):
        """Poista vastaus"""
        answers_data = self.load_answers()
        
        initial_count = len(answers_data["answers"])
        answers_data["answers"] = [
            answer for answer in answers_data["answers"]
            if not (answer.get("candidate_id") == candidate_id and 
                   answer.get("question_id") == question_id)
        ]
        
        removed_count = initial_count - len(answers_data["answers"])
        if removed_count > 0:
            self.save_answers(answers_data)
            return True, f"Poistettu {removed_count} vastaus"
        else:
            return False, "Vastausta ei löytynyt"
    
    def update_answer(self, candidate_id, question_id, value=None, confidence=None, explanation_fi=None, explanation_en=None):
        """Päivitä olemassa oleva vastaus"""
        answers_data = self.load_answers()
        updated = False
        
        for answer in answers_data["answers"]:
            if (answer.get("candidate_id") == candidate_id and 
                answer.get("question_id") == question_id):
                
                if value is not None:
                    answer["value"] = value
                    updated = True
                if confidence is not None:
                    answer["confidence"] = confidence
                    updated = True
                if explanation_fi is not None:
                    answer["explanation_fi"] = explanation_fi
                    updated = True
                if explanation_en is not None:
                    answer["explanation_en"] = explanation_en
                    updated = True
                
                if updated:
                    answer["updated_at"] = datetime.now().isoformat()
        
        if updated:
            self.save_answers(answers_data)
            return True, "Vastaus päivitetty"
        else:
            return False, "Vastausta ei löytynyt tai ei muutoksia"
    
    def list_answers(self, candidate_id=None):
        """Listaa vastaukset"""
        answers_data = self.load_answers()
        
        if candidate_id:
            answers = [a for a in answers_data["answers"] if a.get("candidate_id") == candidate_id]
        else:
            answers = answers_data["answers"]
        
        return answers
    
    def get_answer_stats(self):
        """Hae vastaustilastot"""
        answers_data = self.load_answers()
        answers = answers_data["answers"]
        
        # Ehdokkaat joilla on vastauksia
        candidates_with_answers = set(a["candidate_id"] for a in answers)
        
        # Lataa ehdokkaat yhteensä
        candidates_file = Path(self.data_path) / "candidates.json"
        total_candidates = 0
        if candidates_file.exists():
            candidates_data = read_json_file(candidates_file)
            total_candidates = len(candidates_data.get("candidates", []))
        
        return {
            "total_answers": len(answers),
            "candidates_with_answers": len(candidates_with_answers),
            "total_candidates": total_candidates,
            "answer_coverage": round((len(candidates_with_answers) / total_candidates * 100) if total_candidates > 0 else 0, 1)
        }


@click.group()
def manage_answers():
    """Ehdokkaiden vastausten hallinta"""
    pass


@manage_answers.command()
@click.option('--election', required=False, help='Vaalin tunniste (valinnainen, käytetään configista)')
@click.option('--candidate-id', required=True, help='Ehdokkaan ID')
@click.option('--question-id', required=True, help='Kysymyksen ID')
@click.option('--answer', type=int, required=True, help='Vastaus (-5 - +5)')
@click.option('--confidence', type=int, required=True, help='Varmuus (1-5)')
@click.option('--explanation-fi', help='Perustelu suomeksi')
@click.option('--explanation-en', help='Perustelu englanniksi')
def add(election, candidate_id, question_id, answer, confidence, explanation_fi, explanation_en):
    """Lisää uusi vastaus"""
    election_id = get_election_id(election)
    if not election_id:
        print("❌ Vaali-ID:tä ei annettu eikä config tiedostoa löydy.")
        print("💡 Käytä: --election VAALI_ID tai asenna järjestelmä ensin: python src/cli/install.py --first-install")
        return
    
    # Validointi
    if not (-5 <= answer <= 5):
        print("❌ Virheellinen vastausarvo! Käytä lukua -5 ja +5 välillä.")
        return
    
    if not (1 <= confidence <= 5):
        print("❌ Virheellinen varmuusarvo! Käytä lukua 1-5 välillä.")
        return
    
    manager = AnswerManager(election_id)
    success, result = manager.add_answer(candidate_id, question_id, answer, confidence, explanation_fi, explanation_en)
    
    if success:
        print("✅ Vastaus lisätty!")
        print(f"📊 Ehdokas: {candidate_id} → Kysymys: {question_id}")
        print(f"🎯 Arvo: {answer}/5, Varmuus: {confidence}/5")
        if explanation_fi:
            print(f"💬 Perustelu: {explanation_fi}")
    else:
        print(f"❌ {result}")


@manage_answers.command()
@click.option('--election', required=False, help='Vaalin tunniste (valinnainen, käytetään configista)')
@click.option('--candidate-id', required=True, help='Ehdokkaan ID')
@click.option('--question-id', required=True, help='Kysymyksen ID')
def remove(election, candidate_id, question_id):
    """Poista vastaus"""
    election_id = get_election_id(election)
    if not election_id:
        print("❌ Vaali-ID:tä ei annettu eikä config tiedostoa löydy.")
        return
    
    manager = AnswerManager(election_id)
    success, result = manager.remove_answer(candidate_id, question_id)
    
    if success:
        print(f"✅ {result}")
        print(f"🗑️  Poistettu: {candidate_id} → {question_id}")
    else:
        print(f"❌ {result}")


@manage_answers.command()
@click.option('--election', required=False, help='Vaalin tunniste (valinnainen, käytetään configista)')
@click.option('--candidate-id', required=True, help='Ehdokkaan ID')
@click.option('--question-id', required=True, help='Kysymyksen ID')
@click.option('--answer', type=int, help='Uusi vastaus (-5 - +5)')
@click.option('--confidence', type=int, help='Uusi varmuus (1-5)')
@click.option('--explanation-fi', help='Uusi perustelu suomeksi')
@click.option('--explanation-en', help='Uusi perustelu englanniksi')
def update(election, candidate_id, question_id, answer, confidence, explanation_fi, explanation_en):
    """Päivitä vastaus"""
    election_id = get_election_id(election)
    if not election_id:
        print("❌ Vaali-ID:tä ei annettu eikä config tiedostoa löydy.")
        return
    
    # Validointi
    if answer is not None and not (-5 <= answer <= 5):
        print("❌ Virheellinen vastausarvo! Käytä lukua -5 ja +5 välillä.")
        return
    
    if confidence is not None and not (1 <= confidence <= 5):
        print("❌ Virheellinen varmuusarvo! Käytä lukua 1-5 välillä.")
        return
    
    manager = AnswerManager(election_id)
    success, result = manager.update_answer(candidate_id, question_id, answer, confidence, explanation_fi, explanation_en)
    
    if success:
        print(f"✅ {result}")
        print(f"✏️  Päivitetty: {candidate_id} → {question_id}")
        if answer is not None:
            print(f"📊 Uusi arvo: {answer}/5")
        if confidence is not None:
            print(f"🎯 Uusi varmuus: {confidence}/5")
    else:
        print(f"❌ {result}")


@manage_answers.command()
@click.option('--election', required=False, help='Vaalin tunniste (valinnainen, käytetään configista)')
@click.option('--candidate-id', help='Näytä vain tietyn ehdokkaan vastaukset')
def list(election, candidate_id):
    """Listaa vastaukset"""
    election_id = get_election_id(election)
    if not election_id:
        print("❌ Vaali-ID:tä ei annettu eikä config tiedostoa löydy.")
        return
    
    manager = AnswerManager(election_id)
    
    if candidate_id:
        answers = manager.list_answers(candidate_id)
        if answers:
            print(f"📝 EHDOKKAAN {candidate_id} VASTAUKSET")
            print("=" * 50)
            for answer in answers:
                print(f"❓ Kysymys: {answer.get('question_id')}")
                print(f"📊 Vastaus: {answer.get('value')}/5")
                print(f"🎯 Varmuus: {answer.get('confidence')}/5")
                if answer.get('explanation_fi'):
                    print(f"💬 Perustelu: {answer.get('explanation_fi')}")
                print("-" * 30)
        else:
            print(f"❌ Ehdokkaalla {candidate_id} ei ole vastauksia")
    else:
        stats = manager.get_answer_stats()
        print("📊 EHDOKKAIDEN VASTAUSYHTEENVETO")
        print("=" * 50)
        
        # Lataa ehdokkaat nimille
        candidates_file = Path(manager.data_path) / "candidates.json"
        candidate_names = {}
        if candidates_file.exists():
            candidates_data = read_json_file(candidates_file)
            for candidate in candidates_data.get("candidates", []):
                candidate_names[candidate["id"]] = candidate.get("name_fi", candidate.get("name_en", "Nimetön"))
        
        answers = manager.list_answers()
        candidates_answers = {}
        
        for answer in answers:
            candidate_id = answer["candidate_id"]
            if candidate_id not in candidates_answers:
                candidates_answers[candidate_id] = 0
            candidates_answers[candidate_id] += 1
        
        # Näytä kaikki ehdokkaat
        for candidate_id, name in candidate_names.items():
            answer_count = candidates_answers.get(candidate_id, 0)
            status = "✅" if answer_count > 0 else "❌"
            print(f"{status} {name} ({candidate_id}): {answer_count} vastausta")
        
        print(f"\n📈 YHTEENVETO:")
        print(f"   Ehdokkaita: {stats['total_candidates']}")
        print(f"   Vastanneita: {stats['candidates_with_answers']}")
        print(f"   Vastauksia yhteensä: {stats['total_answers']}")
        print(f"   Vastauskattavuus: {stats['answer_coverage']}%")


if __name__ == "__main__":
    manage_answers()
