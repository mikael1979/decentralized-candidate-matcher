#!/usr/bin/env python3
"""
Päämoduuli config-hallinnalle - MODULAARINEN VERSIO
"""
import sys
import click
from pathlib import Path

# Lisää projektin juuri Python-polkuun
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from src.cli.config.commands.propose_command import propose_update
    from src.cli.config.commands.vote_command import vote
    from src.cli.config.commands.status_command import status
    from src.cli.config.commands.list_command import list_configs  # Oikea nimi
    from src.cli.config.commands.get_command import config_info
    from src.cli.config.commands.export_command import history
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


@click.group()
def cli():
    """Config-tiedostojen hallinta TAQ-kvoorumilla"""
    pass


# Liitä komennot
cli.add_command(propose_update, name='propose')
cli.add_command(vote, name='vote')
cli.add_command(status, name='status')
cli.add_command(list_configs, name='list')
cli.add_command(config_info, name='info')
cli.add_command(history, name='history')


if __name__ == '__main__':
    cli()
