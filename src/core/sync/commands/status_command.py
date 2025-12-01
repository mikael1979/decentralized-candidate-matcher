# src/core/sync/commands/status_command.py
"""
Status command - näytä synkronointitila.
"""
import click

from ..orchestrators import SyncCoordinator


def status_command(election_id: str, debug: bool = False):
    """Suorita status-komento."""
    coordinator = SyncCoordinator(election_id=election_id, debug=debug)
    coordinator.show_sync_status()


@click.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--debug', is_flag=True, help='Debug-tila')
def status(election, debug):
    """Näytä synkronointitila."""
    status_command(election, debug)
