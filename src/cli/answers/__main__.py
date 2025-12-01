#!/usr/bin/env python3
"""
Päämoduuli vastausten hallintaan - MODULAARINEN VERSIO
"""
import sys
import click
from pathlib import Path

# Lisää projektin juuri Python-polkuun
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from src.cli.answers.commands import (
        add_command,
        list_command,
        remove_command,
        update_command
    )
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


@click.group()
def cli():
    """Ehdokkaiden vastausten hallinta - modulaarinen versio"""
    pass


# Liitä komennot
cli.add_command(add_command, name='add')
cli.add_command(list_command, name='list')
cli.add_command(remove_command, name='remove')
cli.add_command(update_command, name='update')


if __name__ == '__main__':
    cli()
