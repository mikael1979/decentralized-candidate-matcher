#!/usr/bin/env python3
import click
import json
import random
from datetime import datetime
from pathlib import Path
import sys

# Lisää src-hakemisto polkuun
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import get_election_id, get_data_path
from core.file_utils import read_json_file, write_json_file

# KORJATTU: Käytetään aina fallback ELOManageria
class ELOManager:
    def __init__(self, election_id: str):
        self.election_id = election_id
        self.k_factor = 32
    
    def calculate_expected(self, rating_a: int, rating_b: int) -> float:
        return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    
    def update_ratings(self, question_a_id: str, question_b_id: str, winner: str):
        # KORJATTU: Käytä config-järjestelmän data-polkua
        election_id = get_election_id()
        data_path = get_data_path(election_id)
        questions_file = Path(data_path) / "questions.json"
        
        data = read_json_file(questions_file)
        
        # KORJATTU: Etsi kysymykset id:n perusteella
        q_a = next((q for q in data["questions"] if q.get("id") == question_a_id), None)
        q_b = next((q for q in data["questions"] if q.get("id") == question_b_id), None)
        
        if not q_a or not q_b:
            raise ValueError(f"Kysymyksiä ei löydy: {question_a_id} tai {question_b_id}")
        
        # KORJATTU: elo_rating on kokonaisluku, ei dictionary
        rating_a = q_a["elo_rating"]  # Suoraan kokonaisluku
        rating_b = q_b["elo_rating"]  # Suoraan kokonaisluku
        
        expected_a = self.calculate_expected(rating_a, rating_b)
        expected_b = self.calculate_expected(rating_b, rating_a)
        
        if winner == "a":
            actual_a, actual_b = 1.0, 0.0
        elif winner == "b":
            actual_a, actual_b = 0.0, 1.0
        else:
            actual_a, actual_b = 0.5, 0.5
        
        new_rating_a = rating_a + self.k_factor * (actual_a - expected_a)
        new_rating_b = rating_b + self.k_factor * (actual_b - expected_b)
        
        # KORJATTU: Päivitä suoraan kokonaislukuna
        q_a["elo_rating"] = int(new_rating_a)
        q_b["elo_rating"] = int(new_rating_b)
        
        write_json_file(questions_file, data)
        
        return {
            "question_a": {"old": rating_a, "new": new_rating_a, "delta": new_rating_a - rating_a},
            "question_b": {"old": rating_b, "new": new_rating_b, "delta": new_rating_b - rating_b}
        }

def auto_compare(election_id: str, rounds: int):
    """Suorita automaattinen ELO-vertailu ilman käyttäjän syötettä"""
    elo_manager = ELOManager(election_id)
    
    # KORJATTU: Käytä config-järjestelmän data-polkua
    data_path = get_data_path(election_id)
    questions_file = Path(data_path) / "questions.json"
    
    data = read_json_file(questions_file)
    
    if len(data["questions"]) < 2:
        click.echo("❌ Tarvitaan vähintään 2 kysymystä automaattiseen vertailuun")
        return
    
    click.echo(f"🤖 SUORITETAAN {rounds} AUTOMAATTISTA VERTAILUA...")
    click.echo("-" * 50)
    
    for i in range(rounds):
        # Valitse kaksi satunnaista kysymystä
        q1, q2 = random.sample(data["questions"], 2)
        
        # Simuloi satunnainen tulos: 45% q1 voittaa, 45% q2 voittaa, 10% tasapeli
        rand = random.random()
        if rand < 0.45:
            winner = "a"
        elif rand < 0.90:
            winner = "b"
        else:
            winner = "t"
        
        try:
            result = elo_manager.update_ratings(q1["id"], q2["id"], winner)
            
            winner_text = {"a": "A", "b": "B", "t": "TASAPELI"}[winner]
            # KORJATTU: Käytä oikeaa kysymyskenttää
            question_text_a = q1.get("question_fi", "Nimetön kysymys")
            question_text_b = q2.get("question_fi", "Nimetön kysymys")
            
            question_a_text = question_text_a[:30] + "..." if len(question_text_a) > 30 else question_text_a
            question_b_text = question_text_b[:30] + "..." if len(question_text_b) > 30 else question_text_b
            
            click.echo(f"{i+1:2d}. {winner_text} | {question_a_text} vs {question_b_text}")
            click.echo(f"      A: {result['question_a']['old']} → {result['question_a']['new']} ({result['question_a']['delta']:+.0f})")
            click.echo(f"      B: {result['question_b']['old']} → {result['question_b']['new']} ({result['question_b']['delta']:+.0f})")
        
        except Exception as e:
            click.echo(f"{i+1:2d}. ❌ Virhe ELO-päivityksessä: {e}")
            continue
    
    click.echo(f"\n✅ {rounds} automaattista ELO-vertailua suoritettu!")

def get_questions_data(election_id=None):
    """Hae kysymysten data config-järjestelmän kautta"""
    try:
        election_id = election_id or get_election_id()
        data_path = get_data_path(election_id)
        questions_file = Path(data_path) / "questions.json"
        
        if not questions_file.exists():
            click.echo(f"❌ Kysymysten tiedostoa ei löydy: {questions_file}")
            click.echo("💡 Luo kysymyksiä ensin: python src/cli/manage_questions.py --add")
            return None
            
        return read_json_file(questions_file)
        
    except Exception as e:
        click.echo(f"❌ Kysymysten lataus epäonnistui: {e}")
        return None

@click.command()
@click.option('--election', help='Vaalin tunniste (valinnainen, käytetään configista)')
@click.option('--auto', type=int, help='Automaattisten vertailukierrosten määrä (esim. 5)')
@click.option('--choice', help='Valinta (a/b/t) - jos annettu, ei kysy interaktiivisesti')
def compare_questions(election, auto, choice):
    """Vertaa kysymyksiä ELO-järjestelmällä (interaktiivisesti tai automaattisesti)"""
    
    # KORJATTU: Käytä config-järjestelmää
    election_id = election or get_election_id()
    if not election_id:
        click.echo("❌ Vaalia ei ole asetettu. Käytä --election tai asenna järjestelmä ensin.")
        click.echo("💡 Asenna vaali: python src/cli/install.py --list-elections")
        return
    
    click.echo(f"🎯 ELO-vertailu vaalille: {election_id}")
    
    if auto is not None:
        if auto <= 0:
            click.echo("❌ --auto arvon tulee olla positiivinen kokonaisluku")
            return
        auto_compare(election_id, auto)
        return
    
    # Interaktiivinen vertailu
    data = get_questions_data(election_id)
    if not data:
        return
    
    if len(data["questions"]) < 2:
        click.echo("❌ Tarvitaan vähintään 2 kysymystä vertailuun")
        click.echo("💡 Lisää kysymyksiä: python src/cli/manage_questions.py --add")
        return
    
    q1, q2 = random.sample(data["questions"], 2)
    
    click.echo("🔍 VERTAA KYSYMYKSIÄ")
    click.echo("=" * 50)
    
    # KORJATTU: Käytä oikeaa kysymyskenttää
    click.echo(f"A) {q1['question_fi']}")
    click.echo(f"   Luokitus: {q1['elo_rating']}")
    click.echo("")
    click.echo(f"B) {q2['question_fi']}") 
    click.echo(f"   Luokitus: {q2['elo_rating']}")
    click.echo("")
    
    if choice:
        if choice.lower() in ['a', 'b', 't']:
            user_choice = choice.lower()
            click.echo(f"Automaattinen valinta: {user_choice}")
        else:
            click.echo("❌ Virheellinen valinta, käytetään interaktiivista")
            user_choice = click.prompt("Kumpi on tärkeämpi? (a/b/tasapeli)", type=click.Choice(['a', 'b', 't']))
    else:
        user_choice = click.prompt("Kumpi on tärkeämpi? (a/b/tasapeli)", type=click.Choice(['a', 'b', 't']))
    
    elo_manager = ELOManager(election_id)
    try:
        result = elo_manager.update_ratings(q1["id"], q2["id"], user_choice)
        
        click.echo("\n✅ Luokitukset päivitetty!")
        click.echo(f"📊 A: {result['question_a']['old']} → {result['question_a']['new']} ({result['question_a']['delta']:+.0f})")
        click.echo(f"📊 B: {result['question_b']['old']} → {result['question_b']['new']} ({result['question_b']['delta']:+.0f})")
    
    except Exception as e:
        click.echo(f"❌ ELO-päivitys epäonnistui: {e}")

if __name__ == '__main__':
    compare_questions()
