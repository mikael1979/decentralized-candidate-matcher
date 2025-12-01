# src/core/sync/__init__.py
"""
Synkronointimoduuli - hallitsee IPFS-synkronointia.
"""
import click

# Tuo komennot suoraan
try:
    from .commands.publish_command import publish, publish_command
    from .commands.sync_command import sync, sync_command
    from .commands.status_command import status, status_command
    COMMANDS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Sync commands not available: {e}")
    COMMANDS_AVAILABLE = False

# Luo CLI-ryhmä vain jos komennot ovat saatavilla
if COMMANDS_AVAILABLE:
    @click.group()
    def sync_cli():
        """Synkronointi - MODULAARINEN VERSIO"""
        pass
    
    sync_cli.add_command(publish, name='publish')
    sync_cli.add_command(sync, name='sync')
    sync_cli.add_command(status, name='status')
else:
    sync_cli = None

__version__ = '1.0.0'
