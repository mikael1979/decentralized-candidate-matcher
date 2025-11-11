#!/usr/bin/env python3
import click
import json
from datetime import datetime
import os

@click.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--add', is_flag=True, help='Lisää uusi kysymys')
@click.option('--category', help='Kysymyksen kategoria')
@click.option('--question-fi', help='Kysymys suomeksi')
def manage_questions(election, add, category, question_fi):
    """Hallinnoi vaalikoneen kysymyksiä"""
    
    if add:
        if not category or not question_fi:
            click.echo("❌ Anna --category ja --question-fi")
            return
        
        # Lataa nykyiset kysymykset
        questions_file = f"data/runtime/questions.json"
        if os.path.exists(questions_file):
            with open(questions_file, 'r') as f:
                data = json.load(f)
        else:
            data = {"questions": [], "metadata": {"election_id": election}}
        
        # Lisää uusi kysymys
        new_question = {
            "local_id": f"q_{len(data['questions']) + 1}",
            "content": {
                "category": category,
                "question": {
                    "fi": question_fi,
                    "en": f"[EN] {question_fi}",
                    "sv": f"[SV] {question_fi}"
                },
                "scale": {"min": -5, "max": 5}
            },
            "elo_rating": {
                "base_rating": 1000,
                "current_rating": 1000,
                "comparison_delta": 0,
                "vote_delta": 0
            },
            "timestamps": {
                "created_local": datetime.now().isoformat()
            }
        }
        
        data["questions"].append(new_question)
        
        # Tallenna
        with open(questions_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        click.echo(f"✅ Kysymys lisätty: {question_fi}")
        click.echo(f"📊 Kysymyksiä yhteensä: {len(data['questions'])}")

if __name__ == '__main__':
    manage_questions()
