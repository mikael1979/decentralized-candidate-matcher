# src/core/sync/commands/publish_command.py
"""
Publish command - julkaise uusi arkisto.
"""
import click

from ..orchestrators import SyncCoordinator


def publish_command(election_id: str, force: bool = False, debug: bool = False):
    """Suorita publish-komento."""
    coordinator = SyncCoordinator(election_id=election_id, debug=debug)
    return coordinator.publish_new_archive(force)


@click.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--force', is_flag=True, help='Pakota julkaisu vaikka data ei olisi muuttunut')
@click.option('--debug', is_flag=True, help='Debug-tila')
def publish(election, force, debug):
    """Julkaise uusi arkisto."""
    publish_command(election, force, debug)
