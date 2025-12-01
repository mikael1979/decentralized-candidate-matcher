# src/core/sync/managers/archive_manager.py
"""
Arkiston hallinta - luo, lataa ja hallinnoi arkistoja.
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import click

from core.file_utils import read_json_file, write_json_file, ensure_directory


class ArchiveManager:
    """Arkiston hallinta."""
    
    def __init__(self, election_id: str = "Jumaltenvaalit2026"):
        self.election_id = election_id
        self.data_dir = Path("data/runtime")
    
    def load_current_data(self) -> Dict[str, Any]:
        """Lataa nykyinen data arkistointia varten."""
        data_files = [
            "meta.json",
            "questions.json", 
            "candidates.json",
            "parties.json",
            "candidate_answers.json",
            "system_chain.json"
        ]
        
        archive_data = {
            "election_id": self.election_id,
            "timestamp": datetime.now().isoformat(),
            "files": {}
        }
        
        for filename in data_files:
            file_path = self.data_dir / filename
            if file_path.exists():
                file_data = read_json_file(str(file_path), {})
                archive_data["files"][filename] = file_data
                click.echo(f"   ✅ Lisätty: {filename}")
            else:
                click.echo(f"   ⚠️  Puuttuu: {filename}")
        
        return archive_data
    
    def unpack_archive(self, archive_data: Dict[str, Any]) -> bool:
        """Pura arkisto tiedostoiksi."""
        try:
            file_count = 0
            for filename, filedata in archive_data.get("files", {}).items():
                filepath = self.data_dir / filename
                ensure_directory(filepath.parent)
                write_json_file(str(filepath), filedata)
                file_count += 1
                click.echo(f"   ✅ Palautettu: {filename}")
            
            click.echo(f"📁 Purettu {file_count} tiedostoa")
            return True
            
        except Exception as e:
            click.echo(f"❌ Arkiston purku epäonnistui: {e}")
            return False
    
    def count_data_files(self) -> int:
        """Laske data-tiedostojen määrä."""
        return len(list(self.data_dir.glob("*.json")))
    
    def has_data_changed(self, last_archive_timestamp: Optional[str] = None) -> bool:
        """Tarkista onko data muuttunut viime julkaisusta."""
        # Yksinkertaistettu - aina palautetaan True testauksen helpottamiseksi
        # Todellisessa käytössä voitaisiin vertailla timestampeja tai hash-eja
        return True
    
    def get_data_files_info(self) -> Dict[str, Any]:
        """Hae data-tiedostojen tiedot."""
        files_info = {}
        for json_file in self.data_dir.glob("*.json"):
            try:
                data = read_json_file(str(json_file), {})
                files_info[json_file.name] = {
                    "size_bytes": len(json.dumps(data).encode('utf-8')),
                    "modified": datetime.fromtimestamp(json_file.stat().st_mtime).isoformat(),
                    "entries": len(data) if isinstance(data, dict) else 0
                }
            except Exception as e:
                click.echo(f"⚠️  Virhe tiedostossa {json_file.name}: {e}")
        
        return files_info
