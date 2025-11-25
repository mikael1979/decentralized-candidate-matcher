"""
PÄÄMODUULI - CONFIG CLI
Click-komentojen hallinta modulaarisessa rakenteessa
"""
import click

# Importoi kaikki komennot
from src.cli.config.commands.propose_command import propose_update
from src.cli.config.commands.vote_command import vote
from src.cli.config.commands.status_command import status
from src.cli.config.commands.list_command import list
from src.cli.config.commands.get_command import config_info
from src.cli.config.commands.export_command import history
from src.cli.config.utils.cli_helpers import help

@click.group()
def manage_config():
    """Config-tiedostojen hallinta TAQ-kvoorumilla"""
    pass

# Lisää komennot manage_config-ryhmään

@manage_config.command()
@click.option('--election', required=False, help='Vaalitunniste')
@click.option('--key', required=True, help='Päivitettävä config-avain')
@click.option('--value', required=True, help='Uusi arvo')
@click.option('--type', 'update_type', required=True, 
              type=click.Choice(['minor', 'major', 'emergency']),
              help='Päivitystyyppi')
@click.option('--justification', required=True, help='Muutoksen perustelu')
@click.option('--node-id', required=True, help='Ehdotuksen tekijän node-id')
def propose_update_command(election, key, value, update_type, justification, node_id):
    """Ehdotta config-päivitystä TAQ-kvoorumille"""
    propose_update(election, key, value, update_type, justification, node_id)

@manage_config.command()
@click.option('--election', required=False, help='Vaalitunniste')
@click.option('--proposal-id', required=True, help='Päivitysehdotuksen ID')
@click.option('--vote', type=click.Choice(['approve', 'reject', 'abstain']), required=True)
@click.option('--node-id', required=True, help='Äänestäjän node-id')
@click.option('--justification', help='Äänestysperustelu')
def vote_command(election, proposal_id, vote, node_id, justification):
    """Äänestä config-päivitysehdotuksesta"""
    vote(election, proposal_id, vote, node_id, justification)

@manage_config.command()
@click.option('--election', required=False, help='Vaalitunniste')
@click.option('--proposal-id', help='Näytä tietyn ehdotuksen tila')
@click.option('--verbose', '-v', is_flag=True, help='Näytä yksityiskohtainen tila')
def status_command(election, proposal_id, verbose):
    """Näytä config-päivitysten tila"""
    status(election, proposal_id, verbose)

@manage_config.command()
@click.option('--election', required=False, help='Vaalitunniste')
def list_command(election):
    """Listaa kaikki config-päivitysehdotukset"""
    list(election)

@manage_config.command()
@click.option('--election', required=False, help='Vaalitunniste')
def config_info_command(election):
    """Näytä config-tiedoston perustiedot"""
    config_info(election)

@manage_config.command()
@click.option('--election', required=False, help='Vaalitunniste')
def history_command(election):
    """Näytä config-päivityshistoria"""
    history(election)

@manage_config.command()
def help_command():
    """Näytä käyttöohjeet"""
    help()

if __name__ == '__main__':
    manage_config()
