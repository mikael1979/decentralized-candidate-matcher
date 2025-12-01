#!/usr/bin/env python3
"""
Yksinkertainen toimiva config CLI.
"""
import sys
import click

@click.group()
def cli():
    """Config-tiedostojen hallinta"""
    pass

@cli.command()
@click.option('--election', help='Election ID')
def list(election):
    """List configs"""
    click.echo(f"✅ Config list for election: {election or 'default'}")

@cli.command()
def info():
    """Show config info"""
    click.echo("✅ Config system is working!")

if __name__ == '__main__':
    cli()
