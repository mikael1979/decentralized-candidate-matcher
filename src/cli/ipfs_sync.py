#!/usr/bin/env python3
import click
import json
from datetime import datetime
import os
import sys
from pathlib import Path

# LISÄTTY: Lisää src hakemisto Python-polkuun
sys.path.insert(0, str(Path(__file__).parent.parent))

"""
IPFS-synkronoinnin CLI-työkalu Jumaltenvaaleille
"""
import click
import json
import sys
import os
from datetime import datetime

# Lisää src-hakemisto Python-polkuun
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

@click.group()
def ipfs_sync():
    """IPFS-synkronoinnin hallinta Jumaltenvaaleille"""
    pass

@ipfs_sync.command()
@click.option('--election', default='Jumaltenvaalit2026', help='Vaalin tunniste')
def full_sync(election):
    """Suorita täysi IPFS-synkronointi"""
    from managers.ipfs_sync_manager import IPFSSyncManager
    
    sync_manager = IPFSSyncManager(election)
    report = sync_manager.full_sync()
    
    click.echo("📊 IPFS-SYNKRONOINTIRAPORTTI:")
    click.echo(f"   Vaali: {report['election_id']}")
    click.echo(f"   Tyyppi: {report['sync_type']}")
    click.echo(f"   Aikaleima: {report['timestamp'][:19]}")
    click.echo(f"   Synkronoidut tiedostot: {report['files_synced']}")
    
    click.echo("\n🔗 IPFS-CID:t:")
    for file_type, cid in report['ipfs_cids'].items():
        click.echo(f"   {file_type}: {cid}")

@ipfs_sync.command() 
@click.option('--election', default='Jumaltenvaalit2026', help='Vaalin tunniste')
def incremental(election):
    """Suorita inkrementaalinen IPFS-synkronointi"""
    from managers.ipfs_sync_manager import IPFSSyncManager
    
    sync_manager = IPFSSyncManager(election)
    report = sync_manager.incremental_sync()
    
    if report['status'] == 'no_changes':
        click.echo("✅ Ei muutoksia synkronoitavaksi")
        return
    
    click.echo("📊 INKREMENTAALINEN SYNKRONOINTI:")
    click.echo(f"   Muuttuneet tiedostot: {len(report['changed_files'])}")
    click.echo(f"   Päivitetyt CID:t: {len(report['ipfs_cids'])}")

@ipfs_sync.command()
@click.option('--election', default='Jumaltenvaalit2026', help='Vaalin tunniste')  
def verify(election):
    """Varmista IPFS-synkronoinnin eheys"""
    from managers.ipfs_sync_manager import IPFSSyncManager
    
    sync_manager = IPFSSyncManager(election)
    report = sync_manager.verify_sync_integrity()
    
    click.echo("🔍 IPFS-EHEYSTARKISTUS:")
    click.echo(f"   Tarkistetut tiedostot: {report['total_files']}")
    click.echo(f"   Valideja tiedostoja: {report['valid_files']}")
    
    click.echo("\n📋 Yksityiskohtaiset tulokset:")
    for file_type, result in report['results'].items():
        status_icon = "✅" if result == "valid" else "❌" if result == "invalid" else "⚠️"
        click.echo(f"   {status_icon} {file_type}: {result}")

@ipfs_sync.command()
@click.option('--election', default='Jumaltenvaalit2026', help='Vaalin tunniste')
def status(election):
    """Näytä IPFS-synkronoinnin tila"""
    sync_file = f"data/runtime/ipfs_sync.json"
    
    try:
        with open(sync_file, 'r') as f:
            sync_data = json.load(f)
        
        click.echo("📡 IPFS-SYNKRONOINTITILA:")
        click.echo(f"   Vaali: {sync_data['election_id']}")
        click.echo(f"   Viimeisin synkronointi: {sync_data['timestamp'][:19]}")
        click.echo(f"   Synkronointityyppi: {sync_data['sync_type']}")
        
        click.echo("\n🔗 Julkaistut CID:t:")
        for file_type, cid in sync_data.get('ipfs_cids', {}).items():
            click.echo(f"   {file_type}: {cid}")
            
    except FileNotFoundError:
        click.echo("❌ IPFS-synkronointitietoja ei löytynyt")
        click.echo("💡 Suorita ensin: python src/cli/ipfs_sync.py full-sync")

if __name__ == '__main__':
    ipfs_sync()
