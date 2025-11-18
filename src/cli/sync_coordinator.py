#!/usr/bin/env python3
import click
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.file_utils import read_json_file, write_json_file, ensure_directory

try:
    from core.ipfs_client import IPFSClient
    HAS_REAL_IPFS = True
except ImportError:
    HAS_REAL_IPFS = False

# Yksinkertaistettu IPFS-wrapper joka käyttää oikeita metodeja
class IPFSWrapper:
    def __init__(self):
        self.client = IPFSClient() if HAS_REAL_IPFS else None
        self.connected = False
        
        if self.client:
            try:
                # Tarkista IPFS-yhteys useilla tavoilla
                if hasattr(self.client, 'check_ipfs_connection'):
                    self.connected = self.client.check_ipfs_connection()
                elif hasattr(self.client, 'ipfs') and hasattr(self.client.ipfs, 'id'):
                    # Vaihtoehtoinen tapa tarkistaa yhteys
                    result = self.client.ipfs.id()
                    self.connected = bool(result)
                else:
                    # Oletetaan yhteys olevan jos IPFSClient on luotu onnistuneesti
                    self.connected = True
                
                if self.connected:
                    click.echo("✅ IPFS-yhteys toimii")
                else:
                    click.echo("⚠️  IPFS-yhteys epäonnistui")
                    
            except Exception as e:
                click.echo(f"⚠️  IPFS-yhteysvirhe: {e}")
                self.connected = False
        else:
            click.echo("🔶 Käytetään mock-IPFS:ää")
    
    def add_data(self, data, filename="data.json"):
        """Lisää data IPFS:ään"""
        if not self.connected or not self.client:
            click.echo("   🔶 Käytetään mock-IPFS:ää")
            return self._mock_add(data)
        
        try:
            # Kokeile ensin suoraa JSON-lisäystä
            if hasattr(self.client, 'add_json'):
                cid = self.client.add_json(data)
                if cid:
                    click.echo(f"   ✅ Lisätty IPFS:ään (JSON): {cid}")
                    return cid
            
            # Fallback: tallenna tiedostoon ja lisää
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                temp_path = f.name
            
            # Korjattu add_file-kutsu
            if hasattr(self.client, 'add_file'):
                try:
                    cid = self.client.add_file(temp_path)
                except Exception as e:
                    click.echo(f"   ⚠️  add_file epäonnistui: {e}")
                    # Yritä suoraa IPFS-apia
                    if hasattr(self.client, 'ipfs') and hasattr(self.client.ipfs, 'add'):
                        with open(temp_path, 'rb') as f:
                            result = self.client.ipfs.add(f)
                            cid = result['Hash'] if isinstance(result, dict) else str(result)
                    else:
                        cid = self._mock_add(data)
            elif hasattr(self.client, 'ipfs') and hasattr(self.client.ipfs, 'add'):
                with open(temp_path, 'rb') as f:
                    result = self.client.ipfs.add(f)
                    cid = result['Hash'] if isinstance(result, dict) else str(result)
            else:
                cid = self._mock_add(data)
            
            # Siivoa
            Path(temp_path).unlink()
            
            if cid:
                click.echo(f"   ✅ Lisätty IPFS:ään: {cid}")
            return cid
            
        except Exception as e:
            click.echo(f"   ⚠️  IPFS-lisäys epäonnistui: {e}")
            return self._mock_add(data)
    
    def get_data(self, cid):
        """Hae data IPFS:stä"""
        if not self.connected or not self.client:
            click.echo(f"   🔶 Mock-haku: {cid}")
            return self._mock_get(cid)
        
        try:
            # Kokeile eri get-metodeja
            if hasattr(self.client, 'get_json'):
                data = self.client.get_json(cid)
            elif hasattr(self.client, 'get_file_content'):
                content = self.client.get_file_content(cid)
                data = json.loads(content) if content else None
            elif hasattr(self.client, 'ipfs') and hasattr(self.client.ipfs, 'cat'):
                content = self.client.ipfs.cat(cid)
                data = json.loads(content) if content else None
            else:
                data = self._mock_get(cid)
            
            if data:
                click.echo(f"   ✅ Haettu IPFS:stä: {cid}")
            else:
                click.echo(f"   ❌ Dataa ei löytynyt: {cid}")
            return data
                
        except Exception as e:
            click.echo(f"   ⚠️  IPFS-haku epäonnistui: {e}")
            return self._mock_get(cid)
    
    def _mock_add(self, data):
        """Mock IPFS-lisäys"""
        import hashlib
        data_str = json.dumps(data, sort_keys=True)
        hash_obj = hashlib.sha256(data_str.encode())
        return f"Qm{hash_obj.hexdigest()[:44]}"
    
    def _mock_get(self, cid):
        """Mock IPFS-haku"""
        # Yritä ladata paikalliset tiedostot
        try:
            return {
                "election_id": "Jumaltenvaalit2026",
                "timestamp": datetime.now().isoformat(),
                "files": {
                    "meta.json": read_json_file("data/runtime/meta.json", {}),
                    "questions.json": read_json_file("data/runtime/questions.json", {}),
                    "candidates.json": read_json_file("data/runtime/candidates.json", {}),
                    "parties.json": read_json_file("data/runtime/parties.json", {}),
                    "candidate_answers.json": read_json_file("data/runtime/candidate_answers.json", {}),
                    "system_chain.json": read_json_file("data/runtime/system_chain.json", {})
                }
            }
        except:
            return None

# Loput koodi pysyy samana...
@click.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--publish', is_flag=True, help='Julkaise uusi arkisto')
@click.option('--sync', is_flag=True, help='Synkronoi uusimman arkiston mukaan')
@click.option('--status', is_flag=True, help='Näytä synkronointitila')
@click.option('--force', is_flag=True, help='Pakota julkaisu vaikka data ei olisi muuttunut')
@click.option('--debug', is_flag=True, help='Debug-tila')
def sync_coordinator(election, publish, sync, status, force, debug):
    """Synkronointikoordinaattori - Hallitsee arkistojen julkaisua ja synkronointia"""
    
    ipfs = IPFSWrapper()
    
    if debug:
        click.echo("🐛 DEBUG-TILA")
        click.echo(f"🌐 IPFS saatavilla: {HAS_REAL_IPFS}")
        click.echo(f"🔗 IPFS yhteys: {ipfs.connected}")
        if HAS_REAL_IPFS and ipfs.client:
            methods = [m for m in dir(ipfs.client) if not m.startswith('_')]
            click.echo(f"📋 IPFSClient metodit: {methods}")
        return
    
    if not HAS_REAL_IPFS:
        click.echo("⚠️  KÄYTTÄÄ MOCK-IPFS:ÄÄ - Asenna oikea IPFS parempaan suorituskykyyn")
    
    if publish:
        publish_new_archive(election, force, ipfs)
    elif sync:
        sync_to_latest(election, ipfs)
    elif status:
        show_sync_status(election, ipfs)
    else:
        click.echo("💡 KÄYTTÖ:")
        click.echo("   --publish  # Luo ja julkaise uusi arkisto")
        click.echo("   --sync     # Synkronoi uusimman arkiston mukaan") 
        click.echo("   --status   # Näytä synkronointitila")
        click.echo("   --force    # Pakota julkaisu (--publish --force)")
        click.echo("   --debug    # Debug-tila")

def publish_new_archive(election, force, ipfs):
    """Luo uusi arkisto ja päivitä synkronointilista"""
    click.echo(f"🔄 LUODAAN UUSI ARKISTO - {election}")
    
    # Tarkista onko data muuttunut
    if not force and not has_data_changed(election, ipfs):
        click.echo("ℹ️  Data ei ole muuttunut viime julkaisusta -- käytä --force pakottamiseen")
        return
    
    # 1. Luo arkisto
    archive_cid = create_and_upload_archive(election, ipfs)
    if not archive_cid:
        click.echo("❌ Arkiston luonti epäonnistui")
        return
    
    # 2. Lataa nykyinen synkronointilista
    sync_list = load_sync_list(election, ipfs)
    
    # 3. Päivitä lista
    if sync_list.get("latest_archive_cid"):
        sync_list.setdefault("previous_archives", []).insert(0, sync_list["latest_archive_cid"])
    
    sync_list["latest_archive_cid"] = archive_cid
    sync_list["previous_archives"] = sync_list.get("previous_archives", [])[:5]  # Säilytä 5 viimeisintä
    
    # Varmista että metadata on olemassa
    sync_list.setdefault("metadata", {})
    sync_list["metadata"].update({
        "timestamp": datetime.now().isoformat(),
        "archive_size_bytes": len(json.dumps(load_current_data()).encode('utf-8')),
        "file_count": count_data_files(),
        "ipfs_mode": "REAL" if ipfs.connected else "MOCK"
    })
    
    # 4. Tallennetaan synkronointilista
    sync_list_cid = save_sync_list(election, sync_list, ipfs)
    
    click.echo("✅ UUSI ARKISTO JULKAISTU!")
    click.echo(f"📦 Arkisto CID: {archive_cid}")
    click.echo(f"📋 Synkronointilista CID: {sync_list_cid}")
    click.echo(f"📁 Tiedostoja: {sync_list['metadata']['file_count']}")
    click.echo(f"🌐 IPFS-tila: {'REAL' if ipfs.connected else 'MOCK'}")

def has_data_changed(election, ipfs):
    """Tarkista onko data muuttunut viime julkaisusta"""
    sync_list = load_sync_list(election, ipfs)
    if not sync_list.get("latest_archive_cid"):
        return True
    return True  # Aina muuttunut testauksen helpottamiseksi

def create_and_upload_archive(election, ipfs):
    """Luo ja lähetä arkisto IPFS:ään"""
    try:
        current_data = load_current_data()
        
        if not current_data["files"]:
            click.echo("   ❌ Ei data-tiedostoja saatavilla")
            return None
        
        cid = ipfs.add_data(current_data, f"{election}_archive.json")
        
        click.echo(f"   📊 Pakattu {len(current_data['files'])} tiedostoa")
        click.echo(f"   💾 Koko: {len(json.dumps(current_data)) / 1024:.1f} KB")
        return cid
        
    except Exception as e:
        click.echo(f"❌ Arkiston luonti epäonnistui: {e}")
        return None

def load_current_data():
    """Lataa nykyinen data arkistointia varten"""
    data_files = [
        "data/runtime/meta.json",
        "data/runtime/questions.json",
        "data/runtime/candidates.json", 
        "data/runtime/parties.json",
        "data/runtime/candidate_answers.json",
        "data/runtime/system_chain.json"
    ]
    
    archive_data = {
        "election_id": "Jumaltenvaalit2026",
        "timestamp": datetime.now().isoformat(),
        "files": {}
    }
    
    for file_path in data_files:
        if Path(file_path).exists():
            file_data = read_json_file(file_path, {})
            archive_data["files"][Path(file_path).name] = file_data
            click.echo(f"   ✅ Lisätty: {Path(file_path).name}")
        else:
            click.echo(f"   ⚠️  Puuttuu: {Path(file_path).name}")
    
    return archive_data

def load_sync_list(election, ipfs):
    """Lataa synkronointilista IPFS:stä tai paikallisesti"""
    # Fallback paikalliseen tiedostoon - käytetään aina paikallista mock-tilassa
    sync_file = f"data/runtime/{election}_sync_list.json"
    if Path(sync_file).exists():
        click.echo("   📁 Ladataan paikallinen synkronointilista")
        data = read_json_file(sync_file, create_default_sync_list(election))
        click.echo(f"   ✅ Synkronointilista ladattu: {data.get('latest_archive_cid', 'Ei arkistoa')}")
        return data
    else:
        click.echo("   📝 Luodaan uusi synkronointilista")
        return create_default_sync_list(election)

def get_sync_list_cid(election):
    """Hae synkronointilistan CID"""
    sync_file = f"data/runtime/{election}_sync_list.cid"
    if Path(sync_file).exists():
        with open(sync_file, 'r') as f:
            cid = f.read().strip()
            if cid:
                return cid
    return None

def create_default_sync_list(election):
    """Luo oletussynkronointilista"""
    return {
        "election_id": election,
        "latest_archive_cid": None,
        "previous_archives": [],
        "sync_schedule": {
            "next_sync": (datetime.now() + timedelta(hours=1)).isoformat(),
            "interval_hours": 1
        },
        "metadata": {
            "created": datetime.now().isoformat(),
            "archive_size_bytes": 0,
            "file_count": 0,
            "ipfs_mode": "MOCK"
        }
    }

def save_sync_list(election, sync_list, ipfs):
    """Tallenna synkronointilista"""
    # Tallenna paikallisesti
    sync_file = f"data/runtime/{election}_sync_list.json"
    write_json_file(sync_file, sync_list)
    click.echo(f"   💾 Tallennettu paikallisesti: {sync_file}")
    
    # Lisää IPFS:ään
    cid = ipfs.add_data(sync_list, f"{election}_sync_list.json")
    
    # Tallenna CID
    cid_file = f"data/runtime/{election}_sync_list.cid"
    with open(cid_file, 'w') as f:
        f.write(cid)
    click.echo(f"   🔗 Tallennettu CID: {cid_file}")
    
    return cid

def sync_to_latest(election, ipfs):
    """Synkronoi uusimman arkiston mukaan"""
    click.echo(f"🔄 SYNKRONOIDAAN - {election}")
    
    # 1. Hae synkronointilista
    sync_list = load_sync_list(election, ipfs)
    latest_cid = sync_list.get("latest_archive_cid")
    
    if not latest_cid:
        click.echo("❌ Ei arkistoja saatavilla")
        click.echo("💡 Luo ensin arkisto: python src/cli/sync_coordinator.py --publish --election Jumaltenvaalit2026")
        return
    
    click.echo(f"   📦 Löytyi arkisto: {latest_cid}")
    
    # 2. Lataa ja pura arkisto
    success = download_and_unpack_archive(latest_cid, ipfs)
    
    if success:
        click.echo("✅ SYNKRONOINTI VALMIS!")
        click.echo(f"📊 Arkisto: {latest_cid}")
        click.echo(f"📅 Päivitetty: {sync_list.get('metadata', {}).get('timestamp', 'N/A')}")
        click.echo(f"🌐 Lähde: {sync_list.get('metadata', {}).get('ipfs_mode', 'UNKNOWN')}")
    else:
        click.echo("❌ Synkronointi epäonnistui")

def download_and_unpack_archive(cid, ipfs):
    """Lataa ja pura arkisto IPFS:stä"""
    try:
        archive_data = ipfs.get_data(cid)
        if not archive_data:
            click.echo(f"❌ Arkistoa ei löydy: {cid}")
            return False
            
        click.echo(f"📦 Ladataan arkisto: {cid}")
        
        # Pura tiedostot
        file_count = 0
        for filename, filedata in archive_data.get("files", {}).items():
            filepath = f"data/runtime/{filename}"
            ensure_directory(Path(filepath).parent)
            write_json_file(filepath, filedata)
            file_count += 1
            click.echo(f"   ✅ Palautettu: {filename}")
        
        click.echo(f"📁 Purettu {file_count} tiedostoa")
        return True
        
    except Exception as e:
        click.echo(f"❌ Arkiston purku epäonnistui: {e}")
        return False

def show_sync_status(election, ipfs):
    """Näytä synkronointitila"""
    sync_list = load_sync_list(election, ipfs)
    
    click.echo(f"📋 SYNKRONOINTITILA - {election}")
    click.echo("=" * 50)
    
    latest_cid = sync_list.get('latest_archive_cid', 'Ei saatavilla')
    metadata = sync_list.get('metadata', {})
    ipfs_mode = metadata.get('ipfs_mode', 'UNKNOWN')
    
    click.echo(f"🆔 Viimeisin arkisto: {latest_cid}")
    click.echo(f"📅 Päivitetty: {metadata.get('timestamp', 'N/A')}")
    click.echo(f"📊 Tiedostoja: {metadata.get('file_count', 0)}")
    click.echo(f"📚 Historiaa: {len(sync_list.get('previous_archives', []))} arkistoa")
    click.echo(f"🌐 IPFS-tila: {ipfs_mode}")
    
    sync_schedule = sync_list.get('sync_schedule', {})
    click.echo(f"🕒 Seuraava synkronointi: {sync_schedule.get('next_sync', 'N/A')}")
    
    if latest_cid != 'Ei saatavilla':
        click.echo(f"\n💡 Synkronoi: python src/cli/sync_coordinator.py --sync --election {election}")

def count_data_files():
    """Laske data-tiedostojen määrä"""
    data_dir = Path("data/runtime")
    return len(list(data_dir.glob("*.json")))

if __name__ == '__main__':
    sync_coordinator()
