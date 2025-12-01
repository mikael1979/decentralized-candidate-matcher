#!/usr/bin/env python3
"""
Yksinkertainen päämoduuli config-hallinnalle.
"""
import sys
import click
from pathlib import Path

# Lisää projektin juuri Python-polkuun
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

@click.group()
def cli():
    """Config-tiedostojen hallinta TAQ-kvoorumilla"""
    pass

# Lisää tyhjä list-komento testaamista varten
@cli.command()
def list():
    """List configs"""
    click.echo("✅ Config list command works!")

@cli.command()
def info():
    """Show config info"""
    click.echo("✅ Config info command works!")

if __name__ == '__main__':
    cli()
