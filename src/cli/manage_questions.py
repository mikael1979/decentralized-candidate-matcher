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


class QuestionManager:
    """Kysymysten hallinta config-järjestelmän kanssa"""
    
    def __init__(self, election_id=None):
        self.election_id = election_id or get_election_id()
        self.data_path = get_data_path(self.election_id)
        self.questions_file = Path(self.data_path) / "questions.json"
    
    def load_questions(self):
        """Lataa kysymykset"""
        if not self.questions_file.exists():
            return {"questions": []}
        return read_json_file(self.questions_file)
    
    def save_questions(self, questions_data):
        """Tallenna kysymykset"""
        ensure_directory(self.questions_file.parent)
        write_json_file(self.questions_file, questions_data)
    
    def add_question(self, question_fi, category="Yleinen", question_en=None, elo_rating=1000):
        """Lisää uusi kysymys"""
        questions_data = self.load_questions()
        
        # Tarkista onko kysymys jo olemassa
        for question in questions_data["questions"]:
            if question.get("question_fi") == question_fi:
                return False, "Kysymys samalla tekstillä on jo olemassa"
        
        # Luo uusi kysymys
        question_id = f"q_{uuid.uuid4().hex[:8]}"
        new_question = {
            "id": question_id,
            "question_fi": question_fi,
            "question_en": question_en or question_fi,
            "category": category,
            "elo_rating": elo_rating,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        questions_data["questions"].append(new_question)
        self.save_questions(questions_data)
        
        return True, new_question
    
    def remove_question(self, question_identifier):
        """Poista kysymys"""
        questions_data = self.load_questions()
        
        # Etsi kysymys ID:llä tai tekstillä
        question_to_remove = None
        for question in questions_data["questions"]:
            if (question["id"] == question_identifier or 
                question["question_fi"] == question_identifier):
                question_to_remove = question
                break
        
        if not question_to_remove:
            return False, "Kysymystä ei löydy"
        
        initial_count = len(questions_data["questions"])
        questions_data["questions"] = [
            question for question in questions_data["questions"]
            if question["id"] != question_to_remove["id"]
        ]
        
        removed_count = initial_count - len(questions_data["questions"])
        if removed_count > 0:
            self.save_questions(questions_data)
            return True, f"Poistettu kysymys: {question_to_remove['question_fi']}"
        else:
            return False, "Kysymystä ei löytynyt"
    
    def update_question(self, question_identifier, question_fi=None, question_en=None, category=None, elo_rating=None):
        """Päivitä kysymys"""
        questions_data = self.load_questions()
        updated = False
        
        # Etsi kysymys
        question_to_update = None
        question_index = -1
        
        for i, question in enumerate(questions_data["questions"]):
            if (question["id"] == question_identifier or 
                question["question_fi"] == question_identifier):
                question_to_update = question
                question_index = i
                break
        
        if not question_to_update:
            return False, "Kysymystä ei löydy"
        
        # Päivitä kentät
        if question_fi is not None:
            questions_data["questions"][question_index]["question_fi"] = question_fi
            updated = True
        
        if question_en is not None:
            questions_data["questions"][question_index]["question_en"] = question_en
            updated = True
        
        if category is not None:
            questions_data["questions"][question_index]["category"] = category
            updated = True
        
        if elo_rating is not None:
            questions_data["questions"][question_index]["elo_rating"] = elo_rating
            updated = True
        
        if updated:
            questions_data["questions"][question_index]["updated_at"] = datetime.now().isoformat()
            self.save_questions(questions_data)
            return True, f"Kysymys päivitetty: {question_to_update['question_fi']}"
        else:
            return False, "Ei muutoksia"
    
    def list_questions(self, category_filter=None):
        """Listaa kysymykset"""
        questions_data = self.load_questions()
        questions = questions_data.get("questions", [])
        
        if category_filter:
            questions = [q for q in questions if q["category"] == category_filter]
        
        return questions
    
    def get_question_stats(self):
        """Hae kysymystilastot"""
        questions_data = self.load_questions()
        questions = questions_data.get("questions", [])
        
        # Kategoriat
        categories = {}
        for question in questions:
            category = question["category"]
            categories[category] = categories.get(category, 0) + 1
        
        # ELO-jakauma
        elo_ratings = [q["elo_rating"] for q in questions if "elo_rating" in q]
        avg_elo = sum(elo_ratings) / len(elo_ratings) if elo_ratings else 1000
        
        return {
            "total_questions": len(questions),
            "categories": categories,
            "average_elo": round(avg_elo, 1),
            "min_elo": min(elo_ratings) if elo_ratings else 1000,
            "max_elo": max(elo_ratings) if elo_ratings else 1000
        }


@click.command()
@click.option('--election', required=False, help='Vaalin tunniste (valinnainen, käytetään configista)')
@click.option('--add', is_flag=True, help='Lisää uusi kysymys')
@click.option('--remove', help='Poista kysymys (ID tai teksti)')
@click.option('--update', help='Päivitä kysymys (ID tai teksti)')
@click.option('--list', 'list_questions', is_flag=True, help='Listaa kaikki kysymykset')
@click.option('--question-fi', help='Kysymys suomeksi')
@click.option('--question-en', help='Kysymys englanniksi')
@click.option('--category', help='Kysymyksen kategoria')
@click.option('--elo-rating', type=int, help='ELO-luokitus')
def manage_questions(election, add, remove, update, list_questions, question_fi, question_en, category, elo_rating):
    """Kysymysten hallinta"""
    
    # Hae election_id configista jos parametria ei annettu
    election_id = get_election_id(election)
    if not election_id:
        print("❌ Vaali-ID:tä ei annettu eikä config tiedostoa löydy.")
        print("💡 Käytä: --election VAALI_ID tai asenna järjestelmä ensin: python src/cli/install.py --first-install")
        return
    
    manager = QuestionManager(election_id)
    
    if add:
        if not question_fi:
            print("❌ --question-fi vaaditaan uuden kysymyksen lisäämiseksi")
            return
        
        success, result = manager.add_question(
            question_fi=question_fi,
            question_en=question_en,
            category=category or "Yleinen",
            elo_rating=elo_rating or 1000
        )
        
        if success:
            print("✅ Kysymys lisätty!")
            print(f"❓ {result['question_fi']}")
            print(f"🆔 ID: {result['id']}")
            print(f"📁 Kategoria: {result['category']}")
            print(f"🎯 ELO-luokitus: {result['elo_rating']}")
        else:
            print(f"❌ {result}")
    
    elif remove:
        success, result = manager.remove_question(remove)
        if success:
            print(f"✅ {result}")
        else:
            print(f"❌ {result}")
    
    elif update:
        if not any([question_fi, question_en, category, elo_rating]):
            print("❌ Anna vähintään yksi päivitettävä kenttä (--question-fi, --question-en, --category, --elo-rating)")
            return
        
        success, result = manager.update_question(
            question_identifier=update,
            question_fi=question_fi,
            question_en=question_en,
            category=category,
            elo_rating=elo_rating
        )
        
        if success:
            print(f"✅ {result}")
        else:
            print(f"❌ {result}")
    
    elif list_questions:
        questions = manager.list_questions(category)
        stats = manager.get_question_stats()
        
        print(f"📝 KYSYMYSLISTA - {election_id}")
        print("=" * 50)
        
        # Ryhmittele kategorioittain
        categories = {}
        for question in questions:
            cat = question["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(question)
        
        for category_name, category_questions in categories.items():
            print(f"\n📁 KATEGORIA: {category_name}")
            print("-" * 40)
            
            for i, question in enumerate(category_questions, 1):
                print(f"{i}. [{question['id']}] {question['question_fi']}")
                if question.get('question_en') and question['question_en'] != question['question_fi']:
                    print(f"   EN: {question['question_en']}")
                print(f"   🎯 ELO-luokitus: {question['elo_rating']}")
        
        print(f"\n📊 YHTEENVETO:")
        print(f"   ❓ Kysymyksiä: {stats['total_questions']}")
        print(f"   📁 Kategorioita: {len(stats['categories'])}")
        print(f"   📈 Keskim. ELO: {stats['average_elo']}")
        for cat, count in stats['categories'].items():
            print(f"      - {cat}: {count} kysymystä")
    
    else:
        print("❌ Anna komento: --add, --remove, --update tai --list")
        print("💡 Kokeile: python src/cli/manage_questions.py --list")


if __name__ == "__main__":
    manage_questions()
