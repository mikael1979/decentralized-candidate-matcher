# src/cli/questions/commands/list_command.py
"""
List questions -komento.
"""
import click

from ..managers import QuestionManager
from ..utils.formatters import format_question_list, format_stats


def list_questions_command(election_id, category_filter):
    """Suorita list-komento."""
    manager = QuestionManager(election_id=election_id)
    
    questions = manager.list_questions(category_filter)
    stats = manager.get_question_stats()
    
    # Käytä formattereita
    formatted_list = format_question_list(questions, election_id=election_id)
    formatted_stats = format_stats(stats)
    
    print(formatted_list)
    print(formatted_stats)
    
    return True


@click.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--category', help='Suodata kategorian mukaan')
def list_command(election, category):
    """Listaa kysymykset."""
    list_questions_command(election, category)
