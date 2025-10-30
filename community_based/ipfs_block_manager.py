#!/usr/bin/env python3
# ipfs_block_manager.py
"""
IPFS Block Manager - Hallinnoi pyöriviä varauslohkoja IPFS:ssä
Käyttö:
  manager = IPFSBlockManager(ipfs_client, "election_2024")
  entry_id = manager.write_to_block("active", data, "normal_backup")
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import hashlib

class IPFSBlockManager:
    """Hallinnoi pyöriviä varauslohkoja IPFS:ssä usealle nodelle"""
    
    def __init__(self, ipfs_client, election_id: str, node_id: str = "default_node"):
        self.ipfs_client = ipfs_client
        self.election_id = election_id
        self.node_id = node_id
        self.blocks_metadata_cid = None
        
        # Lohkojen määritelmät
        self.blocks_config = {
            "buffer1": {
                "purpose": "empty_buffer",
                "max_size": 100,
                "time_window": None,
                "priority": "low",
                "allowed_operations": ["read", "archive"]
            },
            "urgent": {
                "purpose": "emergency_backups", 
                "max_size": 50,
                "time_window": 3600,  # 1 tunti
                "priority": "critical",
                "allowed_operations": ["read", "write", "emergency"]
            },
            "sync": {
                "purpose": "synchronization_point",
                "max_size": 200,
                "time_window": 21600,  # 6 tuntia
                "priority": "high", 
                "allowed_operations": ["read", "write", "sync"]
            },
            "active": {
                "purpose": "active_writing",
                "max_size": 150,
                "time_window": 7200,  # 2 tuntia
                "priority": "medium",
                "allowed_operations": ["read", "write"]
            },
            "buffer2": {
                "purpose": "transfer_buffer",
                "max_size": 100,
                "time_window": None,
                "priority": "low",
                "allowed_operations": ["read", "archive"]
            }
        }
        
        # Lohkojen järjestys
        self.block_sequence = ["buffer1", "urgent", "sync", "active", "buffer2"]
    
    def initialize_blocks(self) -> str:
        """Alusta lohkorakenne IPFS:ään"""
        
        block_cids = {}
        
        for block_name, config in self.blocks_config.items():
            block_data = {
                "metadata": {
                    "block_name": block_name,
                    "purpose": config["purpose"],
                    "created": datetime.now().isoformat(),
                    "max_size": config["max_size"],
                    "time_window": config["time_window"],
                    "election_id": self.election_id,
                    "node_id": self.node_id
                },
                "entries": [],
                "current_index": 0,
                "total_entries": 0,
                "entry_hashes": []  # Tarkistusta varten
            }
            
            cid = self.ipfs_client.upload(block_data)
            block_cids[block_name] = cid
            print(f"✅ Lohko alustettu: {block_name} -> {cid}")
        
        # Luo metadata-tiedosto
        blocks_metadata = {
            "version": "1.0.0",
            "created": datetime.now().isoformat(),
            "election_id": self.election_id,
            "node_id": self.node_id,
            "block_sequence": self.block_sequence,
            "current_rotation": 0,
            "total_rotations": 0,
            "blocks": block_cids,
            "rotation_history": [],
            "node_registry": [self.node_id]  # Rekisteröi ensimmäinen node
        }
        
        self.blocks_metadata_cid = self.ipfs_client.upload(blocks_metadata)
        print(f"🎯 Lohkometadata luotu: {self.blocks_metadata_cid}")
        
        return self.blocks_metadata_cid
    
    def write_to_block(self, block_name: str, data: Dict, data_type: str, 
                      priority: str = "normal") -> str:
        """Kirjoita dataa tiettyyn lohkoon"""
        
        if block_name not in self.blocks_config:
            raise ValueError(f"Tuntematon lohko: {block_name}")
        
        # Lataa metadata
        blocks_metadata = self._load_blocks_metadata()
        block_cid = blocks_metadata["blocks"][block_name]
        
        # Lataa lohkon data
        block_data = self.ipfs_client.download(block_cid)
        if not block_data:
            raise BlockNotFoundError(f"Lohkoa ei löydy: {block_cid}")
        
        # Tarkista lohkon tilaa
        if self._is_block_full(block_data, block_name):
            if block_name == "active":
                print("🔄 Aktiivinen lohko täynnä, pyöritetään lohkoja...")
                self._rotate_blocks()
                # Lataa uusi aktiivinen lohko
                blocks_metadata = self._load_blocks_metadata()
                block_cid = blocks_metadata["blocks"][block_name]
                block_data = self.ipfs_client.download(block_cid)
            else:
                raise BlockFullError(f"Lohko {block_name} on täynnä")
        
        # Luo uusi merkintä
        entry_id = f"{block_name}_{block_data['current_index']}_{self.node_id}"
        entry_hash = self._calculate_entry_hash(data)
        
        new_entry = {
            "entry_id": entry_id,
            "timestamp": datetime.now().isoformat(),
            "data_type": data_type,
            "node_id": self.node_id,
            "priority": priority,
            "data": data,
            "entry_hash": entry_hash
        }
        
        # Lisää lohkoon
        block_data["entries"].append(new_entry)
        block_data["current_index"] += 1
        block_data["total_entries"] = len(block_data["entries"])
        block_data["entry_hashes"].append(entry_hash)
        
        # Päivitä lohko IPFS:ään
        new_block_cid = self.ipfs_client.upload(block_data)
        
        # Päivitä metadata
        blocks_metadata["blocks"][block_name] = new_block_cid
        self.blocks_metadata_cid = self.ipfs_client.upload(blocks_metadata)
        
        print(f"📝 Kirjoitettu lohkoon {block_name}: {entry_id}")
        return entry_id
    
    def read_from_block(self, block_name: str, entry_id: str = None) -> List[Dict]:
        """Lue dataa lohkosta"""
        
        blocks_metadata = self._load_blocks_metadata()
        block_cid = blocks_metadata["blocks"][block_name]
        block_data = self.ipfs_client.download(block_cid)
        
        if not block_data:
            return []
        
        if entry_id:
            # Etsi tietty merkintä
            for entry in block_data["entries"]:
                if entry["entry_id"] == entry_id:
                    return [entry]
            return []
        else:
            # Palauta kaikki merkinnät
            return block_data["entries"]
    
    def get_block_status(self, block_name: str = None) -> Dict:
        """Hae lohkon/lohkojen status"""
        
        blocks_metadata = self._load_blocks_metadata()
        
        if block_name:
            # Yksittäisen lohkon status
            block_cid = blocks_metadata["blocks"][block_name]
            block_data = self.ipfs_client.download(block_cid)
            
            return {
                "block_name": block_name,
                "purpose": self.blocks_config[block_name]["purpose"],
                "current_entries": len(block_data["entries"]),
                "max_size": self.blocks_config[block_name]["max_size"],
                "usage_percentage": (len(block_data["entries"]) / self.blocks_config[block_name]["max_size"]) * 100,
                "last_updated": block_data["entries"][-1]["timestamp"] if block_data["entries"] else "Ei merkintöjä"
            }
        else:
            # Kaikkien lohkojen status
            status = {}
            for block_name in self.block_sequence:
                block_cid = blocks_metadata["blocks"][block_name]
                block_data = self.ipfs_client.download(block_cid)
                
                status[block_name] = {
                    "purpose": self.blocks_config[block_name]["purpose"],
                    "entries": len(block_data["entries"]),
                    "max_size": self.blocks_config[block_name]["max_size"],
                    "full": len(block_data["entries"]) >= self.blocks_config[block_name]["max_size"]
                }
            
            return status
    
    def _rotate_blocks(self):
        """Pyöritä lohkoja kun aktiivinen lohko täyttyy"""
        
        blocks_metadata = self._load_blocks_metadata()
        old_sequence = blocks_metadata["block_sequence"]
        
        print(f"🔄 Pyöritetään lohkoja: {old_sequence}")
        
        # Uusi sekvenssi: siirrä kaikkia yksi asema eteenpäin
        new_sequence = old_sequence[1:] + [old_sequence[0]]
        
        # 1. Arkistoi vanha aktiivinen lohko (entinen active -> uusi buffer2)
        old_active_cid = blocks_metadata["blocks"]["active"]
        old_active_data = self.ipfs_client.download(old_active_cid)
        
        archive_entry = {
            "archive_timestamp": datetime.now().isoformat(),
            "original_block": "active",
            "total_entries": len(old_active_data["entries"]),
            "entry_ids": [entry["entry_id"] for entry in old_active_data["entries"]]
        }
        
        # Kirjoita arkistoi buffer2:een
        self.write_to_block("buffer2", archive_entry, "block_archive", "low")
        
        # 2. Siirrä sync -> active (tyhjennä ensin)
        sync_cid = blocks_metadata["blocks"]["sync"]
        sync_data = self.ipfs_client.download(sync_cid)
        sync_data["metadata"]["purpose"] = "active_writing"
        sync_data["entries"] = []  # Tyhjennä uusi aktiivinen lohko
        sync_data["current_index"] = 0
        sync_data["total_entries"] = 0
        sync_data["entry_hashes"] = []
        new_active_cid = self.ipfs_client.upload(sync_data)
        
        # 3. Siirrä urgent -> sync (säilytä data)
        urgent_cid = blocks_metadata["blocks"]["urgent"]
        urgent_data = self.ipfs_client.download(urgent_cid)
        urgent_data["metadata"]["purpose"] = "synchronization_point"
        new_sync_cid = self.ipfs_client.upload(urgent_data)
        
        # 4. Siirrä buffer1 -> urgent (tyhjennä)
        buffer1_cid = blocks_metadata["blocks"]["buffer1"]
        buffer1_data = self.ipfs_client.download(buffer1_cid)
        buffer1_data["metadata"]["purpose"] = "emergency_backups"
        buffer1_data["entries"] = []  # Tyhjennä kiireelliset
        buffer1_data["current_index"] = 0
        buffer1_data["total_entries"] = 0
        buffer1_data["entry_hashes"] = []
        new_urgent_cid = self.ipfs_client.upload(buffer1_data)
        
        # 5. Luo uusi buffer1 (tyhjä)
        new_buffer1_data = {
            "metadata": {
                "block_name": "buffer1",
                "purpose": "empty_buffer",
                "created": datetime.now().isoformat(),
                "max_size": self.blocks_config["buffer1"]["max_size"],
                "time_window": None,
                "election_id": self.election_id,
                "node_id": self.node_id
            },
            "entries": [],
            "current_index": 0,
            "total_entries": 0,
            "entry_hashes": []
        }
        new_buffer1_cid = self.ipfs_client.upload(new_buffer1_data)
        
        # Päivitä metadata
        blocks_metadata["block_sequence"] = new_sequence
        blocks_metadata["current_rotation"] += 1
        blocks_metadata["total_rotations"] += 1
        
        blocks_metadata["rotation_history"].append({
            "rotation_id": blocks_metadata["current_rotation"],
            "timestamp": datetime.now().isoformat(),
            "old_sequence": old_sequence,
            "new_sequence": new_sequence,
            "trigger": "active_block_full"
        })
        
        # Päivitä lohkojen CID:t
        blocks_metadata["blocks"] = {
            "buffer1": new_buffer1_cid,
            "urgent": new_urgent_cid,
            "sync": new_sync_cid,
            "active": new_active_cid,
            "buffer2": blocks_metadata["blocks"]["buffer2"]  # Pysyy samana
        }
        
        self.blocks_metadata_cid = self.ipfs_client.upload(blocks_metadata)
        
        print(f"✅ Lohkot pyörivät. Uusi sekvenssi: {new_sequence}")
        print(f"🔄 Pyöritys #{blocks_metadata['current_rotation']} valmis")
    
    def _load_blocks_metadata(self) -> Dict:
        """Lataa lohkojen metadata"""
        if not self.blocks_metadata_cid:
            raise MetadataNotInitializedError("Lohkometadataa ei ole alustettu")
        
        metadata = self.ipfs_client.download(self.blocks_metadata_cid)
        if not metadata:
            raise MetadataNotFoundError("Lohkometadataa ei löydy")
        
        return metadata
    
    def _is_block_full(self, block_data: Dict, block_name: str) -> bool:
        """Tarkista onko lohko täynnä"""
        max_size = self.blocks_config[block_name]["max_size"]
        return len(block_data["entries"]) >= max_size
    
    def _calculate_entry_hash(self, data: Dict) -> str:
        """Laske datan hash"""
        data_string = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    def register_new_node(self, node_id: str) -> bool:
        """Rekisteröi uusi node lohkoihin"""
        blocks_metadata = self._load_blocks_metadata()
        
        if node_id not in blocks_metadata["node_registry"]:
            blocks_metadata["node_registry"].append(node_id)
            self.blocks_metadata_cid = self.ipfs_client.upload(blocks_metadata)
            print(f"✅ Node rekisteröity: {node_id}")
            return True
        
        return False
    
    def get_known_nodes(self) -> List[str]:
        """Hae kaikki tunnetut nodet"""
        blocks_metadata = self._load_blocks_metadata()
        return blocks_metadata.get("node_registry", [])

class BlockNotFoundError(Exception):
    """Lohkoa ei löydy"""
    pass

class BlockFullError(Exception):
    """Lohko on täynnä"""
    pass

class MetadataNotInitializedError(Exception):
    """Metadataa ei ole alustettu"""
    pass

class MetadataNotFoundError(Exception):
    """Metadataa ei löydy"""
    pass

# Testaus
if __name__ == "__main__":
    print("🧪 IPFS BLOCK MANAGER TESTI")
    print("=" * 50)
    
    # Käytä mock-IPFS:ää testaamiseen
    from mock_ipfs import MockIPFS
    
    ipfs = MockIPFS()
    manager = IPFSBlockManager(ipfs, "test_election_2024", "test_node_1")
    
    # Alusta lohkot
    metadata_cid = manager.initialize_blocks()
    print(f"✅ Lohkot alustettu: {metadata_cid}")
    
    # Testaa kirjoitus
    test_data = {"action": "test", "value": 123}
    entry_id = manager.write_to_block("active", test_data, "test_entry")
    print(f"✅ Testimerkintä kirjoitettu: {entry_id}")
    
    # Tarkista status
    status = manager.get_block_status()
    print("📊 LOHKOSTATUS:")
    for block, info in status.items():
        print(f"   {block}: {info['entries']}/{info['max_size']} ({info['purpose']})")
