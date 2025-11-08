#!/usr/bin/env python3
# ipfs_block_manager.py
"""
IPFS Block Manager - PÄIVITETTY NIMIAVARUUDEN KANSSA
Hallinnoi pyöriviä varauslohkoja IPFS:ssä usealle nodelle
Nimiavaruusperustainen eristys eri vaaleille
Käyttö:
  manager = IPFSBlockManager(ipfs_client, "election_2024_namespace")
  entry_id = manager.write_to_block("active", data, "normal_backup")
"""

import json
from datetime import datetime, timedelta
from datetime import timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
import hashlib

class IPFSBlockManager:
    """Hallinnoi pyöriviä varauslohkoja IPFS:ssä usealle nodelle - PÄIVITETTY NIMIAVARUUDELLA"""
    
    def __init__(self, ipfs_client, namespace: str, node_id: str = "default_node"):
        self.ipfs_client = ipfs_client
        self.namespace = namespace  # Vaalikohtainen nimiavaruus
        self.node_id = node_id
        self.blocks_metadata_cid = None
        
        # Lohkojen määritelmät nimiavaruudella
        self.blocks_config = {
            "buffer1": {
                "purpose": f"empty_buffer_{namespace}",
                "max_size": 100,
                "time_window": None,
                "priority": "low",
                "allowed_operations": ["read", "archive"]
            },
            "urgent": {
                "purpose": f"emergency_backups_{namespace}", 
                "max_size": 50,
                "time_window": 3600,  # 1 tunti
                "priority": "critical",
                "allowed_operations": ["read", "write", "emergency"]
            },
            "sync": {
                "purpose": f"synchronization_point_{namespace}",
                "max_size": 200,
                "time_window": 21600,  # 6 tuntia
                "priority": "high", 
                "allowed_operations": ["read", "write", "sync"]
            },
            "active": {
                "purpose": f"active_writing_{namespace}",
                "max_size": 150,
                "time_window": 7200,  # 2 tuntia
                "priority": "medium",
                "allowed_operations": ["read", "write"]
            },
            "buffer2": {
                "purpose": f"transfer_buffer_{namespace}",
                "max_size": 100,
                "time_window": None,
                "priority": "low",
                "allowed_operations": ["read", "archive"]
            }
        }
        
        # Lohkojen järjestys
        self.block_sequence = ["buffer1", "urgent", "sync", "active", "buffer2"]
    
    def initialize_blocks(self) -> str:
        """Alusta lohkorakenne IPFS:ään - PÄIVITETTY NIMIAVARUUDELLA"""
        
        block_cids = {}
        
        for block_name, config in self.blocks_config.items():
            block_data = {
                "metadata": {
                    "block_name": block_name,
                    "namespace": self.namespace,
                    "purpose": config["purpose"],
                    "created": datetime.now(timezone.utc).isoformat(),
                    "max_size": config["max_size"],
                    "time_window": config["time_window"],
                    "election_namespace": self.namespace,
                    "node_id": self.node_id,
                    "priority": config["priority"]
                },
                "entries": [],
                "current_index": 0,
                "total_entries": 0,
                "entry_hashes": []
            }
            
            cid = self.ipfs_client.upload(block_data)
            block_cids[block_name] = cid
            print(f"✅ Lohko alustettu ({self.namespace}): {block_name} -> {cid}")
        
        # Luo metadata-tiedosto nimiavaruudella
        blocks_metadata = {
            "version": "2.0.0",
            "namespace": self.namespace,
            "created": datetime.now(timezone.utc).isoformat(),
            "election_namespace": self.namespace,
            "node_id": self.node_id,
            "block_sequence": self.block_sequence,
            "current_rotation": 0,
            "total_rotations": 0,
            "blocks": block_cids,
            "rotation_history": [],
            "node_registry": [self.node_id],
            "metadata": {
                "namespace_strategy": "election_based",
                "isolation_level": "namespace",
                "created_by": "IPFSBlockManager"
            }
        }
        
        self.blocks_metadata_cid = self.ipfs_client.upload(blocks_metadata)
        print(f"🎯 Lohkometadata luotu ({self.namespace}): {self.blocks_metadata_cid}")
        
        return self.blocks_metadata_cid
    
    def write_to_block(self, block_name: str, data: Dict, data_type: str, 
                      priority: str = "normal") -> str:
        """Kirjoita dataa tiettyyn lohkoon - PÄIVITETTY NIMIAVARUUDELLA"""
        
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
        
        # Luo uusi merkintä nimiavaruudella
        entry_id = f"{self.namespace}_{block_name}_{block_data['current_index']}_{self.node_id}"
        entry_hash = self._calculate_entry_hash(data)
        
        new_entry = {
            "entry_id": entry_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data_type": data_type,
            "node_id": self.node_id,
            "namespace": self.namespace,
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
        
        print(f"📝 Kirjoitettu lohkoon {block_name} ({self.namespace}): {entry_id}")
        return entry_id
    
    def read_from_block(self, block_name: str, entry_id: str = None) -> List[Dict]:
        """Lue dataa lohkosta - PÄIVITETTY NIMIAVARUUDELLA"""
        
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
        """Hae lohkon/lohkojen status - PÄIVITETTY NIMIAVARUUDELLA"""
        
        blocks_metadata = self._load_blocks_metadata()
        
        if block_name:
            # Yksittäisen lohkon status
            block_cid = blocks_metadata["blocks"][block_name]
            block_data = self.ipfs_client.download(block_cid)
            
            return {
                "block_name": block_name,
                "namespace": self.namespace,
                "purpose": self.blocks_config[block_name]["purpose"],
                "current_entries": len(block_data["entries"]),
                "max_size": self.blocks_config[block_name]["max_size"],
                "usage_percentage": (len(block_data["entries"]) / self.blocks_config[block_name]["max_size"]) * 100,
                "last_updated": block_data["entries"][-1]["timestamp"] if block_data["entries"] else "Ei merkintöjä",
                "node_id": self.node_id
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
                    "full": len(block_data["entries"]) >= self.blocks_config[block_name]["max_size"],
                    "namespace": self.namespace,
                    "usage_percentage": (len(block_data["entries"]) / self.blocks_config[block_name]["max_size"]) * 100
                }
            
            return status
    
    def _rotate_blocks(self):
        """Pyöritä lohkoja kun aktiivinen lohko täyttyy - PÄIVITETTY NIMIAVARUUDELLA"""
        
        blocks_metadata = self._load_blocks_metadata()
        old_sequence = blocks_metadata["block_sequence"]
        
        print(f"🔄 Pyöritetään lohkoja ({self.namespace}): {old_sequence}")
        
        # Uusi sekvenssi: siirrä kaikkia yksi asema eteenpäin
        new_sequence = old_sequence[1:] + [old_sequence[0]]
        
        # 1. Arkistoi vanha aktiivinen lohko (entinen active -> uusi buffer2)
        old_active_cid = blocks_metadata["blocks"]["active"]
        old_active_data = self.ipfs_client.download(old_active_cid)
        
        archive_entry = {
            "archive_timestamp": datetime.now(timezone.utc).isoformat(),
            "original_block": "active",
            "namespace": self.namespace,
            "total_entries": len(old_active_data["entries"]),
            "entry_ids": [entry["entry_id"] for entry in old_active_data["entries"]],
            "rotated_by": self.node_id
        }
        
        # Kirjoita arkistoi buffer2:een
        self.write_to_block("buffer2", archive_entry, "block_archive", "low")
        
        # 2. Siirrä sync -> active (tyhjennä ensin)
        sync_cid = blocks_metadata["blocks"]["sync"]
        sync_data = self.ipfs_client.download(sync_cid)
        sync_data["metadata"]["purpose"] = f"active_writing_{self.namespace}"
        sync_data["entries"] = []  # Tyhjennä uusi aktiivinen lohko
        sync_data["current_index"] = 0
        sync_data["total_entries"] = 0
        sync_data["entry_hashes"] = []
        new_active_cid = self.ipfs_client.upload(sync_data)
        
        # 3. Siirrä urgent -> sync (säilytä data)
        urgent_cid = blocks_metadata["blocks"]["urgent"]
        urgent_data = self.ipfs_client.download(urgent_cid)
        urgent_data["metadata"]["purpose"] = f"synchronization_point_{self.namespace}"
        new_sync_cid = self.ipfs_client.upload(urgent_data)
        
        # 4. Siirrä buffer1 -> urgent (tyhjennä)
        buffer1_cid = blocks_metadata["blocks"]["buffer1"]
        buffer1_data = self.ipfs_client.download(buffer1_cid)
        buffer1_data["metadata"]["purpose"] = f"emergency_backups_{self.namespace}"
        buffer1_data["entries"] = []  # Tyhjennä kiireelliset
        buffer1_data["current_index"] = 0
        buffer1_data["total_entries"] = 0
        buffer1_data["entry_hashes"] = []
        new_urgent_cid = self.ipfs_client.upload(buffer1_data)
        
        # 5. Luo uusi buffer1 (tyhjä)
        new_buffer1_data = {
            "metadata": {
                "block_name": "buffer1",
                "namespace": self.namespace,
                "purpose": f"empty_buffer_{self.namespace}",
                "created": datetime.now(timezone.utc).isoformat(),
                "max_size": self.blocks_config["buffer1"]["max_size"],
                "time_window": None,
                "election_namespace": self.namespace,
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
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "old_sequence": old_sequence,
            "new_sequence": new_sequence,
            "trigger": "active_block_full",
            "namespace": self.namespace,
            "node_id": self.node_id
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
        
        print(f"✅ Lohkot pyörivät ({self.namespace}). Uusi sekvenssi: {new_sequence}")
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
        """Rekisteröi uusi node lohkoihin - PÄIVITETTY NIMIAVARUUDELLA"""
        blocks_metadata = self._load_blocks_metadata()
        
        if node_id not in blocks_metadata["node_registry"]:
            blocks_metadata["node_registry"].append(node_id)
            self.blocks_metadata_cid = self.ipfs_client.upload(blocks_metadata)
            print(f"✅ Node rekisteröity ({self.namespace}): {node_id}")
            return True
        
        return False
    
    def get_known_nodes(self) -> List[str]:
        """Hae kaikki tunnetut nodet"""
        blocks_metadata = self._load_blocks_metadata()
        return blocks_metadata.get("node_registry", [])
    
    def get_namespace_info(self) -> Dict:
        """Hae nimiavaruuden tiedot"""
        blocks_metadata = self._load_blocks_metadata()
        
        return {
            "namespace": self.namespace,
            "metadata_cid": self.blocks_metadata_cid,
            "total_blocks": len(self.blocks_config),
            "total_rotations": blocks_metadata.get("total_rotations", 0),
            "current_rotation": blocks_metadata.get("current_rotation", 0),
            "node_count": len(blocks_metadata.get("node_registry", [])),
            "created": blocks_metadata.get("created", "unknown"),
            "node_id": self.node_id
        }
    
    def verify_namespace_integrity(self) -> bool:
        """Tarkista nimiavaruuden eheys"""
        try:
            blocks_metadata = self._load_blocks_metadata()
            
            # Tarkista että metadata-nimiavaruus vastaa instanssin nimiavaruutta
            metadata_namespace = blocks_metadata.get("namespace")
            if metadata_namespace != self.namespace:
                print(f"❌ Nimiavaruussopimattomuus: {metadata_namespace} != {self.namespace}")
                return False
            
            # Tarkista että kaikki lohkot ovat olemassa
            for block_name in self.block_sequence:
                block_cid = blocks_metadata["blocks"][block_name]
                block_data = self.ipfs_client.download(block_cid)
                
                if not block_data:
                    print(f"❌ Lohkoa ei löydy: {block_name}")
                    return False
                
                # Tarkista että lohkon nimiavaruus vastaa
                block_namespace = block_data["metadata"].get("namespace")
                if block_namespace != self.namespace:
                    print(f"❌ Lohkon nimiavaruussopimattomuus: {block_namespace} != {self.namespace}")
                    return False
            
            print(f"✅ Nimiavaruuden eheys varmistettu: {self.namespace}")
            return True
            
        except Exception as e:
            print(f"❌ Nimiavaruuden eheyden tarkistus epäonnistui: {e}")
            return False
    
    def cleanup_old_entries(self, older_than_days: int = 30) -> Dict:
        """Siivoa vanhat merkinnät - PÄIVITETTY NIMIAVARUUDELLA"""
        print(f"🧹 Siivotaan vanhat merkinnät ({self.namespace}), yli {older_than_days} päivää vanhat")
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=older_than_days)
        cleanup_stats = {
            "namespace": self.namespace,
            "cutoff_date": cutoff_date.isoformat(),
            "cleaned_entries": 0,
            "affected_blocks": []
        }
        
        blocks_metadata = self._load_blocks_metadata()
        
        for block_name in self.block_sequence:
            block_cid = blocks_metadata["blocks"][block_name]
            block_data = self.ipfs_client.download(block_cid)
            
            original_count = len(block_data["entries"])
            
            # Suodata vanhat merkinnät
            block_data["entries"] = [
                entry for entry in block_data["entries"]
                if datetime.fromisoformat(entry["timestamp"]) > cutoff_date
            ]
            
            cleaned_count = original_count - len(block_data["entries"])
            if cleaned_count > 0:
                # Päivitä lohko
                new_block_cid = self.ipfs_client.upload(block_data)
                blocks_metadata["blocks"][block_name] = new_block_cid
                
                cleanup_stats["cleaned_entries"] += cleaned_count
                cleanup_stats["affected_blocks"].append({
                    "block_name": block_name,
                    "cleaned_entries": cleaned_count,
                    "remaining_entries": len(block_data["entries"])
                })
                
                print(f"   🧹 {block_name}: poistettu {cleaned_count} vanhaa merkintää")
        
        # Päivitä metadata jos tarvittaessa
        if cleanup_stats["cleaned_entries"] > 0:
            self.blocks_metadata_cid = self.ipfs_client.upload(blocks_metadata)
            print(f"✅ Siivous valmis: {cleanup_stats['cleaned_entries']} merkintää poistettu")
        else:
            print("ℹ️  Ei vanhoja merkintöjä siivottavaksi")
        
        return cleanup_stats

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
    print("🧪 IPFS BLOCK MANAGER TESTI - PÄIVITETTY NIMIAVARUUDELLA")
    print("=" * 60)
    
    # Käytä mock-IPFS:ää testaamiseen
    from mock_ipfs import MockIPFS
    
    ipfs = MockIPFS()
    
    # Testaa eri nimiavaruuksilla
    namespaces = ["election_test_2024", "election_demo_2024"]
    
    for namespace in namespaces:
        print(f"\n🔗 Testataan nimiavaruutta: {namespace}")
        manager = IPFSBlockManager(ipfs, namespace, f"test_node_{namespace}")
        
        # Alusta lohkot
        metadata_cid = manager.initialize_blocks()
        print(f"✅ Lohkot alustettu: {metadata_cid}")
        
        # Testaa kirjoitus
        test_data = {"action": "test", "namespace": namespace, "value": 123}
        entry_id = manager.write_to_block("active", test_data, "test_entry")
        print(f"✅ Testimerkintä kirjoitettu: {entry_id}")
        
        # Tarkista status
        status = manager.get_block_status()
        print("📊 LOHKOSTATUS:")
        for block, info in status.items():
            print(f"   {block}: {info['entries']}/{info['max_size']} ({info['namespace']})")
        
        # Tarkista nimiavaruuden eheys
        integrity_ok = manager.verify_namespace_integrity()
        print(f"🔒 Nimiavaruuden eheys: {'✅ OK' if integrity_ok else '❌ FAIL'}")
        
        # Näytä nimiavaruuden tiedot
        namespace_info = manager.get_namespace_info()
        print(f"📋 Nimiavaruustiedot: {namespace_info['namespace']}")
        print(f"   Lohkoja: {namespace_info['total_blocks']}")
        print(f"   Pyörityksiä: {namespace_info['total_rotations']}")
