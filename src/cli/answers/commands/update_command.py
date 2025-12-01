"""
Update answer -komento.
"""
import click
import sys
from pathlib import Path
from datetime import datetime

# Lisää projektin juuri Python-polkuun
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from core import get_election_id
from src.cli.answers.managers import AnswerManager


@click.command()
@click.option('--election', required=False, help='Vaalin tunniste (valinnainen, käytetään configista)')
@click.option('--candidate-id', required=True, help='Ehdokkaan ID')
@click.option('--question-id', required=True, help='Kysymyksen ID')
@click.option('--answer', type=int, help='Uusi vastaus (-5 - +5)')
@click.option('--confidence', type=int, help='Uusi varmuus (1-5)')
@click.option('--explanation-fi', help='Uusi perustelu suomeksi')
@click.option('--explanation-en', help='Uusi perustelu englanniksi')
def update_command(election, candidate_id, question_id, answer, confidence, explanation_fi, explanation_en):
    """Päivitä vastaus"""
    election_id = get_election_id(election)
    if not election_id:
        click.echo("❌ Vaali-ID:tä ei annettu eikä config tiedostoa löydy.")
        return
    
    # Validointi
    if answer is not None and not (-5 <= answer <= 5):
        click.echo("❌ Virheellinen vastausarvo! Käytä lukua -5 ja +5 välillä.")
        return
    
    if confidence is not None and not (1 <= confidence <= 5):
        click.echo("❌ Virheellinen varmuusarvo! Käytä lukua 1-5 välillä.")
        return
    
    manager = AnswerManager(election_id)
    success, result = manager.update_answer(candidate_id, question_id, answer, confidence, explanation_fi, explanation_en)
    
    if success:
        click.echo(f"✅ {result}")
        click.echo(f"✏️  Päivitetty: {candidate_id} → {question_id}")
        if answer is not None:
            click.echo(f"📊 Uusi arvo: {answer}/5")
        if confidence is not None:
            click.echo(f"🎯 Uusi varmuus: {confidence}/5")
    else:
        click.echo(f"❌ {result}")
