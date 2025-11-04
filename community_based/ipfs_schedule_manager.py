#!/usr/bin/env python3
# ipfs_schedule_manager.py
"""
IPFS-synkronoinnin ajanvarausjärjestelmä
Hallitsee aikaikkunoita synkronoinneille ja estää konflikteja useiden nodien välillä
"""

import json
from datetime import datetime, timedelta
from datetime import timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum

class ReservationType(Enum):
    """Ajanvarauksen tyypit"""
    URGENT = "urgent_reservation"
    NODE_SYNC = "node_reservation" 
    DATA_BACKUP = "data_backup"
    SYSTEM_SYNC = "system_sync"
    RECOVERY = "recovery_operation"
    EMERGENCY = "emergency_backup"

class ReservationStatus(Enum):
    """Varauksen tilat"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    CONFLICT = "conflict"

class IPFSScheduleManager:
    """Hallinnoi IPFS-synkronoinnin ajanvarauksia"""
    
    def __init__(self, config_file: str = "ipfs_schedule_config.json", 
                 schedule_file: str = "runtime/ipfs_schedule.json"):
        self.config_file = Path(config_file)
        self.schedule_file = Path(schedule_file)
        self.config = self._load_config()
        self.schedule = self._load_schedule()
        
    def _load_config(self) -> Dict:
        """Lataa ajanvarauskonfiguraatio"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Virhe konfiguraatiota ladatessa: {e}")
        
        # Oletuskonfiguraatio
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Oletuskonfiguraatio"""
        return {
            "metadata": {
                "version": "1.0.0",
                "created": datetime.now(timezone.utc).isoformat(),
                "description": {
                    "fi": "IPFS-synkronoinnin ajanvarauskonfiguraatio",
                    "en": "IPFS synchronization scheduling configuration",
                    "sv": "IPFS-synkroniserings schemaläggningskonfiguration"
                }
            },
            "schedule_config": {
                "time_slots": {
                    "buffer_before": {
                        "duration_minutes": 5,
                        "purpose": {
                            "fi": "Tyhjä aika ennen varausta - estää konflikteja",
                            "en": "Empty time before reservation - prevents conflicts",
                            "sv": "Tom tid före reservation - förhindrar konflikter"
                        },
                        "reservable": False,
                        "priority": "low"
                    },
                    "urgent_reservation": {
                        "duration_minutes": 15,
                        "purpose": {
                            "fi": "Kiireelliset varaukset - kriittiset toiminnot",
                            "en": "Urgent reservations - critical operations", 
                            "sv": "Brådskande reservationer - kritiska operationer"
                        },
                        "reservable": True,
                        "priority": "critical",
                        "max_concurrent": 1
                    },
                    "node_reservation": {
                        "duration_minutes": 30,
                        "purpose": {
                            "fi": "Nodin oma varausaika - säännöllinen synkronointi",
                            "en": "Node's own reservation time - regular synchronization",
                            "sv": "Nodens egen reservationstid - regelbunden synkronisering"
                        },
                        "reservable": True,
                        "priority": "high",
                        "max_concurrent": 3
                    },
                    "buffer_after": {
                        "duration_minutes": 10,
                        "purpose": {
                            "fi": "Tyhjä aika varauksen jälkeen - siirtovaraa",
                            "en": "Empty time after reservation - buffer time",
                            "sv": "Tom tid efter reservation - bufferttid"
                        },
                        "reservable": False,
                        "priority": "low"
                    }
                },
                "scheduling_rules": {
                    "min_time_between_reservations": 2,
                    "max_reservations_per_hour": 6,
                    "max_reservations_per_day": 24,
                    "advance_booking_hours": 24,
                    "timezone": "UTC"
                },
                "conflict_resolution": {
                    "strategy": "timestamp_priority",
                    "auto_resolve": True,
                    "manual_intervention_threshold": 3
                }
            }
        }
    
    def _load_schedule(self) -> Dict:
        """Lataa ajanvarauskalenteri"""
        if self.schedule_file.exists():
            try:
                with open(self.schedule_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Virhe ajanvarausta ladatessa: {e}")
        
        # Uusi tyhjä ajanvaraus
        return {
            "metadata": {
                "created": datetime.now(timezone.utc).isoformat(),
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "total_reservations": 0,
                "description": {
                    "fi": "IPFS-synkronoinnin ajanvarauskalenteri",
                    "en": "IPFS synchronization schedule calendar",
                    "sv": "IPFS-synkroniserings schema kalender"
                }
            },
            "reservations": [],
            "conflicts": [],
            "schedule_stats": {
                "reservations_today": 0,
                "conflicts_today": 0,
                "last_sync": None,
                "total_nodes": 0
            }
        }
    
    def _save_schedule(self):
        """Tallenna ajanvarauskalenteri"""
        try:
            self.schedule["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()
            with open(self.schedule_file, 'w', encoding='utf-8') as f:
                json.dump(self.schedule, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Virhe ajanvarausta tallennettaessa: {e}")
    
    def request_reservation(self, reservation_type: ReservationType, 
                          node_id: str, duration_minutes: int = None,
                          urgency: str = "normal", metadata: Dict = None) -> Dict:
        """
        Pyydä ajanvarausta IPFS-synkronointiin
        
        Args:
            reservation_type: Varauksen tyyppi
            node_id: Varaavan noden ID
            duration_minutes: Kesto minuutteina (valinnainen)
            urgency: "low", "normal", "high", "critical"
            metadata: Lisämetadatat varaukselle
            
        Returns:
            Varauksen tulos
        """
        print(f"📅 Pyydetään ajanvarausta: {reservation_type.value} ({urgency}) - Node: {node_id}")
        
        # 1. Tarkista rajoitukset
        limit_check = self._check_reservation_limits(node_id, reservation_type)
        if not limit_check["allowed"]:
            conflict_data = {
                "detected_at": datetime.now(timezone.utc).isoformat(),
                "node_id": node_id,
                "reservation_type": reservation_type.value,
                "reason": limit_check["reason"],
                "resolved": False
            }
            self._record_conflict(conflict_data)
            
            return {
                "success": False,
                "error": "Reservation limit exceeded",
                "details": limit_check,
                "conflict_id": conflict_data.get("conflict_id")
            }
        
        # 2. Laske aikaikkuna
        time_slot = self._calculate_time_slot(reservation_type, duration_minutes)
        
        # 3. Tarkista konfliktit
        conflict_check = self._check_schedule_conflicts(time_slot, reservation_type)
        
        if conflict_check["has_conflicts"]:
            if urgency == "critical":
                # Kriittiset varaukset voivat ohittaa konfliktit
                print("🚨 Kriittinen varaus - ohitetaan konfliktit")
                conflict_check["conflicts_resolved"] = True
            else:
                conflict_data = {
                    "detected_at": datetime.now(timezone.utc).isoformat(),
                    "node_id": node_id,
                    "reservation_type": reservation_type.value,
                    "conflicts": conflict_check["conflicts"],
                    "resolved": False
                }
                self._record_conflict(conflict_data)
                
                return {
                    "success": False,
                    "error": "Schedule conflict detected",
                    "conflicts": conflict_check["conflicts"],
                    "suggested_times": conflict_check["suggestions"],
                    "conflict_id": conflict_data.get("conflict_id")
                }
        
        # 4. Luo varaus
        reservation = self._create_reservation(
            reservation_type, node_id, time_slot, urgency, metadata
        )
        
        # 5. Lisää ajanvaraukseen
        self.schedule["reservations"].append(reservation)
        self.schedule["metadata"]["total_reservations"] = len(self.schedule["reservations"])
        
        # 6. Päivitä tilastot
        self._update_schedule_stats()
        
        # 7. Tallenna
        self._save_schedule()
        
        # 8. Kirjaa system_chainiin
        self._log_reservation_to_chain(reservation)
        
        print(f"✅ Ajanvaraus vahvistettu: {reservation['reservation_id']}")
        
        return {
            "success": True,
            "reservation_id": reservation["reservation_id"],
            "time_slot": self._serialize_time_slot(time_slot),
            "status": ReservationStatus.CONFIRMED.value,
            "conflicts_resolved": conflict_check.get("conflicts_resolved", False),
            "node_id": node_id,
            "reservation_type": reservation_type.value
        }
    
    def _calculate_time_slot(self, reservation_type: ReservationType, 
                           custom_duration: int = None) -> Dict[str, datetime]:
        """Laske aikaikkuna varaukselle"""
        time_slots = self.config["schedule_config"]["time_slots"]
        now = datetime.now(timezone.utc)
        
        # Määritä kesto
        if custom_duration:
            duration = custom_duration
        else:
            slot_config = time_slots.get(reservation_type.value, {})
            duration = slot_config.get("duration_minutes", 30)
        
        # Laske aikaikkunan rajat bufferien kanssa
        buffer_before = time_slots["buffer_before"]["duration_minutes"]
        buffer_after = time_slots["buffer_after"]["duration_minutes"]
        
        start_time = now + timedelta(minutes=buffer_before)
        end_time = start_time + timedelta(minutes=duration)
        
        return {
            "buffer_start": now,
            "reservation_start": start_time,
            "reservation_end": end_time,
            "buffer_end": end_time + timedelta(minutes=buffer_after),
            "total_duration_minutes": duration + buffer_before + buffer_after,
            "reservation_type": reservation_type.value
        }
    
    def _check_schedule_conflicts(self, time_slot: Dict, reservation_type: ReservationType) -> Dict:
        """Tarkista aikaikkunakonfliktit"""
        conflicts = []
        
        for reservation in self.schedule["reservations"]:
            if reservation["status"] in ["confirmed", "in_progress"]:
                # Tarkista päällekkäisyys
                if self._time_slots_overlap(time_slot, reservation["time_slot"]):
                    conflicts.append({
                        "conflicting_reservation": reservation["reservation_id"],
                        "conflicting_node": reservation["node_id"],
                        "conflicting_type": reservation["type"],
                        "overlap_type": self._get_overlap_type(time_slot, reservation["time_slot"])
                    })
        
        # Tarkista samanaikaisuusrajoitukset
        concurrent_check = self._check_concurrent_limits(time_slot, reservation_type)
        if not concurrent_check["allowed"]:
            conflicts.extend(concurrent_check["conflicts"])
        
        # Etsi ehdotuksia konfliktittomille ajoille
        suggestions = self._find_conflict_free_times(time_slot, reservation_type) if conflicts else []
        
        return {
            "has_conflicts": len(conflicts) > 0,
            "conflicts": conflicts,
            "suggestions": suggestions,
            "concurrent_limits_ok": concurrent_check["allowed"]
        }
    
    def _check_concurrent_limits(self, time_slot: Dict, reservation_type: ReservationType) -> Dict:
        """Tarkista samanaikaisten varausten rajoitukset"""
        time_slots_config = self.config["schedule_config"]["time_slots"]
        slot_config = time_slots_config.get(reservation_type.value, {})
        max_concurrent = slot_config.get("max_concurrent", 1)
        
        # Laske samanaikaiset varaukset
        concurrent_reservations = []
        for reservation in self.schedule["reservations"]:
            if (reservation["status"] in ["confirmed", "in_progress"] and
                reservation["type"] == reservation_type.value and
                self._time_slots_overlap(time_slot, reservation["time_slot"])):
                concurrent_reservations.append(reservation)
        
        if len(concurrent_reservations) >= max_concurrent:
            return {
                "allowed": False,
                "conflicts": [{
                    "conflict_type": "concurrent_limit",
                    "limit": max_concurrent,
                    "current": len(concurrent_reservations),
                    "reservation_type": reservation_type.value
                }]
            }
        
        return {"allowed": True, "conflicts": []}
    
    def _time_slots_overlap(self, slot1: Dict, slot2: Dict) -> bool:
        """Tarkista päällekkäisyys kahden aikaikkunan välillä"""
        start1 = datetime.fromisoformat(slot1["reservation_start"]) if isinstance(slot1["reservation_start"], str) else slot1["reservation_start"]
        end1 = datetime.fromisoformat(slot1["reservation_end"]) if isinstance(slot1["reservation_end"], str) else slot1["reservation_end"]
        start2 = datetime.fromisoformat(slot2["reservation_start"]) if isinstance(slot2["reservation_start"], str) else slot2["reservation_start"]
        end2 = datetime.fromisoformat(slot2["reservation_end"]) if isinstance(slot2["reservation_end"], str) else slot2["reservation_end"]
        
        return (start1 < end2) and (start2 < end1)
    
    def _get_overlap_type(self, slot1: Dict, slot2: Dict) -> str:
        """Määritä päällekkäisyyden tyyppi"""
        start1 = datetime.fromisoformat(slot1["reservation_start"]) if isinstance(slot1["reservation_start"], str) else slot1["reservation_start"]
        end1 = datetime.fromisoformat(slot1["reservation_end"]) if isinstance(slot1["reservation_end"], str) else slot1["reservation_end"]
        start2 = datetime.fromisoformat(slot2["reservation_start"]) if isinstance(slot2["reservation_start"], str) else slot2["reservation_start"]
        end2 = datetime.fromisoformat(slot2["reservation_end"]) if isinstance(slot2["reservation_end"], str) else slot2["reservation_end"]
        
        if start1 <= start2 and end1 >= end2:
            return "complete_overlap"
        elif start1 >= start2 and end1 <= end2:
            return "contained_within"
        elif start1 < start2 < end1:
            return "partial_overlap_start"
        elif start1 < end2 < end1:
            return "partial_overlap_end"
        else:
            return "unknown"
    
    def _find_conflict_free_times(self, original_slot: Dict, reservation_type: ReservationType) -> List[Dict]:
        """Etsi konfliktittomia aikoja"""
        suggestions = []
        now = datetime.now(timezone.utc)
        duration = original_slot["total_duration_minutes"]
        
        # Etsi vapaita aikoja seuraavan 2 tunnin aikana
        for minutes_from_now in [15, 30, 45, 60, 90, 120]:
            suggestion_time = now + timedelta(minutes=minutes_from_now)
            if self._is_time_slot_available(suggestion_time, duration, reservation_type):
                confidence = "high" if minutes_from_now <= 60 else "medium"
                suggestions.append({
                    "suggestion": f"{minutes_from_now}_minutes",
                    "time": suggestion_time.isoformat(),
                    "confidence": confidence,
                    "minutes_from_now": minutes_from_now
                })
                # Löydettyään 3 ehdotusta, lopeta
                if len(suggestions) >= 3:
                    break
        
        return suggestions
    
    def _is_time_slot_available(self, start_time: datetime, duration_minutes: int, 
                              reservation_type: ReservationType) -> bool:
        """Tarkista onko aikaikkuna vapaa"""
        test_slot = {
            "reservation_start": start_time,
            "reservation_end": start_time + timedelta(minutes=duration_minutes),
            "reservation_type": reservation_type.value
        }
        
        conflict_check = self._check_schedule_conflicts(test_slot, reservation_type)
        return not conflict_check["has_conflicts"]
    
    def _check_reservation_limits(self, node_id: str, reservation_type: ReservationType) -> Dict:
        """Tarkista noden varausrajat"""
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        hour_start = now.replace(minute=0, second=0, microsecond=0)
        
        rules = self.config["schedule_config"]["scheduling_rules"]
        
        # Laske tämän päivän varaukset
        todays_reservations = [
            r for r in self.schedule["reservations"]
            if (r["node_id"] == node_id and 
                datetime.fromisoformat(r["created_at"]) > today_start)
        ]
        
        # Laske tämän tunnin varaukset
        hourly_reservations = [
            r for r in self.schedule["reservations"]
            if (r["node_id"] == node_id and 
                datetime.fromisoformat(r["created_at"]) > hour_start)
        ]
        
        max_per_day = rules.get("max_reservations_per_day", 24)
        max_per_hour = rules.get("max_reservations_per_hour", 6)
        
        if len(todays_reservations) >= max_per_day:
            return {
                "allowed": False,
                "reason": "Daily reservation limit exceeded",
                "reservations_today": len(todays_reservations),
                "limit": max_per_day,
                "period": "day"
            }
        
        if len(hourly_reservations) >= max_per_hour:
            return {
                "allowed": False,
                "reason": "Hourly reservation limit exceeded",
                "reservations_hour": len(hourly_reservations),
                "limit": max_per_hour,
                "period": "hour"
            }
        
        return {
            "allowed": True, 
            "reservations_today": len(todays_reservations),
            "reservations_hour": len(hourly_reservations)
        }
    
    def _create_reservation(self, reservation_type: ReservationType, node_id: str, 
                          time_slot: Dict, urgency: str, metadata: Dict = None) -> Dict:
        """Luo uusi varaus"""
        reservation_id = f"res_{node_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        reservation_data = {
            "reservation_id": reservation_id,
            "type": reservation_type.value,
            "node_id": node_id,
            "urgency": urgency,
            "time_slot": self._serialize_time_slot(time_slot),
            "status": ReservationStatus.CONFIRMED.value,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metadata": {
                "duration_minutes": time_slot["total_duration_minutes"],
                "timezone": "UTC",
                "reservation_type": reservation_type.value
            }
        }
        
        if metadata:
            reservation_data["metadata"].update(metadata)
        
        return reservation_data
    
    def _serialize_time_slot(self, time_slot: Dict) -> Dict:
        """Muunna datetime-objektit merkkijonoiksi"""
        return {
            "buffer_start": time_slot["buffer_start"].isoformat(),
            "reservation_start": time_slot["reservation_start"].isoformat(),
            "reservation_end": time_slot["reservation_end"].isoformat(),
            "buffer_end": time_slot["buffer_end"].isoformat(),
            "total_duration_minutes": time_slot["total_duration_minutes"]
        }
    
    def _record_conflict(self, conflict_data: Dict):
        """Tallenna konflikti"""
        conflict_data["conflict_id"] = f"conflict_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if "conflicts" not in self.schedule:
            self.schedule["conflicts"] = []
        
        self.schedule["conflicts"].append(conflict_data)
        self._save_schedule()
        
        print(f"⚠️  Konflikti tallennettu: {conflict_data['conflict_id']}")
    
    def _update_schedule_stats(self):
        """Päivitä ajanvarauksen tilastot"""
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Laske uniikit nodet
        unique_nodes = set(r["node_id"] for r in self.schedule["reservations"])
        
        todays_reservations = [
            r for r in self.schedule["reservations"]
            if datetime.fromisoformat(r["created_at"]) > today_start
        ]
        
        todays_conflicts = [
            c for c in self.schedule.get("conflicts", [])
            if datetime.fromisoformat(c.get("detected_at", now.isoformat())) > today_start
        ]
        
        self.schedule["schedule_stats"] = {
            "reservations_today": len(todays_reservations),
            "conflicts_today": len(todays_conflicts),
            "total_nodes": len(unique_nodes),
            "last_updated": now.isoformat()
        }
    
    def _log_reservation_to_chain(self, reservation: Dict):
        """Kirjaa varaus system_chainiin"""
        try:
            from system_chain_manager import log_action
            
            log_action(
                "ipfs_reservation",
                f"IPFS-aika varattu: {reservation['type']} - {reservation['reservation_id']}",
                user_id=reservation["node_id"],
                metadata={
                    "reservation_id": reservation["reservation_id"],
                    "reservation_type": reservation["type"],
                    "node_id": reservation["node_id"],
                    "urgency": reservation["urgency"],
                    "duration_minutes": reservation["metadata"]["duration_minutes"],
                    "time_slot": reservation["time_slot"]
                }
            )
        except ImportError:
            print("⚠️  System chain ei saatavilla - skipataan kirjaus")
    
    def get_schedule_status(self, node_id: str = None) -> Dict:
        """Hae ajanvarauksen tila"""
        now = datetime.now(timezone.utc)
        
        if node_id:
            # Tietyn noden varaukset
            node_reservations = [
                r for r in self.schedule["reservations"]
                if r["node_id"] == node_id
            ]
        else:
            # Kaikki varaukset
            node_reservations = self.schedule["reservations"]
        
        # Järjestä kronologisesti
        sorted_reservations = sorted(
            node_reservations,
            key=lambda x: x["time_slot"]["reservation_start"]
        )
        
        # Erota menneet ja tulevat
        past_reservations = [
            r for r in sorted_reservations
            if datetime.fromisoformat(r["time_slot"]["reservation_end"]) < now
        ]
        
        upcoming_reservations = [
            r for r in sorted_reservations
            if datetime.fromisoformat(r["time_slot"]["reservation_start"]) >= now
        ]
        
        # Etsi aktiiviset varaukset
        active_reservations = [
            r for r in sorted_reservations
            if (datetime.fromisoformat(r["time_slot"]["reservation_start"]) <= now and
                datetime.fromisoformat(r["time_slot"]["reservation_end"]) >= now)
        ]
        
        return {
            "total_reservations": len(sorted_reservations),
            "active_now": len(active_reservations),
            "upcoming": len(upcoming_reservations),
            "past": len(past_reservations),
            "upcoming_reservations": upcoming_reservations[:5],
            "active_reservations": active_reservations,
            "schedule_stats": self.schedule["schedule_stats"],
            "node_filter": node_id if node_id else "all_nodes"
        }
    
    def cancel_reservation(self, reservation_id: str, node_id: str) -> bool:
        """Peru varaus"""
        for reservation in self.schedule["reservations"]:
            if (reservation["reservation_id"] == reservation_id and 
                reservation["node_id"] == node_id):
                
                reservation["status"] = ReservationStatus.CANCELLED.value
                reservation["cancelled_at"] = datetime.now(timezone.utc).isoformat()
                reservation["cancelled_by"] = node_id
                
                self._save_schedule()
                
                # Kirjaa peruutus system_chainiin
                try:
                    from system_chain_manager import log_action
                    log_action(
                        "ipfs_reservation_cancelled",
                        f"Varaus peruttu: {reservation_id}",
                        user_id=node_id,
                        metadata={
                            "reservation_id": reservation_id,
                            "cancelled_at": reservation["cancelled_at"]
                        }
                    )
                except ImportError:
                    pass
                
                print(f"✅ Varaus peruttu: {reservation_id}")
                return True
        
        print(f"❌ Varausta ei löydy: {reservation_id}")
        return False
    
    def get_node_stats(self, node_id: str) -> Dict:
        """Hae noden tilastot"""
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        node_reservations = [r for r in self.schedule["reservations"] if r["node_id"] == node_id]
        todays_reservations = [r for r in node_reservations if datetime.fromisoformat(r["created_at"]) > today_start]
        
        # Ryhmittele varaukset tyypeittäin
        by_type = {}
        for reservation in node_reservations:
            res_type = reservation["type"]
            if res_type not in by_type:
                by_type[res_type] = 0
            by_type[res_type] += 1
        
        return {
            "node_id": node_id,
            "total_reservations": len(node_reservations),
            "reservations_today": len(todays_reservations),
            "reservations_by_type": by_type,
            "first_reservation": min([r["created_at"] for r in node_reservations]) if node_reservations else None,
            "last_reservation": max([r["created_at"] for r in node_reservations]) if node_reservations else None
        }

# Singleton instance
_schedule_manager_instance = None

def get_schedule_manager() -> IPFSScheduleManager:
    """Hae ajanvarausmanageri"""
    global _schedule_manager_instance
    if _schedule_manager_instance is None:
        _schedule_manager_instance = IPFSScheduleManager()
    return _schedule_manager_instance

# Testaus
if __name__ == "__main__":
    print("🧪 IPFS-AJANVARAUSJÄRJESTELMÄ")
    print("=" * 50)
    
    manager = get_schedule_manager()
    
    # Testaa varaus
    result = manager.request_reservation(
        ReservationType.NODE_SYNC,
        "test_node_1",
        urgency="normal",
        metadata={"purpose": "test_sync"}
    )
    
    if result["success"]:
        print(f"✅ Varaus onnistui: {result['reservation_id']}")
        print(f"   Aikaikkuna: {result['time_slot']['reservation_start']}")
    else:
        print(f"❌ Varaus epäonnistui: {result.get('error', 'Unknown error')}")
        if 'suggested_times' in result:
            print("   Ehdotetut ajat:")
            for suggestion in result['suggested_times']:
                print(f"   - {suggestion['time']} ({suggestion['confidence']})")
    
    # Näytä tila
    status = manager.get_schedule_status("test_node_1")
    print(f"📊 Ajanvarauksen tila: {status['total_reservations']} varausta")
    print(f"   Aktiivisia: {status['active_now']}")
    print(f"   Tulevia: {status['upcoming']}")
    
    # Näytä noden tilastot
    node_stats = manager.get_node_stats("test_node_1")
    print(f"📈 Noden tilastot: {node_stats['total_reservations']} varausta")
