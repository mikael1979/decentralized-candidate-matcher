# src/cli/sync_coordinator_refactored.py
"""
sync_coordinator.py - REFAKTOROITU VERSIO
Käyttää modulaarisia synkronointikomponentteja.
"""
#!/usr/bin/env python3
import sys
from pathlib import Path

# Lisää projektin juuri Python-polkuun
sys.path.insert(0, str(Path(__file__).parent.parent))

import click

# Tuo modulaariset komponentit suoraan
try:
    from core.sync.orchestrators import SyncCoordinator
    from core.sync.managers import IPFSManager, ArchiveManager, SyncManager
    MODULAR_SYNC_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Modular sync not available: {e}")
    MODULAR_SYNC_AVAILABLE = False


@click.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--publish', is_flag=True, help='Julkaise uusi arkisto')
@click.option('--sync', is_flag=True, help='Synkronoi uusimman arkiston mukaan')
@click.option('--status', is_flag=True, help='Näytä synkronointitila')
@click.option('--force', is_flag=True, help='Pakota julkaisu vaikka data ei olisi muuttunut')
@click.option('--debug', is_flag=True, help='Debug-tila')
def main(election, publish, sync, status, force, debug):
    """Synkronointikoordinaattori - refaktoroitu versio."""
    
    if not MODULAR_SYNC_AVAILABLE:
        print("❌ Modular sync components not available")
        return
    
    if debug:
        print("🐛 DEBUG-TILA")
        print("📦 Using modular sync components")
    
    coordinator = SyncCoordinator(election_id=election, debug=debug)
    
    if publish:
        success = coordinator.publish_new_archive(force)
        if success:
            print("✅ Publish completed successfully")
        else:
            print("❌ Publish failed")
    
    elif sync:
        success = coordinator.sync_to_latest()
        if success:
            print("✅ Sync completed successfully")
        else:
            print("❌ Sync failed")
    
    elif status:
        coordinator.show_sync_status()
    
    else:
        print("❌ Anna komento: --publish, --sync tai --status")
        print("💡 Kokeile: python src/cli/sync_coordinator_refactored.py --status --election Jumaltenvaalit2026")


if __name__ == "__main__":
    main()
