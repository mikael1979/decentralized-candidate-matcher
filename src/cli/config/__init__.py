"""
PÄÄMODUULI - CONFIG CLI
Click-komentojen hallinta modulaarisessa rakenteessa
"""
import click

# Importoi kaikki komennot
from src.cli.config.commands.propose_command import propose_update
from src.cli.config.commands.vote_command import vote
from src.cli.config.commands.status_command import status
from src.cli.config.commands.list_command import list_configs_configs  # Muutettu list -> list_configs
from src.cli.config.commands.get_command import config_info
from src.cli.config.commands.export_command import history
from src.cli.config.utils.cli_helpers import help

@click.group()
def manage_config():
    """Config-tiedostojen hallinta TAQ-kvoorumilla"""
    pass

# Liitä komennot
manage_config.add_command(propose_update, name='propose')
manage_config.add_command(vote, name='vote')
manage_config.add_command(status, name='status')
manage_config.add_command(list_configs, name='list')
manage_config.add_command(config_info, name='info')
manage_config.add_command(history, name='history')

# Lisää help-komento erikseen
manage_config.add_command(help, name='help')
