# src/core/ipfs/delta_manager.py
"""
Delta-päivitysten hallinta - lähettää vain muutokset täyden arkiston perusteella
"""
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional

class DeltaManager:
    """Hallitsee delta-päivityksiä täyden arkiston perusteella"""
    
    def __init__(self, client):
        self.client = client
    
    def create_delta_update(self, current_files: Dict[str, Dict], 
                          base_cid: str, 
                          base_hashes: Dict[str, str]) -> str:
        """
        Luo delta-päivitys perustuen edelliseen täyteen arkistoon
        
        Args:
            current_files: Nykyinen data
            base_cid: Täyden arkiston CID
            base_hashes: Täyden arkiston tiedostotiivisteet
            
        Returns:
            IPFS CID delta-päivitykselle
        """
        # Laske nykyiset tiivisteet
        current_hashes = self._calculate_file_hashes(current_files)
        
        # Etsi muuttuneet tiedostot
        changed_files = {}
        for filename, data in current_files.items():
            current_hash = current_hashes[filename]
            base_hash = base_hashes.get(filename)
            
            if base_hash != current_hash:
                changed_files[filename] = data
                print(f"   📝 {filename} changed: {base_hash[:8]}... → {current_hash[:8]}...")
        
        # Etsi poistetut tiedostot
        deleted_files = []
        for base_filename in base_hashes:
            if base_filename not in current_files:
                deleted_files.append(base_filename)
                print(f"   🗑️  {base_filename} deleted")
        
        # Luo delta
        delta = {
            "metadata": {
                "type": "delta_update",
                "version": "1.0",
                "timestamp": datetime.now().isoformat(),
                "base_cid": base_cid,
                "changed_count": len(changed_files),
                "deleted_count": len(deleted_files)
            },
            "changed_files": changed_files,
            "deleted_files": deleted_files,
            "current_hashes": current_hashes
        }
        
        delta_size = len(json.dumps(delta, ensure_ascii=False).encode('utf-8'))
        print(f"📋 Creating delta: {len(changed_files)} changed, {len(deleted_files)} deleted, "
              f"{delta_size} bytes")
        
        cid = self.client.add_json(delta)
        print(f"✅ Delta created: {cid}")
        
        return cid
    
    def apply_delta_update(self, base_files: Dict[str, Dict], delta_cid: str) -> Dict[str, Dict]:
        """
        Sovelta delta-päivitys täyteen arkistoon
        
        Args:
            base_files: Täyden arkiston data
            delta_cid: Delta-päivityksen CID
            
        Returns:
            Päivitetty data
        """
        print(f"📋 Applying delta: {delta_cid}")
        
        delta_data = self.client.get_json(delta_cid)
        
        if delta_data.get("metadata", {}).get("type") != "delta_update":
            raise ValueError(f"CID {delta_cid} is not a delta update")
        
        # Alusta tulos täydellä arkistolla
        result_files = base_files.copy()
        
        # Päivitä muuttuneet tiedostot
        changed_files = delta_data.get("changed_files", {})
        for filename, new_data in changed_files.items():
            result_files[filename] = new_data
            print(f"   🔄 Updated: {filename}")
        
        # Poista poistetut tiedostot
        deleted_files = delta_data.get("deleted_files", [])
        for filename in deleted_files:
            if filename in result_files:
                del result_files[filename]
                print(f"   🗑️  Deleted: {filename}")
        
        # Varmista eheys
        expected_hashes = delta_data.get("current_hashes", {})
        current_hashes = self._calculate_file_hashes(result_files)
        
        for filename, expected_hash in expected_hashes.items():
            if current_hashes.get(filename) != expected_hash:
                raise ValueError(f"Integrity check failed for {filename}")
        
        print(f"✅ Delta applied: {len(result_files)} files total")
        return result_files
    
    def _calculate_file_hashes(self, data_files: Dict[str, Dict]) -> Dict[str, str]:
        """Laske tiedostojen SHA-256 tiivisteet"""
        hashes = {}
        for filename, data in data_files.items():
            content = json.dumps(data, sort_keys=True, ensure_ascii=False)
            file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            hashes[filename] = file_hash
        return hashes
    
    def calculate_delta_size_saving(self, current_files: Dict[str, Dict], 
                                  base_hashes: Dict[str, str]) -> Dict[str, Any]:
        """
        Laske kuinka paljon delta säästää tilaa
        
        Returns:
            Säästötilastot
        """
        current_hashes = self._calculate_file_hashes(current_files)
        
        # Laske täyden arkiston koko
        full_size = len(json.dumps(current_files, ensure_ascii=False).encode('utf-8'))
        
        # Laske deltan koko
        changed_files = {}
        for filename, data in current_files.items():
            current_hash = current_hashes[filename]
            if base_hashes.get(filename) != current_hash:
                changed_files[filename] = data
        
        deleted_files = [f for f in base_hashes if f not in current_files]
        
        delta = {
            "changed_files": changed_files,
            "deleted_files": deleted_files
        }
        delta_size = len(json.dumps(delta, ensure_ascii=False).encode('utf-8'))
        
        saving_percent = ((full_size - delta_size) / full_size) * 100 if full_size > 0 else 0
        
        return {
            "full_size_bytes": full_size,
            "delta_size_bytes": delta_size,
            "saving_bytes": full_size - delta_size,
            "saving_percent": saving_percent,
            "changed_files": len(changed_files),
            "deleted_files": len(deleted_files)
        }
