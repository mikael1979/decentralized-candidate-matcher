# src/core/sync/orchestrators/coordinator.py
"""
Pääkoordinaattori - yhdistää kaikki managerit.
"""
import click
from datetime import datetime
from typing import Optional

from ..managers import IPFSManager, ArchiveManager, SyncManager


class SyncCoordinator:
    """Synkronointikoordinaattori."""
    
    def __init__(self, election_id: str = "Jumaltenvaalit2026", debug: bool = False):
        self.election_id = election_id
        self.debug = debug
        self.ipfs = IPFSManager()
        self.archive = ArchiveManager(election_id)
        self.sync = SyncManager(election_id)
        
        if debug:
            self._print_debug_info()
    
    def _print_debug_info(self):
        """Tulosta debug-tiedot."""
        click.echo("🐛 DEBUG-TILA")
        click.echo(f"🌐 IPFS saatavilla: {self.ipfs.client is not None}")
        click.echo(f"🔗 IPFS yhteys: {self.ipfs.is_connected()}")
        click.echo(f"📁 Arkistotiedostot: {self.archive.count_data_files()}")
    
    def publish_new_archive(self, force: bool = False) -> bool:
        """Luo uusi arkisto ja päivitä synkronointilista."""
        click.echo(f"🔄 LUODAAN UUSI ARKISTO - {self.election_id}")
        
        # Tarkista onko data muuttunut
        if not force and not self.archive.has_data_changed():
            click.echo("ℹ️  Data ei ole muuttunut viime julkaisusta -- käytä --force pakottamiseen")
            return False
        
        # 1. Luo arkisto
        archive_data = self.archive.load_current_data()
        archive_cid = self.ipfs.add_data(archive_data, f"{self.election_id}_archive.json")
        
        if not archive_cid:
            click.echo("❌ Arkiston luonti epäonnistui")
            return False
        
        click.echo(f"   📊 Pakattu {len(archive_data['files'])} tiedostoa")
        click.echo(f"   💾 Koko: {len(str(archive_data)) / 1024:.1f} KB")
        
        # 2. Päivitä synkronointilista
        metadata = {
            "archive_size_bytes": len(str(archive_data).encode('utf-8')),
            "file_count": self.archive.count_data_files(),
            "ipfs_mode": self.ipfs.get_mode()
        }
        
        updated_sync_list = self.sync.update_sync_list(archive_cid, metadata, self.ipfs)
        sync_list_cid = self.sync.save_sync_list(updated_sync_list, self.ipfs)
        
        click.echo("✅ UUSI ARKISTO JULKAISTU!")
        click.echo(f"📦 Arkisto CID: {archive_cid}")
        click.echo(f"📋 Synkronointilista CID: {sync_list_cid}")
        click.echo(f"📁 Tiedostoja: {metadata['file_count']}")
        click.echo(f"🌐 IPFS-tila: {metadata['ipfs_mode']}")
        
        return True
    
    def sync_to_latest(self) -> bool:
        """Synkronoi uusimman arkiston mukaan."""
        click.echo(f"🔄 SYNKRONOIDAAN - {self.election_id}")
        
        # 1. Hae synkronointilista
        sync_list = self.sync.load_sync_list(self.ipfs)
        latest_cid = sync_list.get("latest_archive_cid")
        
        if not latest_cid:
            click.echo("❌ Ei arkistoja saatavilla")
            click.echo("💡 Luo ensin arkisto: python src/cli/sync_coordinator.py --publish --election Jumaltenvaalit2026")
            return False
        
        click.echo(f"   📦 Löytyi arkisto: {latest_cid}")
        
        # 2. Lataa ja pura arkisto
        archive_data = self.ipfs.get_data(latest_cid)
        if not archive_data:
            click.echo(f"❌ Arkistoa ei löydy: {latest_cid}")
            return False
        
        success = self.archive.unpack_archive(archive_data)
        
        if success:
            click.echo("✅ SYNKRONOINTI VALMIS!")
            click.echo(f"📊 Arkisto: {latest_cid}")
            click.echo(f"📅 Päivitetty: {sync_list.get('metadata', {}).get('timestamp', 'N/A')}")
            click.echo(f"🌐 Lähde: {sync_list.get('metadata', {}).get('ipfs_mode', 'UNKNOWN')}")
            return True
        else:
            click.echo("❌ Synkronointi epäonnistui")
            return False
    
    def show_sync_status(self):
        """Näytä synkronointitila."""
        sync_status = self.sync.get_sync_status(self.ipfs)
        
        click.echo(f"📋 SYNKRONOINTITILA - {self.election_id}")
        click.echo("=" * 50)
        
        latest_cid = sync_status.get('latest_archive_cid', 'Ei saatavilla')
        metadata = sync_status.get('metadata', {})
        ipfs_mode = metadata.get('ipfs_mode', 'UNKNOWN')
        
        click.echo(f"🆔 Viimeisin arkisto: {latest_cid}")
        click.echo(f"📅 Päivitetty: {metadata.get('timestamp', 'N/A')}")
        click.echo(f"📊 Tiedostoja: {metadata.get('file_count', 0)}")
        click.echo(f"📚 Historiaa: {sync_status.get('previous_archives_count', 0)} arkistoa")
        click.echo(f"🌐 IPFS-tila: {ipfs_mode}")
        
        sync_schedule = sync_status.get('sync_schedule', {})
        click.echo(f"🕒 Seuraava synkronointi: {sync_schedule.get('next_sync', 'N/A')}")
        
        if latest_cid != 'Ei saatavilla':
            click.echo(f"\n💡 Synkronoi: python src/cli/sync_coordinator.py --sync --election {self.election_id}")
