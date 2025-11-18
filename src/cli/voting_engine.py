#!/usr/bin/env python3
import click
import json
import sys
from pathlib import Path
from datetime import datetime

# Lisää src hakemisto Python-polkuun
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.file_utils import read_json_file, write_json_file, ensure_directory

@click.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--start', is_flag=True, help='Aloita vaalikone')
@click.option('--results', help='Näytä tulokset (käyttäjä-ID)')
def voting_engine(election, start, results):
    """Vaalikoneen ydin - käyttäjien vastausten keräys ja tulosten laskenta"""
    
    if start:
        start_voting_session(election)
    elif results:
        show_results(election, results)
    else:
        click.echo("💡 KÄYTTÖ:")
        click.echo("   --start          # Aloita uusi vaalikone")
        click.echo("   --results ID     # Näytä tulokset")

def start_voting_session(election):
    """Aloita uusi vaalikonesessio"""
    click.echo(f"🗳️  VAALIKONE: {election}")
    click.echo("=" * 50)
    
    # Lataa kysymykset
    questions = load_questions(election)
    if not questions:
        click.echo("❌ Ei kysymyksiä saatavilla")
        return
    
    click.echo(f"📝 Kysymyksiä: {len(questions)}")
    click.echo("🤔 Vastaa kysymyksiin asteikolla -5 (täysin eri mieltä) ... +5 (täysin samaa mieltä)")
    click.echo()
    
    # Yksinkertainen testiversio - kerää vastaukset
    user_answers = {}
    for i, question in enumerate(questions, 1):
        q_content = question["content"]
        click.echo(f"{i}. {q_content['question']['fi']}")
        
        try:
            answer = click.prompt("   Vastaus (-5 - +5)", type=int)
            if -5 <= answer <= 5:
                user_answers[question["local_id"]] = answer
            else:
                click.echo("   ❌ Vastauksen tulee olla välillä -5 - +5")
        except ValueError:
            click.echo("   ❌ Anna numero")
    
    click.echo(f"✅ Vastasit {len(user_answers)} kysymykseen")
    click.echo("🚧 Vaalikone on kehityksessä - tulosten laskenta tulossa pian!")

def load_questions(election):
    """Lataa kysymykset"""
    questions_file = "data/runtime/questions.json"
    if not Path(questions_file).exists():
        return []
    
    data = read_json_file(questions_file, {"questions": []})
    return [q for q in data.get("questions", []) if q.get("content")]

def show_results(election, session_id):
    """Näytä tulokset (placeholder)"""
    click.echo(f"📊 Tulosten näyttäminen kehityksessä - Sessio: {session_id}")

if __name__ == '__main__':
    voting_engine()
