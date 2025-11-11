#!/usr/bin/env python3
import click
import random
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from managers.elo_manager import ELOManager
except ImportError:
    # Fallback simple implementation
    class ELOManager:
        def __init__(self, election_id: str):
            self.election_id = election_id
            self.k_factor = 32
        
        def calculate_expected(self, rating_a: int, rating_b: int) -> float:
            return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
        
        def update_ratings(self, question_a: str, question_b: str, winner: str):
            with open("data/runtime/questions.json", "r") as f:
                data = json.load(f)
            
            q_a = next((q for q in data["questions"] if q["local_id"] == question_a), None)
            q_b = next((q for q in data["questions"] if q["local_id"] == question_b), None)
            
            if not q_a or not q_b:
                raise ValueError("Kysymyksiä ei löydy")
            
            rating_a = q_a["elo_rating"]["current_rating"]
            rating_b = q_b["elo_rating"]["current_rating"]
            
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
            
            q_a["elo_rating"]["current_rating"] = int(new_rating_a)
            q_a["elo_rating"]["comparison_delta"] = int(new_rating_a - rating_a)
            q_b["elo_rating"]["current_rating"] = int(new_rating_b)
            q_b["elo_rating"]["comparison_delta"] = int(new_rating_b - rating_b)
            
            with open("data/runtime/questions.json", "w") as f:
                json.dump(data, f, indent=2)
            
            return {
                "question_a": {"old": rating_a, "new": new_rating_a, "delta": new_rating_a - rating_a},
                "question_b": {"old": rating_b, "new": new_rating_b, "delta": new_rating_b - rating_b}
            }

@click.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--choice', help='Valinta (a/b/t) - jos annettu, ei kysy interaktiivisesti')
def compare_questions(election, choice):
    """Vertaa kahta satunnaista kysymystä keskenään"""
    
    # Lataa kysymykset
    with open("data/runtime/questions.json", "r") as f:
        data = json.load(f)
    
    if len(data["questions"]) < 2:
        click.echo("❌ Tarvitaan vähintään 2 kysymystä vertailuun")
        return
    
    # Valitse kaksi satunnaista kysymystä
    q1, q2 = random.sample(data["questions"], 2)
    
    click.echo("🔍 VERTAA KYSYMYKSIÄ")
    click.echo("=" * 50)
    click.echo(f"A) {q1['content']['question']['fi']}")
    click.echo(f"   Luokitus: {q1['elo_rating']['current_rating']}")
    click.echo("")
    click.echo(f"B) {q2['content']['question']['fi']}") 
    click.echo(f"   Luokitus: {q2['elo_rating']['current_rating']}")
    click.echo("")
    
    # Hae valinta joko parametrista tai interaktiivisesti
    if choice:
        if choice.lower() in ['a', 'b', 't']:
            user_choice = choice.lower()
            click.echo(f"Automaattinen valinta: {user_choice}")
        else:
            click.echo("❌ Virheellinen valinta parametrissa, käytetään interaktiivista")
            user_choice = click.prompt("Kumpi on tärkeämpi? (a/b/tasapeli)", type=click.Choice(['a', 'b', 't']))
    else:
        user_choice = click.prompt("Kumpi on tärkeämpi? (a/b/tasapeli)", type=click.Choice(['a', 'b', 't']))
    
    # Päivitä ELO-luokitukset
    elo_manager = ELOManager(election)
    result = elo_manager.update_ratings(q1["local_id"], q2["local_id"], user_choice)
    
    click.echo("")
    click.echo("✅ Luokitukset päivitetty!")
    click.echo(f"📊 A: {result['question_a']['old']} → {result['question_a']['new']} ({result['question_a']['delta']:+.0f})")
    click.echo(f"📊 B: {result['question_b']['old']} → {result['question_b']['new']} ({result['question_b']['delta']:+.0f})")

if __name__ == '__main__':
    compare_questions()
