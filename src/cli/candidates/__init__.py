"""
PÄÄMODUULI - CANDIDATES CLI
Click-komentojen hallinta modulaarisessa rakenteessa
"""
import click
import sys
import os
from pathlib import Path

# Lisää src hakemisto Python-polkuun
current_dir = Path(__file__).parent.parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Importoi kaikki komennot
from src.cli.candidates.commands.add_command import add_candidate
from src.cli.candidates.commands.remove_command import remove_candidate
from src.cli.candidates.commands.update_command import update_candidate
from src.cli.candidates.commands.list_command import list_candidates
from src.cli.candidates.commands.status_command import change_candidate_status

@click.command()
@click.option('--election', required=False, help='Vaalin tunniste (valinnainen, käytetään configista)')
@click.option('--add', is_flag=True, help='Lisää uusi ehdokas')
@click.option('--remove', help='Poista ehdokas (ID tai nimi)')
@click.option('--update', help='Päivitä ehdokas (ID tai nimi)')
@click.option('--list', 'list_candidates_flag', is_flag=True, help='Listaa kaikki ehdokkaat')
@click.option('--name-fi', help='Ehdokkaan nimi suomeksi')
@click.option('--name-en', help='Ehdokkaan nimi englanniksi')
@click.option('--party', help='Puolue')
@click.option('--domain', help='Alue/domain')
@click.option('--inactive', is_flag=True, help='Merkitse ehdokas epäaktiiviseksi')
@click.option('--active', is_flag=True, help='Merkitse ehdokas aktiiviseksi')
@click.option('--enable-multinode', is_flag=True, help='Ota multinode käyttöön')
@click.option('--bootstrap-debug', is_flag=True, help='Käytä debug-bootstrap peeritä')
def manage_candidates(election, add, remove, update, list_candidates_flag, name_fi, name_en, party, domain, inactive, active, enable_multinode, bootstrap_debug):
    """Ehdokkaiden hallinta"""
    
    # Käytä configista saatavaa vaalitunnistetta jos ei annettu
    from src.core.config_manager import get_election_id
    election_id = election or get_election_id()
    
    if not election_id:
        click.echo("❌ Vaalia ei ole asetettu")
        return
    
    # Suorita komento
    if add:
        success = add_candidate(election_id, name_fi, name_en, party, domain)
    elif remove:
        success = remove_candidate(election_id, remove)
    elif update:
        success = update_candidate(election_id, update, name_fi, name_en, party, domain)
    elif list_candidates_flag:
        success = list_candidates(election_id)
    elif inactive:
        success = change_candidate_status(election_id, name_fi or party or domain, active=False)
    elif active:
        success = change_candidate_status(election_id, name_fi or party or domain, active=True)
    else:
        click.echo("ℹ️  Käytä --help nähdäksesi käytettävissä olevat komennot")
        success = False
    
    return success

if __name__ == '__main__':
    manage_candidates()
