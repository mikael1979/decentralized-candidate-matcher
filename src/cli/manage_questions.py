#!/usr/bin/env python3
import click
import json
from datetime import datetime
import os
import sys
from pathlib import Path

# LISÄTTY: Lisää src hakemisto Python-polkuun
sys.path.insert(0, str(Path(__file__).parent.parent))

import click
import json
import sys
import os
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.error_handling import (
    handle_file_errors, validate_election_exists, 
    safe_json_read, safe_json_write, ElectionSystemError
)

@click.group()
def manage_questions():
    """Kysymysten hallinta parannetulla virheenkäsittelyllä"""
    pass

@manage_questions.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--add', is_flag=True, help='Lisää uusi kysymys')
@click.option('--category', help='Kysymyksen kategoria')
@click.option('--question-fi', help='Kysymys suomeksi')
@click.option('--list', 'list_questions', is_flag=True, help='Listaa kaikki kysymykset')
@handle_file_errors
def main(election, add, category, question_fi, list_questions):
    """Pääkomento parannetulla virheenkäsittelyllä"""
    
    # Varmista että vaali on olemassa
    validate_election_exists(election)
    
    if add:
        if not category or not question_fi:
            raise click.UsageError("Anna --category ja --question-fi lisätäksesi kysymyksen")
        _add_question(election, category, question_fi)
    elif list_questions:
        _list_questions(election)
    else:
        click.echo("💡 Käytä --add lisätäksesi kysymyksen tai --list listataksesi kysymykset")

def _add_question(election_id: str, category: str, question_fi: str):
    """Lisää uusi kysymys"""
    questions_file = f"data/runtime/questions.json"
    
    # Lataa nykyiset kysymykset turvallisesti
    if os.path.exists(questions_file):
        data = safe_json_read(questions_file)
    else:
        data = {
            "questions": [],
            "metadata": {"election_id": election_id}
        }
    
    # Tarkista duplikaatit
    existing_question = next(
        (q for q in data["questions"] 
         if q["content"]["question"]["fi"].lower() == question_fi.lower()),
        None
    )
    
    if existing_question:
        raise ElectionSystemError(f"Kysymys on jo olemassa: {question_fi}")
    
    # Luo uusi kysymys
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
            "created_local": datetime.now().isoformat(),
            "modified_local": datetime.now().isoformat()
        }
    }
    
    data["questions"].append(new_question)
    
    # Tallenna turvallisesti
    safe_json_write(questions_file, data)
    
    click.echo(f"✅ Kysymys lisätty: {question_fi}")
    click.echo(f"📊 Kysymyksiä yhteensä: {len(data['questions'])}")

def _list_questions(election_id: str):
    """Listaa kaikki kysymykset"""
    questions_file = f"data/runtime/questions.json"
    
    if not os.path.exists(questions_file):
        click.echo("ℹ️ Ei kysymyksiä vielä lisätty")
        return
    
    data = safe_json_read(questions_file)
    
    click.echo("📝 KYSYMYSLISTA")
    click.echo("=" * 50)
    
    for i, question in enumerate(data["questions"], 1):
        click.echo(f"{i}. [{question['local_id']}] {question['content']['question']['fi']}")
        click.echo(f"   Kategoria: {question['content']['category']}")
        click.echo(f"   ELO-luokitus: {question['elo_rating']['current_rating']}")
        click.echo()

if __name__ == '__main__':
    main()
