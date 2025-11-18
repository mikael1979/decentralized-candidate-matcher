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
Analytics ja tilastotyökalu
"""
import click
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from managers.analytics_manager import AnalyticsManager
from core.error_handling import handle_file_errors, validate_election_exists

@click.group()
def analytics():
    """Analytics ja tilastotyökalut"""
    pass

@analytics.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@handle_file_errors
def stats(election):
    """Näytä järjestelmän tilastot"""
    validate_election_exists(election)
    
    manager = AnalyticsManager(election)
    stats = manager.get_system_stats()
    
    click.echo("📊 JÄRJESTELMÄTILASTOT")
    click.echo("=" * 60)
    
    click.echo(f"🏛️  Vaali: {stats['election_id']}")
    click.echo(f"🕒 Luotu: {stats['generated_at'][:16]}")
    click.echo()
    
    # Sisältötilastot
    content = stats['content_stats']
    click.echo("📈 SISÄLLÖN TILASTOT:")
    click.echo(f"   ❓ Kysymyksiä: {content.get('questions', 0)}")
    if 'avg_elo_rating' in content:
        click.echo(f"   ⭐ Keskim. ELO: {content['avg_elo_rating']} ({content['min_elo_rating']}-{content['max_elo_rating']})")
    
    click.echo(f"   👑 Ehdokkaita: {content.get('candidates', 0)}")
    click.echo(f"   📝 Vastauksia: {content.get('total_answers', 0)}")
    if 'answer_coverage_percent' in content:
        click.echo(f"   🎯 Vastauskattavuus: {content['answer_coverage_percent']}%")
    
    click.echo(f"   🏛️  Puolueita: {content.get('parties', 0)}")
    click.echo(f"   ✅ Vahvistettuja: {content.get('verified_parties', 0)}")
    click.echo(f"   ⏳ Odottavia: {content.get('pending_parties', 0)}")

@analytics.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@handle_file_errors
def health(election):
    """Näytä järjestelmän terveysraportti"""
    validate_election_exists(election)
    
    manager = AnalyticsManager(election)
    report = manager.generate_health_report()
    
    click.echo("🏥 JÄRJESTELMÄN TERVEYSRAPORTTI")
    click.echo("=" * 60)
    
    health_icon = "✅" if report["system_health"] == "healthy" else "⚠️"
    click.echo(f"{health_icon} Tila: {report['system_health']}")
    click.echo()
    
    if report["issues"]:
        click.echo("🚨 LÖYDETYT ONGELMAT:")
        for issue in report["issues"]:
            click.echo(f"   • {issue}")
        click.echo()
    
    if report["recommendations"]:
        click.echo("💡 SUOSITUKSET:")
        for recommendation in report["recommendations"]:
            click.echo(f"   • {recommendation}")
        click.echo()
    
    # Näytä kysymysten analytics
    if report.get("question_analytics"):
        qa = report["question_analytics"]
        click.echo("📊 KYSYMYSTEN ANALYTICS:")
        click.echo(f"   Yhteensä: {qa['total_questions']} kysymystä")
        
        click.echo("   🏷️  Kategoriat:")
        for category, count in qa["categories"].items():
            click.echo(f"      • {category}: {count} kysymystä")
        
        click.echo("   🏆 TOP 5 KYSYMYSTÄ:")
        for q in qa["elo_distribution"]["top_5"]:
            click.echo(f"      ⭐ {q['rating']} - {q['question']}")

@analytics.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--output', help='Tallenna raportti tiedostoon')
@handle_file_errors
def report(election, output):
    """Luo kattava analytics-raportti"""
    validate_election_exists(election)
    
    manager = AnalyticsManager(election)
    stats = manager.get_system_stats()
    question_analytics = manager.get_question_analytics()
    health_report = manager.generate_health_report()
    
    full_report = {
        "metadata": {
            "election_id": election,
            "generated_at": stats["generated_at"],
            "report_type": "full_analytics"
        },
        "system_stats": stats,
        "question_analytics": question_analytics,
        "health_report": health_report
    }
    
    if output:
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(full_report, f, indent=2, ensure_ascii=False)
        click.echo(f"✅ Raportti tallennettu: {output}")
    else:
        click.echo(json.dumps(full_report, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    analytics()
