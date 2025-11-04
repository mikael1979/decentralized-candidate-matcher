#!/usr/bin/env python3
# enhanced_recovery_manager.py
"""
Enhanced Recovery Manager - PÄIVITETTY NIMIAVARUUDEN KANSSA
Älykäs palautusmekanismi lohkojen ja ajanvarauksen avulla
Käyttö:
  recovery = EnhancedRecoveryManager(ipfs_client, "election_2024")
  recovery.perform_intelligent_backup(data, "emergency")
"""

import json
from datetime import datetime, timedelta
from datetime import timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

# Ajanvarauksen tyypit
class ReservationType:
    URGENT = "urgent_reservation"
    NODE_SYNC = "node_reservation"
    DATA_BACKUP = "data_backup"
    SYSTEM_SYNC = "system_sync"
    RECOVERY = "recovery_operation"
    EMERGENCY = "emergency_backup"

class EnhancedRecoveryManager:
    """Älykäs palautusmekanismi IPFS-lohkojen ja ajanvarauksen avulla - PÄIVITETTY NIMIAVARUUDELLA"""
    
    def __init__(self, runtime_dir: str = "runtime", ipfs_client=None, 
                 election_id: str = "default_election", node_id: str = "default_node"):
        self.runtime_dir = Path(runtime_dir)
        self.ipfs_client = ipfs_client
        self.election_id = election_id
        self.node_id = node_id
        
        # Luo vaalikohtainen nimiavaruus
        self.namespace = self._get_or_create_namespace()
        
        # Alusta lohkomanageri nimiavaruudella
        self.block_manager = self._initialize_block_manager()
        
        # Alusta ajanvarausmanageri
        self.schedule_manager = self._initialize_schedule_manager()
        
        # Palautuskonfiguraatio
        self.recovery_config = {
            "auto_backup_interval": 3600,  # 1 tunti
            "emergency_threshold": 5,      # 5 virhettä -> hätätila
            "max_recovery_attempts": 3,
            "data_retention_days": 30,
            "use_schedule": True,          # Käytä ajanvarausta
            "schedule_priority_mapping": {
                "emergency": "critical",
                "high": "high", 
                "normal": "normal",
                "low": "low"
            },
            "namespace": self.namespace
        }
        
        # Lataa konfiguraatio
        self._load_recovery_config()
    
    def _get_or_create_namespace(self) -> str:
        """Hae tai luo nimiavaruus"""
        try:
            from metadata_manager import get_metadata_manager
            manager = get_metadata_manager(self.runtime_dir)
            namespace_info = manager.get_namespace_info()
            return namespace_info.get("namespace", f"election_{self.election_id}")
        except ImportError:
            # Fallback: luo nimiavaruus ilman metadataa
            return f"election_{self.election_id}_{datetime.now().strftime('%Y%m%d')}"
    
    def _initialize_block_manager(self):
        """Alusta lohkomanageri nimiavaruudella"""
        try:
            from ipfs_block_manager import IPFSBlockManager
            return IPFSBlockManager(self.ipfs_client, self.namespace, self.node_id)
        except ImportError as e:
            print(f"❌ IPFS-lohkomanageria ei saatavilla: {e}")
            raise
    
    def _initialize_schedule_manager(self):
        """Alusta ajanvarausmanageri"""
        try:
            from ipfs_schedule_manager import IPFSScheduleManager
            return IPFSScheduleManager()
        except ImportError:
            print("⚠️  IPFS-ajanvarausmanageria ei saatavilla - käytetään suoria varauksia")
            return None
    
    def _load_recovery_config(self):
        """Lataa palautuskonfiguraatio"""
        config_file = self.runtime_dir / "recovery_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.recovery_config.update(loaded_config)
            except Exception as e:
                print(f"⚠️  Virhe palautuskonfiguraatiota ladatessa: {e}")
    
    def _save_recovery_config(self):
        """Tallenna palautuskonfiguraatio"""
        config_file = self.runtime_dir / "recovery_config.json"
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.recovery_config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Virhe palautuskonfiguraatiota tallennettaessa: {e}")
    
    def initialize_recovery_system(self) -> str:
        """Alusta palautusjärjestelmä - PÄIVITETTY NIMIAVARUUDELLA"""
        try:
            metadata_cid = self.block_manager.initialize_blocks()
            print(f"✅ Palautusjärjestelmä alustettu: {metadata_cid}")
            print(f"   Nimiavaruus: {self.namespace}")
            print(f"   Node ID: {self.node_id}")
            print(f"   Vaali: {self.election_id}")
            
            # Tee ensimmäinen varaus ajanvarauksen kautta
            initial_backup = {
                "system_initialized": datetime.now(timezone.utc).isoformat(),
                "election_id": self.election_id,
                "node_id": self.node_id,
                "namespace": self.namespace,
                "version": "2.0.0",
                "features": ["ipfs_blocks", "schedule_management", "intelligent_recovery", "namespace_aware"]
            }
            
            backup_id = self.perform_intelligent_backup(initial_backup, "system_init", "high")
            
            # Päivitä konfiguraatio
            self.recovery_config["initialized_at"] = datetime.now(timezone.utc).isoformat()
            self.recovery_config["metadata_cid"] = metadata_cid
            self._save_recovery_config()
            
            return metadata_cid
            
        except Exception as e:
            print(f"❌ Palautusjärjestelmän alustus epäonnistui: {e}")
            raise
    
    def perform_intelligent_backup(self, data: Dict, data_type: str, 
                                 priority: str = "normal") -> str:
        """
        Tee älykäs varaus prioriteetin perusteella AJANVARAUKSEN KANSSA
        
        Args:
            data: Varattava data
            data_type: Datatyypin kuvaus
            priority: "emergency", "high", "normal", "low"
        """
        
        # 1. Käytä ajanvarausta korkean prioriteetin operaatioihin
        reservation_result = None
        if (self.schedule_manager and 
            self.recovery_config.get("use_schedule", True) and 
            priority in ["high", "emergency"]):
            
            reservation_type = (ReservationType.URGENT if priority == "emergency" 
                              else ReservationType.DATA_BACKUP)
            
            urgency = self.recovery_config["schedule_priority_mapping"].get(priority, "normal")
            
            reservation_result = self.schedule_manager.request_reservation(
                reservation_type,
                self.node_id,
                urgency=urgency,
                metadata={
                    "backup_type": data_type,
                    "priority": priority,
                    "election_id": self.election_id,
                    "namespace": self.namespace,
                    "data_size": len(str(data))
                }
            )
            
            if reservation_result["success"]:
                print(f"🕒 Varaus vahvistettu: {reservation_result['reservation_id']}")
            else:
                print(f"⚠️  Ei ajanvarausta saatavilla: {reservation_result.get('error')}")
                if priority == "emergency":
                    print("🚨 Hätätila - ohitetaan ajanvaraus")
                else:
                    # Normaaleille operaatioille, käytä suoraa varausta
                    print("📝 Tehdään suora varaus ilman ajanvarausta")
        
        # 2. Määritä kohdelohko prioriteetin perusteella
        block_mapping = {
            "emergency": "urgent",
            "high": "sync", 
            "normal": "active",
            "low": "buffer2"
        }
        
        target_block = block_mapping.get(priority, "active")
        
        # 3. Lisää metadataa
        enhanced_data = {
            "backup_timestamp": datetime.now(timezone.utc).isoformat(),
            "data_type": data_type,
            "priority": priority,
            "node_id": self.node_id,
            "election_id": self.election_id,
            "namespace": self.namespace,
            "reservation_used": reservation_result["reservation_id"] if reservation_result and reservation_result["success"] else "direct",
            "original_data": data
        }
        
        # 4. Lisää ajanvarauksen tiedot jos käytettiin
        if reservation_result and reservation_result["success"]:
            enhanced_data["reservation_info"] = {
                "reservation_id": reservation_result["reservation_id"],
                "time_slot": reservation_result["time_slot"],
                "conflicts_resolved": reservation_result.get("conflicts_resolved", False)
            }
        
        try:
            entry_id = self.block_manager.write_to_block(
                target_block, enhanced_data, data_type, priority
            )
            
            print(f"✅ Varaus tehty: {data_type} -> {target_block} ({entry_id})")
            print(f"   Nimiavaruus: {self.namespace}")
            
            # 5. Kirjaa system_chainiin
            self._log_backup_to_chain(entry_id, data_type, priority, reservation_result)
            
            return entry_id
            
        except Exception as e:
            print(f"❌ Varaus epäonnistui: {e}")
            # Yritä hätävaraukseen
            return self._emergency_fallback_backup(enhanced_data, data_type, reservation_result)
    
    def recover_system(self, target_timestamp: str = None, use_schedule: bool = True) -> Dict:
        """
        Palauta järjestelmä viimeisestä tiedosta - PÄIVITETTY AJANVARAUKSELLA
        
        Args:
            target_timestamp: Kohdeaika (valinnainen)
            use_schedule: Käytä ajanvarausta palautukseen
        """
        
        print("🔄 Palautetaan järjestelmää...")
        print(f"   Nimiavaruus: {self.namespace}")
        
        # 1. Varaa aika palautusoperaatiolle
        reservation_result = None
        if use_schedule and self.schedule_manager:
            reservation_result = self.schedule_manager.request_reservation(
                ReservationType.RECOVERY,
                self.node_id,
                urgency="high",
                metadata={
                    "operation": "system_recovery",
                    "target_timestamp": target_timestamp,
                    "election_id": self.election_id,
                    "namespace": self.namespace
                }
            )
            
            if reservation_result["success"]:
                print(f"🕒 Palautus ajastettu: {reservation_result['reservation_id']}")
            else:
                print(f"⚠️  Ei ajanvarausta palautukseen: {reservation_result.get('error')}")
                print("🔄 Jatketaan suorana palautuksena")
        
        # 2. Kerää kaikki varausmerkinnät
        all_backups = self._collect_all_backups()
        
        if not all_backups:
            return {
                "success": False, 
                "error": "Ei varauksia saatavilla",
                "namespace": self.namespace,
                "reservation_used": reservation_result["reservation_id"] if reservation_result and reservation_result["success"] else None
            }
        
        # 3. Lajittele aikajärjestykseen
        sorted_backups = sorted(all_backups, 
                              key=lambda x: x["backup_timestamp"], 
                              reverse=True)
        
        # 4. Valitse kohdevaraus
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
            return {
                "success": False, 
                "error": "Kohdevarausta ei löydy",
                "namespace": self.namespace,
                "reservation_used": reservation_result["reservation_id"] if reservation_result and reservation_result["success"] else None
            }
        
        # 5. Palauta data
        recovery_data = target_backup["original_data"]
        
        # 6. Toteuta palautus
        recovery_result = self._execute_recovery(recovery_data)
        
        result = {
            "success": True,
            "recovery_timestamp": datetime.now(timezone.utc).isoformat(),
            "backup_used": target_backup["backup_timestamp"],
            "data_type": target_backup["data_type"],
            "recovery_result": recovery_result,
            "available_backups": len(all_backups),
            "namespace": self.namespace,
            "reservation_used": reservation_result["reservation_id"] if reservation_result and reservation_result["success"] else None
        }
        
        # 7. Kirjaa palautus system_chainiin
        self._log_recovery_to_chain(result, reservation_result)
        
        print(f"✅ Järjestelmä palautettu onnistuneesti: {target_backup['data_type']}")
        
        return result
    
    def multi_node_synchronization(self, known_node_cids: List[str] = None, 
                                 use_schedule: bool = True) -> Dict:
        """Synkronoi tämän noden data muiden nodien kanssa AJANVARAUKSEN KANSSA"""
        
        if not known_node_cids:
            known_node_cids = self.block_manager.get_known_nodes()
        
        print(f"🔗 Synkronoidaan {len(known_node_cids)} noden kanssa...")
        print(f"   Nimiavaruus: {self.namespace}")
        
        # 1. Varaa aika synkronointiin
        reservation_result = None
        if use_schedule and self.schedule_manager:
            reservation_result = self.schedule_manager.request_reservation(
                ReservationType.SYSTEM_SYNC,
                self.node_id,
                urgency="normal",
                metadata={
                    "operation": "multi_node_sync",
                    "node_count": len(known_node_cids),
                    "election_id": self.election_id,
                    "namespace": self.namespace
                }
            )
            
            if reservation_result["success"]:
                print(f"🕒 Synkronointi ajastettu: {reservation_result['reservation_id']}")
        
        # 2. Kerää oma synkronointidata
        own_sync_entries = self.block_manager.read_from_block("sync")
        all_sync_data = []
        
        for entry in own_sync_entries:
            entry["_source_node"] = self.node_id
            entry["_source_block"] = "sync"
            entry["_namespace"] = self.namespace
            all_sync_data.append(entry)
        
        # 3. Kerää muiden nodien data (simuloidaan)
        for node_id in known_node_cids:
            if node_id != self.node_id:
                simulated_node_data = self._simulate_node_sync(node_id)
                all_sync_data.extend(simulated_node_data)
        
        # 4. Yhdistä ja deduplikaatti
        unique_data = self._deduplicate_sync_data(all_sync_data)
        
        # 5. Kirjoita yhdistetty data synkronointilohkoon
        sync_summary = {
            "sync_operation": "multi_node_synchronization",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "nodes_synchronized": len(known_node_cids),
            "total_entries_received": len(all_sync_data),
            "unique_entries_after_deduplication": len(unique_data),
            "participating_nodes": known_node_cids,
            "reservation_used": reservation_result["reservation_id"] if reservation_result and reservation_result["success"] else None,
            "namespace": self.namespace
        }
        
        sync_package = {
            "summary": sync_summary,
            "entries": unique_data
        }
        
        entry_id = self.perform_intelligent_backup(sync_package, "multi_node_sync", "high")
        
        result = {
            "success": True,
            "sync_id": entry_id,
            "nodes_processed": len(known_node_cids),
            "entries_processed": len(all_sync_data),
            "unique_entries": len(unique_data),
            "sync_timestamp": datetime.now(timezone.utc).isoformat(),
            "namespace": self.namespace,
            "reservation_used": reservation_result["reservation_id"] if reservation_result and reservation_result["success"] else None
        }
        
        # 6. Kirjaa synkronointi system_chainiin
        self._log_sync_to_chain(result, reservation_result)
        
        return result
    
    def get_recovery_status(self) -> Dict:
        """Hae palautusjärjestelmän status - PÄIVITETTY AJANVARAUSTIEDOILLA"""
        
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
        
        # Hae ajanvarauksen tila
        schedule_status = {}
        if self.schedule_manager:
            schedule_status = self.schedule_manager.get_schedule_status(self.node_id)
        
        return {
            "recovery_system_initialized": self.block_manager.blocks_metadata_cid is not None,
            "total_backup_entries": total_entries,
            "total_capacity": total_capacity,
            "usage_percentage": (total_entries / total_capacity * 100) if total_capacity > 0 else 0,
            "emergency_backups": emergency_entries,
            "known_nodes": self.block_manager.get_known_nodes(),
            "node_id": self.node_id,
            "election_id": self.election_id,
            "namespace": self.namespace,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "schedule_enabled": self.recovery_config.get("use_schedule", True),
            "schedule_status": schedule_status,
            "block_status": block_status
        }
    
    def update_recovery_config(self, new_config: Dict):
        """Päivitä palautuskonfiguraatiota"""
        self.recovery_config.update(new_config)
        self._save_recovery_config()
        print(f"✅ Palautuskonfiguraatio päivitetty: {new_config}")
    
    def emergency_recovery(self) -> Dict:
        """Hätäpalautus - ohittaa kaikki rajoitukset"""
        print("🚨 HÄTÄPALAUTUS AKTIVOITU!")
        print(f"   Nimiavaruus: {self.namespace}")
        
        # 1. Kerää kaikki saatavilla olevat varaukset
        all_backups = self._collect_all_backups()
        
        if not all_backups:
            return {
                "success": False,
                "error": "Ei varauksia saatavilla hätäpalautukseen",
                "emergency_mode": True,
                "namespace": self.namespace
            }
        
        # 2. Valitse viimeisin varaus
        latest_backup = sorted(all_backups, key=lambda x: x["backup_timestamp"], reverse=True)[0]
        
        # 3. Suorita hätäpalautus
        recovery_data = latest_backup["original_data"]
        recovery_result = self._execute_recovery(recovery_data, emergency_mode=True)
        
        result = {
            "success": True,
            "emergency_recovery": True,
            "recovery_timestamp": datetime.now(timezone.utc).isoformat(),
            "backup_used": latest_backup["backup_timestamp"],
            "data_type": latest_backup["data_type"],
            "recovery_result": recovery_result,
            "available_backups": len(all_backups),
            "node_id": self.node_id,
            "namespace": self.namespace
        }
        
        # 4. Kirjaa hätäpalautus system_chainiin
        try:
            from system_chain_manager import log_action
            log_action(
                "emergency_recovery",
                f"Hätäpalautus suoritettu - käytetty varmuuskopio: {latest_backup['data_type']}",
                user_id=self.node_id,
                metadata=result
            )
        except ImportError:
            print("⚠️  System chain ei saatavilla - skipataan kirjaus")
        
        print("✅ Hätäpalautus suoritettu onnistuneesti!")
        
        return result
    
    def _collect_all_backups(self) -> List[Dict]:
        """Kerää kaikki varausmerkinnät kaikista lohkoista"""
        
        all_entries = []
        blocks = ["urgent", "sync", "active", "buffer2"]  # buffer1 on tyhjä
        
        for block_name in blocks:
            try:
                entries = self.block_manager.read_from_block(block_name)
                # Lisää lohkon nimi jokaiseen merkintään
                for entry in entries:
                    entry["data"]["source_block"] = block_name
                    entry["data"]["namespace"] = self.namespace
                    all_entries.append(entry["data"])
            except Exception as e:
                print(f"⚠️  Ei voitu ladata lohkoa {block_name}: {e}")
        
        return all_entries
    
    def _execute_recovery(self, recovery_data: Dict, emergency_mode: bool = False) -> Dict:
        """Suorita varsinainen palautus"""
        
        recovery_actions = []
        
        if "questions" in recovery_data:
            recovery_actions.append("questions_restored")
            # Toteuta kysymysten palautus
            # TODO: Implementoi kysymysten palautuslogiikka
        
        if "candidates" in recovery_data:
            recovery_actions.append("candidates_restored") 
            # Toteuta ehdokkaiden palautus
            # TODO: Implementoi ehdokkaiden palautuslogiikka
        
        if "system_chain" in recovery_data:
            recovery_actions.append("system_chain_restored")
            # Toteuta system_chainin palautus
            # TODO: Implementoi system_chain palautuslogiikka
        
        if "election_config" in recovery_data:
            recovery_actions.append("election_config_restored")
            # Toteuta vaalikonfiguraation palautus
            # TODO: Implementoi vaalikonfiguraation palautus
        
        return {
            "actions_performed": recovery_actions,
            "data_types_restored": list(recovery_data.keys()),
            "recovery_timestamp": datetime.now(timezone.utc).isoformat(),
            "emergency_mode": emergency_mode,
            "node_id": self.node_id,
            "namespace": self.namespace
        }
    
    def _emergency_fallback_backup(self, data: Dict, data_type: str, 
                                 reservation_result: Dict = None) -> str:
        """Hätävaraus kun normaalit mekanismit epäonnistuvat"""
        
        print("🚨 HÄTÄVARAUS AKTIVOITU!")
        print(f"   Nimiavaruus: {self.namespace}")
        
        # Yritä kirjoittaa suoraan kiireelliseen lohkoon
        try:
            entry_id = self.block_manager.write_to_block(
                "urgent", data, f"emergency_{data_type}", "emergency"
            )
            print(f"✅ Hätävaraus onnistui: {entry_id}")
            
            # Kirjaa hätävaraus system_chainiin
            try:
                from system_chain_manager import log_action
                log_action(
                    "emergency_backup",
                    f"Hätävaraus tehty: {data_type}",
                    user_id=self.node_id,
                    metadata={
                        "entry_id": entry_id,
                        "data_type": data_type,
                        "reservation_attempted": reservation_result is not None,
                        "reservation_success": reservation_result["success"] if reservation_result else False,
                        "namespace": self.namespace,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
            except ImportError:
                pass
            
            return entry_id
        except Exception as e:
            print(f"❌ Hätävaraus epäonnistui: {e}")
            # Viimeinen vaihtoehto: tallenna paikallisesti
            return self._local_emergency_backup(data, data_type)
    
    def _local_emergency_backup(self, data: Dict, data_type: str) -> str:
        """Paikallinen hätävaraus kun IPFS ei saatavilla"""
        
        emergency_dir = self.runtime_dir / "emergency_backups"
        emergency_dir.mkdir(exist_ok=True)
        
        filename = f"emergency_{self.namespace}_{data_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
        # Tässä simuloidaan dataa testaamista varten
        return []
    
    def _log_backup_to_chain(self, entry_id: str, data_type: str, priority: str, 
                           reservation_result: Dict = None):
        """Kirjaa varaus system_chainiin"""
        try:
            from system_chain_manager import log_action
            
            metadata = {
                "entry_id": entry_id,
                "data_type": data_type,
                "priority": priority,
                "node_id": self.node_id,
                "election_id": self.election_id,
                "namespace": self.namespace,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            if reservation_result and reservation_result["success"]:
                metadata["reservation_id"] = reservation_result["reservation_id"]
                metadata["scheduled_backup"] = True
            
            log_action(
                "intelligent_backup",
                f"Älykäs varaus tehty: {data_type} ({priority})",
                user_id=self.node_id,
                metadata=metadata
            )
        except ImportError:
            print("⚠️  System chain ei saatavilla - skipataan kirjaus")
    
    def _log_recovery_to_chain(self, recovery_result: Dict, reservation_result: Dict = None):
        """Kirjaa palautus system_chainiin"""
        try:
            from system_chain_manager import log_action
            
            metadata = recovery_result.copy()
            if reservation_result and reservation_result["success"]:
                metadata["reservation_id"] = reservation_result["reservation_id"]
                metadata["scheduled_recovery"] = True
            
            log_action(
                "system_recovery",
                f"Järjestelmäpalautus suoritettu: {recovery_result['data_type']}",
                user_id=self.node_id,
                metadata=metadata
            )
        except ImportError:
            print("⚠️  System chain ei saatavilla - skipataan kirjaus")
    
    def _log_sync_to_chain(self, sync_result: Dict, reservation_result: Dict = None):
        """Kirjaa synkronointi system_chainiin"""
        try:
            from system_chain_manager import log_action
            
            metadata = sync_result.copy()
            if reservation_result and reservation_result["success"]:
                metadata["reservation_id"] = reservation_result["reservation_id"]
                metadata["scheduled_sync"] = True
            
            log_action(
                "multi_node_sync",
                f"Moninodisynkronointi suoritettu: {sync_result['unique_entries']} merkintää",
                user_id=self.node_id,
                metadata=metadata
            )
        except ImportError:
            print("⚠️  System chain ei saatavilla - skipataan kirjaus")

# Singleton instance
_enhanced_recovery_manager = None

def get_enhanced_recovery_manager(runtime_dir: str = "runtime", ipfs_client=None, 
                                election_id: str = "default_election", 
                                node_id: str = "default_node") -> EnhancedRecoveryManager:
    """Hae EnhancedRecoveryManager-instanssi"""
    global _enhanced_recovery_manager
    if _enhanced_recovery_manager is None:
        _enhanced_recovery_manager = EnhancedRecoveryManager(
            runtime_dir, ipfs_client, election_id, node_id
        )
    return _enhanced_recovery_manager

# Testaus
if __name__ == "__main__":
    print("🧪 ENHANCED RECOVERY MANAGER TESTI - PÄIVITETTY NIMIAVARUUDELLA")
    print("=" * 60)
    
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
    test_data = {"questions": ["q1", "q2"], "timestamp": datetime.now(timezone.utc).isoformat()}
    
    recovery.perform_intelligent_backup(test_data, "test_backup", "normal")
    recovery.perform_intelligent_backup(test_data, "emergency_test", "emergency")
    recovery.perform_intelligent_backup(test_data, "high_priority_test", "high")
    
    # Tarkista status
    status = recovery.get_recovery_status()
    print("📊 PALAUTUSJÄRJESTELMÄN TILA:")
    print(f"   Varauksia: {status['total_backup_entries']}/{status['total_capacity']}")
    print(f"   Käyttö: {status['usage_percentage']:.1f}%")
    print(f"   Hätävarauksia: {status['emergency_backups']}")
    print(f"   Ajanvaraus käytössä: {status['schedule_enabled']}")
    print(f"   Nimiavaruus: {status['namespace']}")
    
    # Testaa moninodisynkronointi
    sync_result = recovery.multi_node_synchronization(["node_1", "node_2", "node_3"])
    print(f"🔗 Synkronointi: {sync_result['entries_processed']} merkintää käsitelty")
    
    # Testaa hätäpalautus
    emergency_result = recovery.emergency_recovery()
    print(f"🚨 Hätäpalautus: {'✅ ONNISTUI' if emergency_result['success'] else '❌ EPÄONNISTUI'}")
