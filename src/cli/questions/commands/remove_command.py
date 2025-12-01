# src/cli/questions/commands/remove_command.py
"""
Remove question -komento.
"""
import click

from ..managers import QuestionManager


def remove_question_command(election_id, question_identifier):
    """Suorita remove-komento."""
    manager = QuestionManager(election_id=election_id)
    
    success, result = manager.remove_question(question_identifier)
    
    if success:
        print(f"✅ {result}")
        return True
    else:
        print(f"❌ {result}")
        return False


@click.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--question-identifier', required=True, help='Kysymyksen ID tai teksti')
def remove_command(election, question_identifier):
    """Poista kysymys."""
    remove_question_command(election, question_identifier)
