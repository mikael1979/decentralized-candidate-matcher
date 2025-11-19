# src/core/ipfs/archive_manager.py
"""
Täyden arkistojen hallinta - käytetään vain ensimmäisellä synkronoinnilla
"""
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

class ArchiveManager:
    """Hallitsee täyden IPFS-arkistojen luomista ja purkamista"""
    
    def __init__(self, client):
        self.client = client
    
    def create_full_archive(self, data_files: Dict[str, Dict]) -> str:
        """
        Luo täyden arkiston kaikesta datasta
        
        Args:
            data_files: Sanakirja tiedostonimi -> data
            
        Returns:
            IPFS CID arkistolle
        """
        archive = {
            "metadata": {
                "type": "full_archive",
                "version": "1.0",
                "timestamp": datetime.now().isoformat(),
                "file_count": len(data_files),
                "total_size": self._calculate_total_size(data_files)
            },
            "files": data_files,
            "file_hashes": self._calculate_file_hashes(data_files)
        }
        
        print(f"📦 Creating full archive: {archive['metadata']['file_count']} files, "
              f"{archive['metadata']['total_size']} bytes")
        
        cid = self.client.add_json(archive)
        print(f"✅ Full archive created: {cid}")
        
        return cid
    
    def extract_full_archive(self, cid: str) -> Dict[str, Any]:
        """
        Pura täysi arkisto IPFS:stä
        
        Args:
            cid: IPFS CID arkistolle
            
        Returns:
            Purettu data sanakirjana
        """
        print(f"📦 Extracting full archive: {cid}")
        
        archive_data = self.client.get_json(cid)
        
        if archive_data.get("metadata", {}).get("type") != "full_archive":
            raise ValueError(f"CID {cid} is not a full archive")
        
        files = archive_data.get("files", {})
        print(f"✅ Extracted {len(files)} files from archive")
        
        return files
    
    def _calculate_total_size(self, data_files: Dict[str, Dict]) -> int:
        """Laske datan kokonaiskoko tavuina"""
        total_size = 0
        for filename, data in data_files.items():
            content = json.dumps(data, ensure_ascii=False)
            total_size += len(content.encode('utf-8'))
        return total_size
    
    def _calculate_file_hashes(self, data_files: Dict[str, Dict]) -> Dict[str, str]:
        """Laske tiedostojen SHA-256 tiivisteet"""
        hashes = {}
        for filename, data in data_files.items():
            content = json.dumps(data, sort_keys=True, ensure_ascii=False)
            file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            hashes[filename] = file_hash
            
            print(f"   🔍 {filename}: {file_hash[:16]}...")
        
        return hashes
    
    def verify_archive_integrity(self, cid: str, expected_files: list) -> bool:
        """
        Tarkista arkiston eheys
        
        Args:
            cid: IPFS CID arkistolle
            expected_files: Odotetut tiedostojen nimet
            
        Returns:
            True jos arkisto on ehjä
        """
        try:
            archive_data = self.client.get_json(cid)
            files = archive_data.get("files", {})
            
            # Tarkista että kaikki odotetut tiedostot ovat läsnä
            for expected_file in expected_files:
                if expected_file not in files:
                    print(f"❌ Missing file in archive: {expected_file}")
                    return False
            
            # Tarkista tiivisteet
            current_hashes = self._calculate_file_hashes(files)
            stored_hashes = archive_data.get("file_hashes", {})
            
            for filename, current_hash in current_hashes.items():
                if stored_hashes.get(filename) != current_hash:
                    print(f"❌ Hash mismatch for {filename}")
                    return False
            
            print(f"✅ Archive integrity verified: {cid}")
            return True
            
        except Exception as e:
            print(f"❌ Archive verification failed: {e}")
            return False
