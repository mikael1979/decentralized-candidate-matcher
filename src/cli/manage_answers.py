# src/cli/questions/__init__.py
"""
Päämoduuli kysymysten hallinnalle - yhdistää kaikki komponentit.
"""
import sys
from pathlib import Path
import click

# Lisää src hakemisto Python-polkuun
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from core import get_election_id
    CORE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Core modules not available: {e}")
    CORE_AVAILABLE = False

from src.cli.questions.commands import (
    add_command,
    remove_command,
    update_command,
    list_command,
    add_question_command,
    remove_question_command,
    update_question_command,
    list_questions_command
)

# MULTINODE: Tuo uudet moduulit
try:
    from nodes.core.node_identity import NodeIdentity
    from nodes.core.network_manager import NetworkManager
    from nodes.protocols.consensus import ConsensusManager
    MULTINODE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Multinode modules not available: {e}")
    MULTINODE_AVAILABLE = False


@click.group()
def questions_cli():
    """Kysymysten hallinta - MODULAARINEN VERSIO"""
    pass


# Rekisteröi komennot
questions_cli.add_command(add_command, name='add')
questions_cli.add_command(remove_command, name='remove')
questions_cli.add_command(update_command, name='update')
questions_cli.add_command(list_command, name='list')


# Pääfunktio yhteensopivuuden säilyttämiseksi
@click.command()
@click.option('--election', required=False, help='Vaalin tunniste (valinnainen, käytetään configista)')
@click.option('--add', is_flag=True, help='Lisää uusi kysymys')
@click.option('--remove', help='Poista kysymys (ID tai teksti)')
@click.option('--update', help='Päivitä kysymys (ID tai teksti)')
@click.option('--list', 'list_questions', is_flag=True, help='Listaa kaikki kysymykset')
@click.option('--question-fi', help='Kysymys suomeksi')
@click.option('--question-en', help='Kysymys englanniksi')
@click.option('--category', help='Kysymyksen kategoria')
@click.option('--elo-rating', type=int, help='ELO-luokitus')
@click.option('--enable-multinode', is_flag=True, help='Ota multinode käyttöön')
@click.option('--bootstrap-debug', is_flag=True, help='Käytä debug-bootstrap peeritä')
def manage_questions(election, add, remove, update, list_questions, question_fi, question_en, 
                     category, elo_rating, enable_multinode, bootstrap_debug):
    """Kysymysten hallinta - YHTEENSOPIVA MODULAARINEN VERSIO"""
    
    if not CORE_AVAILABLE:
        print("❌ Core modules not available")
        return
    
    # Hae election_id configista jos parametria ei annettu
    election_id = get_election_id(election)
    if not election_id:
        print("❌ Vaali-ID:tä ei annettu eikä config tiedostoa löydy.")
        print("💡 Käytä: --election VAALI_ID tai asenna järjestelmä ensin: python src/cli/install.py --first-install")
        return
    
    # MULTINODE: Tarkista saatavuus
    if enable_multinode and not MULTINODE_AVAILABLE:
        print("❌ Multinode requested but modules not available")
        click.confirm("Continue without multinode?", abort=True)
        enable_multinode = False
    
    # Käytä uusia modulaarisia komentoja
    if add:
        if not question_fi:
            print("❌ --question-fi vaaditaan uuden kysymyksen lisäämiseksi")
            return
        
        success = add_question_command(
            election_id=election_id,
            question_fi=question_fi,
            question_en=question_en,
            category=category,
            elo_rating=elo_rating
        )
        # MULTINODE: Toteuta tarvittaessa
        if enable_multinode:
            print("ℹ️  Multinode-tuki tulee myöhemmin")
    
    elif remove:
        if not remove:
            print("❌ --remove vaaditaan kysymyksen poistamiseksi")
            return
        
        success = remove_question_command(
            election_id=election_id,
            question_identifier=remove
        )
    
    elif update:
        if not update:
            print("❌ --update vaaditaan kysymyksen päivittämiseksi")
            return
        
        if not any([question_fi, question_en, category, elo_rating]):
            print("❌ Anna vähintään yksi päivitettävä kenttä (--question-fi, --question-en, --category, --elo-rating)")
            return
        
        success = update_question_command(
            election_id=election_id,
            question_identifier=update,
            question_fi=question_fi,
            question_en=question_en,
            category=category,
            elo_rating=elo_rating
        )
    
    elif list_questions:
        success = list_questions_command(
            election_id=election_id,
            category_filter=category
        )
        
        # MULTINODE: Lisää tilastot tarvittaessa
        if enable_multinode:
            print("ℹ️  Multinode-tilastot tulevat myöhemmin")
    
    else:
        print("❌ Anna komento: --add, --remove, --update tai --list")
        print("💡 Kokeile: python src/cli/manage_questions.py --list")
        if MULTINODE_AVAILABLE:
            print("🌐 Multinode: python src/cli/manage_questions.py --list --enable-multinode")


# Mahdollisuus suorittaa suoraan
if __name__ == "__main__":
    manage_questions()
