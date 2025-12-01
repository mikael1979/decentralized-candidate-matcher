"""
List answers -komento.
"""
import click
import sys
from pathlib import Path

# Lisää projektin juuri Python-polkuun
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from core import get_election_id
from core.file_utils import read_json_file
from src.cli.answers.managers import AnswerManager


@click.command()
@click.option('--election', required=False, help='Vaalin tunniste (valinnainen, käytetään configista)')
@click.option('--candidate-id', help='Näytä vain tietyn ehdokkaan vastaukset')
def list_command(election, candidate_id):
    """Listaa vastaukset"""
    election_id = get_election_id(election)
    if not election_id:
        click.echo("❌ Vaali-ID:tä ei annettu eikä config tiedostoa löydy.")
        return
    
    manager = AnswerManager(election_id)
    
    if candidate_id:
        answers = manager.list_answers(candidate_id)
        if answers:
            click.echo(f"📝 EHDOKKAAN {candidate_id} VASTAUKSET")
            click.echo("=" * 50)
            for answer in answers:
                click.echo(f"❓ Kysymys: {answer.get('question_id')}")
                click.echo(f"📊 Vastaus: {answer.get('value')}/5")
                click.echo(f"🎯 Varmuus: {answer.get('confidence')}/5")
                if answer.get('explanation_fi'):
                    click.echo(f"💬 Perustelu: {answer.get('explanation_fi')}")
                click.echo("-" * 30)
        else:
            click.echo(f"❌ Ehdokkaalla {candidate_id} ei ole vastauksia")
    else:
        stats = manager.get_answer_stats()
        click.echo("📊 EHDOKKAIDEN VASTAUSYHTEENVETO")
        click.echo("=" * 50)
        
        # Lataa ehdokkaat nimille
        candidates_file = Path(manager.data_path) / "candidates.json"
        candidate_names = {}
        if candidates_file.exists():
            candidates_data = read_json_file(candidates_file)
            for candidate in candidates_data.get("candidates", []):
                candidate_names[candidate["id"]] = candidate.get("name_fi", candidate.get("name_en", "Nimetön"))
        
        answers = manager.list_answers()
        candidates_answers = {}
        
        for answer in answers:
            candidate_id = answer["candidate_id"]
            if candidate_id not in candidates_answers:
                candidates_answers[candidate_id] = 0
            candidates_answers[candidate_id] += 1
        
        # Näytä kaikki ehdokkaat
        for candidate_id, name in candidate_names.items():
            answer_count = candidates_answers.get(candidate_id, 0)
            status = "✅" if answer_count > 0 else "❌"
            click.echo(f"{status} {name} ({candidate_id}): {answer_count} vastausta")
        
        click.echo(f"\n📈 YHTEENVETO:")
        click.echo(f"   Ehdokkaita: {stats['total_candidates']}")
        click.echo(f"   Vastanneita: {stats['candidates_with_answers']}")
        click.echo(f"   Vastauksia yhteensä: {stats['total_answers']}")
        click.echo(f"   Vastauskattavuus: {stats['answer_coverage']}%")
