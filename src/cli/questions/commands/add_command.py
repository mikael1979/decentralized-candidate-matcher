# src/cli/questions/commands/add_command.py (korjaa import)
"""
Add question -komento.
"""
import click
import sys
from pathlib import Path

# Lisää projektin juuri Python-polkuun
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cli.questions.managers import QuestionManager


def add_question_command(election_id, question_fi, question_en=None, category=None, elo_rating=None):
    """Suorita add-komento."""
    if not question_fi:
        print("❌ --question-fi vaaditaan uuden kysymyksen lisäämiseksi")
        return False
    
    manager = QuestionManager(election_id=election_id)
    
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
        return True
    else:
        print(f"❌ {result}")
        return False


@click.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--question-fi', required=True, help='Kysymys suomeksi')
@click.option('--question-en', help='Kysymys englanniksi')
@click.option('--category', help='Kysymyksen kategoria')
@click.option('--elo-rating', type=int, help='ELO-luokitus')
def add_command(election, question_fi, question_en, category, elo_rating):
    """Lisää uusi kysymys."""
    add_question_command(election, question_fi, question_en, category, elo_rating)
