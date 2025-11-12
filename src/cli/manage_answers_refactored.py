#!/usr/bin/env python3
import click
from datetime import datetime
from src.cli.base_cli import BaseCLI

@click.group()
def manage_answers():
    """Ehdokkaiden vastausten hallinta (refaktoroitu)"""
    pass

class AnswerManagerCLI(BaseCLI):
    def add_answer(self, candidate_id, question_id, answer_value, confidence, explanations):
        """Lisää vastaus (refaktoroitu)"""
        # Käytä data_manager ja validator -ei toistuvaa koodia
        if not self.validator.validate_candidate_exists(candidate_id, self.data_manager):
            raise ValueError(f"Ehdokas {candidate_id} ei ole olemassa")
        
        # ... lyhennetty refaktoroitu logiikka
        pass

@manage_answers.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--candidate-id', required=True, help='Ehdokkaan tunniste')
def list_answers(election, candidate_id):
    """Listaa vastaukset (refaktoroitu)"""
    cli = AnswerManagerCLI(election)
    cli.validate_election()
    
    # Käytä yhteisiä metodeja
    answers = cli.list_answers(candidate_id)
    # ... näytä tulokset
