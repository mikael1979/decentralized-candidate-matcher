# src/cli/manage_taq_config.py
#!/usr/bin/env python3
import click
import json
from pathlib import Path

@click.group()
def taq_config():
    """TAQ-konfiguraation hallinta"""
    pass

@taq_config.command()
def show_config():
    """Näytä nykyinen TAQ-konfiguraatio"""
    config_path = Path("config/system/trusted_sources.json")
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
            click.echo(json.dumps(config, indent=2, ensure_ascii=False))
    else:
        click.echo("❌ trusted_sources.json ei löydy")

@taq_config.command()
@click.option('--domain', required=True, help='Domain-nimi')
@click.option('--source-type', required=True, help='Mediatyyppi (newspapers/international/online_media/community)')
def add_media_source(domain, source_type):
    """Lisää uusi media-lähde"""
    # Toteutus konfiguraation päivittämiseksi
    pass
