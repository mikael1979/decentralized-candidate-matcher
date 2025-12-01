"""
Add answer -komento.
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
@click.option('--answer', type=int, required=True, help='Vastaus (-5 - +5)')
@click.option('--confidence', type=int, required=True, help='Varmuus (1-5)')
@click.option('--explanation-fi', help='Perustelu suomeksi')
@click.option('--explanation-en', help='Perustelu englanniksi')
def add_command(election, candidate_id, question_id, answer, confidence, explanation_fi, explanation_en):
    """Lisää uusi vastaus"""
    election_id = get_election_id(election)
    if not election_id:
        click.echo("❌ Vaali-ID:tä ei annettu eikä config tiedostoa löydy.")
        click.echo("💡 Käytä: --election VAALI_ID tai asenna järjestelmä ensin: python src/cli/install.py --first-install")
        return
    
    # Validointi
    if not (-5 <= answer <= 5):
        click.echo("❌ Virheellinen vastausarvo! Käytä lukua -5 ja +5 välillä.")
        return
    
    if not (1 <= confidence <= 5):
        click.echo("❌ Virheellinen varmuusarvo! Käytä lukua 1-5 välillä.")
        return
    
    manager = AnswerManager(election_id)
    success, result = manager.add_answer(candidate_id, question_id, answer, confidence, explanation_fi, explanation_en)
    
    if success:
        click.echo("✅ Vastaus lisätty!")
        click.echo(f"📊 Ehdokas: {candidate_id} → Kysymys: {question_id}")
        click.echo(f"🎯 Arvo: {answer}/5, Varmuus: {confidence}/5")
        if explanation_fi:
            click.echo(f"💬 Perustelu: {explanation_fi}")
    else:
        click.echo(f"❌ {result}")
