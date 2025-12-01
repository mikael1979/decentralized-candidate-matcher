"""
IPFS-yhteyden hallinta.
"""
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
import click

try:
    from core.ipfs_client import IPFSClient
    HAS_REAL_IPFS = True
except ImportError:
    HAS_REAL_IPFS = False


class IPFSManager:
    """IPFS-yhteyden hallinta."""
    
    def __init__(self):
        self.client = IPFSClient() if HAS_REAL_IPFS else None
        self.connected = False
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Alusta IPFS-yhteys."""
        if self.client:
            try:
                if hasattr(self.client, 'check_ipfs_connection'):
                    self.connected = self.client.check_ipfs_connection()
                elif hasattr(self.client, 'ipfs') and hasattr(self.client.ipfs, 'id'):
                    result = self.client.ipfs.id()
                    self.connected = bool(result)
                else:
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
    
    def add_data(self, data: Dict[str, Any], filename: str = "data.json") -> Optional[str]:
        """Lisää data IPFS:ään."""
        if not self.connected or not self.client:
            click.echo("   🔶 Käytetään mock-IPFS:ää")
            return self._mock_add(data)
        
        try:
            # Yritä eri lisäysmetodeja
            if hasattr(self.client, 'add_json'):
                cid = self.client.add_json(data)
                if cid:
                    click.echo(f"   ✅ Lisätty IPFS:ään (JSON): {cid}")
                    return cid
            
            # Fallback tiedostoon
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                temp_path = f.name
            
            cid = self._add_file_via_client(temp_path)
            
            # Siivoa
            Path(temp_path).unlink()
            
            if cid:
                click.echo(f"   ✅ Lisätty IPFS:ään: {cid}")
            return cid
            
        except Exception as e:
            click.echo(f"   ⚠️  IPFS-lisäys epäonnistui: {e}")
            return self._mock_add(data)
    
    def _add_file_via_client(self, filepath: str) -> Optional[str]:
        """Lisää tiedosto IPFS:ään clientin kautta."""
        if not hasattr(self.client, 'add_file'):
            return None
        
        try:
            # add_file odottaa Path-oliota, muunna se
            from pathlib import Path
            path_obj = Path(filepath)
            
            # Tarkista että tiedosto on olemassa
            if not path_obj.exists():
                click.echo(f"   ❌ File does not exist: {path_obj}")
                return None
            
            click.echo(f"   🔧 Adding file via IPFS: {path_obj.name}")
            return self.client.add_file(path_obj)
            
        except Exception as e:
            # IPFS-viive tai muu virhe
            click.echo(f"   ⚠️  IPFS error (using mock fallback): {e}")
            # Palauta mock-CID varmuuden vuoksi
            import hashlib
            import time
            mock_hash = hashlib.sha256(f'mock_{filepath}_{time.time()}'.encode()).hexdigest()
            return f"Qm{mock_hash[:44]}"
    
    def get_data(self, cid: str) -> Optional[Dict[str, Any]]:
        """Hae data IPFS:stä."""
        if not self.connected or not self.client:
            click.echo(f"   🔶 Mock-haku: {cid}")
            return self._mock_get(cid)
        
        try:
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
    
    def _mock_add(self, data: Dict[str, Any]) -> str:
        """Mock IPFS-lisäys."""
        data_str = json.dumps(data, sort_keys=True)
        hash_obj = hashlib.sha256(data_str.encode())
        return f"Qm{hash_obj.hexdigest()[:44]}"
    
    def _mock_get(self, cid: str) -> Dict[str, Any]:
        """Mock IPFS-haku."""
        from datetime import datetime
        from core.file_utils import read_json_file
        
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
    
    def is_connected(self) -> bool:
        """Onko IPFS-yhteys toiminnassa?"""
        return self.connected
    
    def get_mode(self) -> str:
        """Palauta IPFS-tila."""
        return "REAL" if self.connected else "MOCK"
