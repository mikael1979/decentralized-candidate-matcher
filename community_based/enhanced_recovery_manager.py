#!/usr/bin/env python3
# enhanced_recovery_manager.py
"""
Enhanced Recovery Manager - Älykäs palautusmekanismi lohkojen avulla
Käyttö:
  recovery = EnhancedRecoveryManager(ipfs_client, "election_2024")
  recovery.perform_intelligent_backup(data, "emergency")
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from ipfs_block_manager import IPFSBlockManager

class EnhancedRecoveryManager:
    """Älykäs palautusmekanismi IPFS-lohkojen avulla"""
    
    def __init__(self, runtime_dir: str = "runtime", ipfs_client=None, 
                 election_id: str = "default_election", node_id: str = "default_node"):
        self.runtime_dir = Path(runtime_dir)
        self.ipfs_client = ipfs_client
        self.election_id = election_id
        self.node_id = node_id
        
        # Alusta lohkomanageri
        self.block_manager = IPFSBlockManager(ipfs_client, election_id, node_id)
        
        # Palautuskonfiguraatio
        self.recovery_config = {
            "auto_backup_interval": 3600,  # 1 tunti
            "emergency_threshold": 5,      # 5 virhettä -> hätätila
            "max_recovery_attempts": 3,
            "data_retention_days": 30
        }
    
    def initialize_recovery_system(self) -> str:
        """Alusta palautusjärjestelmä"""
        try:
            metadata_cid = self.block_manager.initialize_blocks()
            print(f"✅ Palautusjärjestelmä alustettu: {metadata_cid}")
            
            # Tee ensimmäinen varaus
            initial_backup = {
                "system_initialized": datetime.now().isoformat(),
                "election_id": self.election_id,
                "node_id": self.node_id,
                "version": "1.0.0"
            }
            
            self.perform_intelligent_backup(initial_backup, "system_init")
            return metadata_cid
            
        except Exception as e:
            print(f"❌ Palautusjärjestelmän alustus epäonnistui: {e}")
            raise
    
    def perform_intelligent_backup(self, data: Dict, data_type: str, 
                                 priority: str = "normal") -> str:
        """
        Tee älykäs varaus prioriteetin perusteella
        
        Args:
            data: Varattava data
            data_type: Datatyypin kuvaus
            priority: "emergency", "high", "normal", "low"
        """
        
        # Määritä kohdelohko prioriteetin perusteella
        block_mapping = {
            "emergency": "urgent",
            "high": "sync", 
            "normal": "active",
            "low": "buffer2"
        }
        
        target_block = block_mapping.get(priority, "active")
        
        # Lisää metadataa
        enhanced_data = {
            "backup_timestamp": datetime.now().isoformat(),
            "data_type": data_type,
            "priority": priority,
            "node_id": self.node_id,
            "election_id": self.election_id,
            "original_data": data
        }
        
        try:
            entry_id = self.block_manager.write_to_block(
                target_block, enhanced_data, data_type, priority
            )
            
            print(f"✅ Varaus tehty: {data_type} -> {target_block} ({entry_id})")
            return entry_id
            
        except Exception as e:
            print(f"❌ Varaus epäonnistui: {e}")
            # Yritä hätävaraukseen
            return self._emergency_fallback_backup(enhanced_data, data_type)
    
    def recover_system(self, target_timestamp: str = None) -> Dict:
        """
        Palauta järjestelmä viimeisestä tiedosta
        
        Args:
            target_timestamp: Kohdeaika (valinnainen)
        """
        
        print("🔄 Palautetaan järjestelmää...")
        
        # Kerää kaikki varausmerkinnät
        all_backups = self._collect_all_backups()
        
        if not all_backups:
            return {"success": False, "error": "Ei varauksia saatavilla"}
        
        # Lajittele aikajärjestykseen
        sorted_backups = sorted(all_backups, 
                              key=lambda x: x["backup_timestamp"], 
                              reverse=True)
        
        # Valitse kohdevaraus
        if target_timestamp:
            # Etsi tiettyyn aikaan
            target_backup = None
            for backup in sorted_backups:
                if backup["backup_timestamp"] <= target_timestamp:
                    target_backup = backup
                    break
        else:
            # Viimeisin varaus
            target_backup = sorted_backups[0] if sorted_backups else None
        
        if not target_backup:
            return {"success": False, "error": "Kohdevarausta ei löydy"}
        
        # Palauta data
        recovery_data = target_backup["original_data"]
        
        # Toteuta palautus
        recovery_result = self._execute_recovery(recovery_data)
        
        return {
            "success": True,
            "recovery_timestamp": datetime.now().isoformat(),
            "backup_used": target_backup["backup_timestamp"],
            "data_type": target_backup["data_type"],
            "recovery_result": recovery_result,
            "available_backups": len(all_backups)
        }
    
    def multi_node_synchronization(self, known_node_cids: List[str] = None) -> Dict:
        """Synkronoi tämän noden data muiden nodien kanssa"""
        
        if not known_node_cids:
            known_node_cids = self.block_manager.get_known_nodes()
        
        print(f"🔗 Synkronoidaan {len(known_node_cids)} noden kanssa...")
        
        all_sync_data = []
        
        # 1. Kerää oma synkronointidata
        own_sync_entries = self.block_manager.read_from_block("sync")
        all_sync_data.extend(own_sync_entries)
        
        # 2. Kerää muiden nodien data (simuloidaan)
        for node_id in known_node_cids:
            if node_id != self.node_id:
                # Simuloi toisen noden datan hakeminen
                simulated_node_data = self._simulate_node_sync(node_id)
                all_sync_data.extend(simulated_node_data)
        
        # 3. Yhdistä ja deduplikaatti
        unique_data = self._deduplicate_sync_data(all_sync_data)
        
        # 4. Kirjoita yhdistetty data synkronointilohkoon
        sync_summary = {
            "sync_operation": "multi_node_synchronization",
            "timestamp": datetime.now().isoformat(),
            "nodes_synchronized": len(known_node_cids),
            "total_entries_received": len(all_sync_data),
            "unique_entries_after_deduplication": len(unique_data),
            "participating_nodes": known_node_cids
        }
        
        sync_package = {
            "summary": sync_summary,
            "entries": unique_data
        }
        
        entry_id = self.perform_intelligent_backup(sync_package, "multi_node_sync", "high")
        
        return {
            "success": True,
            "sync_id": entry_id,
            "nodes_processed": len(known_node_cids),
            "entries_processed": len(all_sync_data),
            "unique_entries": len(unique_data),
            "sync_timestamp": datetime.now().isoformat()
        }
    
    def get_recovery_status(self) -> Dict:
        """Hae palautusjärjestelmän status"""
        
        block_status = self.block_manager.get_block_status()
        
        # Laske tilastot
        total_entries = 0
        total_capacity = 0
        emergency_entries = 0
        
        for block_name, status in block_status.items():
            total_entries += status["entries"]
            total_capacity += status["max_size"]
            if block_name == "urgent":
                emergency_entries = status["entries"]
        
        return {
            "recovery_system_initialized": self.block_manager.blocks_metadata_cid is not None,
            "total_backup_entries": total_entries,
            "total_capacity": total_capacity,
            "usage_percentage": (total_entries / total_capacity * 100) if total_capacity > 0 else 0,
            "emergency_backups": emergency_entries,
            "known_nodes": self.block_manager.get_known_nodes(),
            "node_id": self.node_id,
            "election_id": self.election_id,
            "last_updated": datetime.now().isoformat(),
            "block_status": block_status
        }
    
    def _collect_all_backups(self) -> List[Dict]:
        """Kerää kaikki varausmerkinnät kaikista lohkoista"""
        
        all_entries = []
        blocks = ["urgent", "sync", "active", "buffer2"]  # buffer1 on tyhjä
        
        for block_name in blocks:
            try:
                entries = self.block_manager.read_from_block(block_name)
                # Lisää lohkon nimi jokaiseen merkintään
                for entry in entries:
                    entry["source_block"] = block_name
                all_entries.extend(entries)
            except Exception as e:
                print(f"⚠️  Ei voitu ladata lohkoa {block_name}: {e}")
        
        return all_entries
    
    def _execute_recovery(self, recovery_data: Dict) -> Dict:
        """Suorita varsinainen palautus"""
        
        # Toteuta palautuslogiikka tähän
        # Tämä riippuu siitä, mitä dataa palautetaan
        
        recovery_actions = []
        
        if "questions" in recovery_data:
            recovery_actions.append("questions_restored")
            # Toteuta kysymysten palautus
        
        if "candidates" in recovery_data:
            recovery_actions.append("candidates_restored") 
            # Toteuta ehdokkaiden palautus
        
        if "system_chain" in recovery_data:
            recovery_actions.append("system_chain_restored")
            # Toteuta system_chainin palautus
        
        return {
            "actions_performed": recovery_actions,
            "data_types_restored": list(recovery_data.keys()),
            "recovery_timestamp": datetime.now().isoformat()
        }
    
    def _emergency_fallback_backup(self, data: Dict, data_type: str) -> str:
        """Hätävaraus kun normaalit mekanismit epäonnistuvat"""
        
        print("🚨 HÄTÄVARAUS AKTIVOITU!")
        
        # Yritä kirjoittaa suoraan kiireelliseen lohkoon
        try:
            entry_id = self.block_manager.write_to_block(
                "urgent", data, f"emergency_{data_type}", "emergency"
            )
            print(f"✅ Hätävaraus onnistui: {entry_id}")
            return entry_id
        except Exception as e:
            print(f"❌ Hätävaraus epäonnistui: {e}")
            # Viimeinen vaihtoehto: tallenna paikallisesti
            return self._local_emergency_backup(data, data_type)
    
    def _local_emergency_backup(self, data: Dict, data_type: str) -> str:
        """Paikallinen hätävaraus kun IPFS ei saatavilla"""
        
        emergency_dir = self.runtime_dir / "emergency_backups"
        emergency_dir.mkdir(exist_ok=True)
        
        filename = f"emergency_{data_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = emergency_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"📁 Paikallinen hätävaraus: {filepath}")
            return f"local_{filename}"
            
        except Exception as e:
            print(f"❌ Paikallinen hätävaraus epäonnistui: {e}")
            return "backup_failed"
    
    def _deduplicate_sync_data(self, sync_data: List[Dict]) -> List[Dict]:
        """Poista duplikaatit synkronointidatasta"""
        
        seen_hashes = set()
        unique_data = []
        
        for entry in sync_data:
            entry_hash = entry.get("entry_hash")
            if entry_hash and entry_hash not in seen_hashes:
                seen_hashes.add(entry_hash)
                unique_data.append(entry)
            elif not entry_hash:
                # Jos ei hashia, käytä timestampia ja dataa
                unique_key = f"{entry.get('timestamp')}_{json.dumps(entry.get('data', {}))}"
                if unique_key not in seen_hashes:
                    seen_hashes.add(unique_key)
                    unique_data.append(entry)
        
        return unique_data
    
    def _simulate_node_sync(self, node_id: str) -> List[Dict]:
        """Simuloi toisen noden synkronointidataa"""
        # Toteutus riippuu todellisesta noden välisestä kommunikaatiosta
        return []

# Testaus
if __name__ == "__main__":
    print("🧪 ENHANCED RECOVERY MANAGER TESTI")
    print("=" * 50)
    
    from mock_ipfs import MockIPFS
    
    ipfs = MockIPFS()
    recovery = EnhancedRecoveryManager(
        runtime_dir="runtime_test", 
        ipfs_client=ipfs,
        election_id="test_election_2024",
        node_id="test_node_1"
    )
    
    # Alusta järjestelmä
    metadata_cid = recovery.initialize_recovery_system()
    
    # Testaa varauksia eri prioriteeteilla
    test_data = {"questions": ["q1", "q2"], "timestamp": datetime.now().isoformat()}
    
    recovery.perform_intelligent_backup(test_data, "test_backup", "normal")
    recovery.perform_intelligent_backup(test_data, "emergency_test", "emergency")
    recovery.perform_intelligent_backup(test_data, "high_priority_test", "high")
    
    # Tarkista status
    status = recovery.get_recovery_status()
    print("📊 PALAUTUSJÄRJESTELMÄN TILA:")
    print(f"   Varauksia: {status['total_backup_entries']}/{status['total_capacity']}")
    print(f"   Käyttö: {status['usage_percentage']:.1f}%")
    print(f"   Hätävarauksia: {status['emergency_backups']}")
    
    # Testaa moninodisynkronointi
    sync_result = recovery.multi_node_synchronization(["node_1", "node_2", "node_3"])
    print(f"🔗 Synkronointi: {sync_result['entries_processed']} merkintää käsitelty")
