#!/usr/bin/env python3
import click
import json
from datetime import datetime
import os
import sys
from pathlib import Path

# LISÄTTY: Lisää src hakemisto Python-polkuun
sys.path.insert(0, str(Path(__file__).parent.parent))

import click
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from managers.elo_manager import ELOManager

@click.group()
def elo_admin():
    """ELO-luokituksen hallintatyökalu"""
    pass

@elo_admin.command()
@click.option('--election', required=True, help='Vaalin tunniste')
def stats(election):
    """Näytä ELO-tilastot"""
    elo = ELOManager(election)
    stats = elo.get_question_stats()
    
    click.echo("📊 ELO-LUOKITUSTILASTOT")
    click.echo("=" * 50)
    click.echo(f"Kysymyksiä yhteensä: {stats['total_questions']}")
    click.echo(f"Keskimääräinen luokitus: {stats['average_rating']}")
    click.echo(f"Korkein luokitus: {stats['max_rating']}")
    click.echo(f"Matalin luokitus: {stats['min_rating']}")
    
    click.echo()
    click.echo("🏆 TOP 10 KYSYMYS:")
    for i, question in enumerate(stats['questions'][:10], 1):
        delta_str = f" ({question['delta']:+.0f})" if question['delta'] != 0 else ""
        click.echo(f"{i:2d}. [{question['rating']:4d}{delta_str}] {question['question']}")

@elo_admin.command()
@click.option('--election', required=True, help='Vaalin tunniste')
def leaderboard(election):
    """Näytä ranking-lista"""
    elo = ELOManager(election)
    leaderboard = elo.get_leaderboard()
    
    click.echo("🏆 ELO-RANKINGLISTA")
    click.echo("=" * 50)
    
    for i, question in enumerate(leaderboard, 1):
        delta_str = f" ({question['delta']:+.0f})" if question['delta'] != 0 else ""
        click.echo(f"{i:2d}. ⭐ {question['rating']:4d}{delta_str} | {question['category']:12} | {question['question']}")

@elo_admin.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.confirmation_option(prompt='Haluatko varmasti nollata kaikki ELO-luokitukset?')
def reset(election):
    """Nollaa kaikki ELO-luokitukset"""
    elo = ELOManager(election)
    count = elo.reset_ratings()
    
    click.echo(f"✅ ELO-luokitukset nollattu {count} kysymykselle")
    click.echo("📊 Kaikki kysymykset palautettu 1000 pisteen luokitukseen")

if __name__ == '__main__':
    elo_admin()
