"""
cli_helpers.py - Config CLI apufunktiot
"""
import click
from src.core.config_manager import ConfigManager

def help():
    """Näytä käyttöohjeet"""
    click.echo("🎯 CONFIG-HALLINNAN KÄYTTÖOHJEET")
    click.echo("=" * 40)
    click.echo("📋 propose-update - Ehdotta config-muutosta")
    click.echo("📋 vote          - Äänestä ehdotuksesta")
    click.echo("📋 status        - Näytä ehdotusten tila")
    click.echo("📋 list          - Listaa kaikki ehdotukset")
    click.echo("📋 config-info   - Näytä nykyinen config")
    click.echo("📋 history       - Näytä päivityshistoria")
