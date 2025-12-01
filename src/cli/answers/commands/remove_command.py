"""
Remove answer -komento.
"""
import click
import sys
from pathlib import Path

# Lisää projektin juuri Python-polkuun
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from core import get_election_id
from src.cli.answers.managers import AnswerManager


@click.command()
@click.option('--election', required=False, help='Vaalin tunniste (valinnainen, käytetään configista)')
@click.option('--candidate-id', required=True, help='Ehdokkaan ID')
@click.option('--question-id', required=True, help='Kysymyksen ID')
def remove_command(election, candidate_id, question_id):
    """Poista vastaus"""
    election_id = get_election_id(election)
    if not election_id:
        click.echo("❌ Vaali-ID:tä ei annettu eikä config tiedostoa löydy.")
        return
    
    manager = AnswerManager(election_id)
    success, result = manager.remove_answer(candidate_id, question_id)
    
    if success:
        click.echo(f"✅ {result}")
        click.echo(f"🗑️  Poistettu: {candidate_id} → {question_id}")
    else:
        click.echo(f"❌ {result}")
