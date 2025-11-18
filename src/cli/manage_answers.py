#!/usr/bin/env python3
import click
import json
from datetime import datetime
import os
import sys
from pathlib import Path

# LISÄTTY: Lisää src hakemisto Python-polkuun
sys.path.insert(0, str(Path(__file__).parent.parent))

"""
Ehdokkaiden vastausten hallinta - PÄIVITETTY MODULAARINEN VERSIO
Käyttää uusia modulaarisia komponentteja
"""
import click

# Tuodaan modulaariset komponentit
try:
    from src.cli.answer_commands import AnswerCommands
    from src.cli.answer_reports import AnswerReports
    from src.cli.answer_validation import AnswerValidation
except ImportError:
    from answer_commands import AnswerCommands
    from answer_reports import AnswerReports
    from answer_validation import AnswerValidation

@click.group()
def manage_answers():
    """Ehdokkaiden vastausten hallinta"""
    pass

@manage_answers.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--candidate-id', required=True, help='Ehdokkaan tunniste')
@click.option('--question-id', required=True, help='Kysymyksen tunniste')
@click.option('--answer', type=click.IntRange(-5, 5), required=True, help='Vastaus (-5 - +5)')
@click.option('--confidence', type=click.IntRange(1, 5), default=3, help='Varmuus taso (1-5)')
@click.option('--explanation-fi', help='Perustelu suomeksi')
@click.option('--explanation-en', help='Perustelu englanniksi')
@click.option('--explanation-sv', help='Perustelu ruotsiksi')
def add(election, candidate_id, question_id, answer, confidence, explanation_fi, explanation_en, explanation_sv):
    """Lisää ehdokkaan vastaus kysymykseen"""
    commands = AnswerCommands(election)
    commands.add_answer(candidate_id, question_id, answer, confidence, 
                       explanation_fi, explanation_en, explanation_sv)

@manage_answers.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--candidate-id', help='Näytä tietyn ehdokkaan vastaukset')
@click.option('--question-id', help='Näytä tietyn kysymyksen vastaukset')
def list(election, candidate_id, question_id):
    """Listaa ehdokkaiden vastaukset"""
    reports = AnswerReports(election)
    
    if candidate_id:
        reports.list_candidate_answers(candidate_id)
    elif question_id:
        reports.list_question_answers(question_id)
    else:
        reports.show_summary()

@manage_answers.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--candidate-id', required=True, help='Ehdokkaan tunniste')
@click.option('--question-id', required=True, help='Kysymyksen tunniste')
def remove(election, candidate_id, question_id):
    """Poista ehdokkaan vastaus"""
    commands = AnswerCommands(election)
    commands.remove_answer(candidate_id, question_id)

@manage_answers.command()
@click.option('--election', required=True, help='Vaalin tunniste')
def validate(election):
    """Validoi kaikki vastaukset"""
    validation = AnswerValidation(election)
    result = validation.validate_all_answers()
    
    click.echo("🔍 VASTAUSTEN VALIDOINTI")
    click.echo("=" * 50)
    click.echo(f"✅ Valideja vastauksia: {result['valid_answers']}")
    click.echo(f"❌ Virheellisiä vastauksia: {result['invalid_answers']}")
    click.echo(f"📊 Validius: {result['validity_percentage']:.1f}%")
    
    if result['issues']:
        click.echo("\n🚨 LÖYDETYT ONGELMAT:")
        for issue in result['issues'][:10]:  # Näytä vain 10 ensimmäistä
            click.echo(f"  {issue}")
        if len(result['issues']) > 10:
            click.echo(f"  ... ja {len(result['issues']) - 10} muuta ongelmaa")

@manage_answers.command()
@click.option('--election', required=True, help='Vaalin tunniste')
def check_consistency(election):
    """Tarkista vastausdatan eheys"""
    validation = AnswerValidation(election)
    result = validation.check_data_consistency()
    
    click.echo("🔍 DATA-EHEYDEN TARKISTUS")
    click.echo("=" * 50)
    
    if result['status'] == 'error':
        click.echo(f"❌ {result['message']}")
        return
    
    checks = result['checks']
    validation_result = result['validation']
    
    click.echo("📋 TARKISTUKSET:")
    click.echo(f"  {'✅' if checks['candidates_exist'] else '❌'} Ehdokkaita löytyy")
    click.echo(f"  {'✅' if checks['questions_exist'] else '❌'} Kysymyksiä löytyy")
    click.echo(f"  {'✅' if checks['answers_exist'] else '❌'} Vastauksia löytyy")
    click.echo(f"  {'✅' if checks['no_duplicate_answers'] else '❌'} Ei duplikaattivastauksia")
    click.echo(f"  {'✅' if checks['all_answers_valid'] else '❌'} Kaikki vastaukset validit")
    
    click.echo(f"\n📊 VALIDOINTITULOKSET:")
    click.echo(f"  Valideja: {validation_result['valid_answers']}")
    click.echo(f"  Virheellisiä: {validation_result['invalid_answers']}")
    
    if result['is_healthy']:
        click.echo("\n🎉 DATA ON EHJÄ JA VALIDI!")
    else:
        click.echo("\n⚠️  DATASSA ON ONGELMIA!")

if __name__ == '__main__':
    manage_answers()
