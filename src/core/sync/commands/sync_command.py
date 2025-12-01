# src/core/sync/commands/sync_command.py
"""
Sync command - synkronoi uusimman arkiston mukaan.
"""
import click

from ..orchestrators import SyncCoordinator


def sync_command(election_id: str, debug: bool = False):
    """Suorita sync-komento."""
    coordinator = SyncCoordinator(election_id=election_id, debug=debug)
    return coordinator.sync_to_latest()


@click.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--debug', is_flag=True, help='Debug-tila')
def sync(election, debug):
    """Synkronoi uusimman arkiston mukaan."""
    sync_command(election, debug)
