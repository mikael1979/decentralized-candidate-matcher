# src/cli/questions/commands/update_command.py
"""
Update question -komento.
"""
import click

from ..managers import QuestionManager


def update_question_command(election_id, question_identifier, question_fi, question_en, category, elo_rating):
    """Suorita update-komento."""
    if not any([question_fi, question_en, category, elo_rating]):
        print("❌ Anna vähintään yksi päivitettävä kenttä (--question-fi, --question-en, --category, --elo-rating)")
        return False
    
    manager = QuestionManager(election_id=election_id)
    
    success, result = manager.update_question(
        question_identifier=question_identifier,
        question_fi=question_fi,
        question_en=question_en,
        category=category,
        elo_rating=elo_rating
    )
    
    if success:
        print(f"✅ {result}")
        return True
    else:
        print(f"❌ {result}")
        return False


@click.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--question-identifier', required=True, help='Kysymyksen ID tai teksti')
@click.option('--question-fi', help='Uusi kysymys suomeksi')
@click.option('--question-en', help='Uusi kysymys englanniksi')
@click.option('--category', help='Uusi kategoria')
@click.option('--elo-rating', type=int, help='Uusi ELO-luokitus')
def update_command(election, question_identifier, question_fi, question_en, category, elo_rating):
    """Päivitä kysymys."""
    update_question_command(election, question_identifier, question_fi, question_en, category, elo_rating)
