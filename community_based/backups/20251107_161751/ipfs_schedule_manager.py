#!/usr/bin/env python3
# ipfs_schedule_manager.py - KORJATTU VERSIO
"""
IPFS Schedule Manager - Hallitsee IPFS-synkronointien ajanvarauksia
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

class ReservationStatus(Enum):
    """Varauksen tilat"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class IPFSScheduleManager:
    """Yksinkertaistettu IPFS-ajanvarausmanageri"""
    
    def __init__(self, config_file: str = "ipfs_schedule_config.json"):
        self.config_file = Path(config_file)
        self.schedule_file = Path("runtime/ipfs_schedule.json")
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
        return {
            "schedule_config": {
                "time_slots": {
                    "buffer_before": {"duration_minutes": 5},
                    "urgent_reservation": {"duration_minutes": 15},
                    "node_reservation": {"duration_minutes": 30},
                    "buffer_after": {"duration_minutes": 10}
                },
                "scheduling_rules": {
                    "max_reservations_per_day": 24,
                    "advance_booking_hours": 24
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
                "total_reservations": 0
            },
            "reservations": [],
            "schedule_stats": {
                "reservations_today": 0,
                "conflicts_today": 0
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
    
    def request_reservation(self, reservation_type: ReservationType, node_id: str, 
                          urgency: str = "normal", metadata: Dict = None) -> Dict:
        """
        Pyydä ajanvarausta IPFS-synkronointiin
        
        Args:
            reservation_type: ReservationType enum
            node_id: Pyytävän noden ID
            urgency: "low", "normal", "high", "critical"
            metadata: Lisätietoja varauksesta
        """
        print(f"📅 Pyydetään ajanvarausta: {reservation_type.value} ({urgency}) - Node: {node_id}")
        
        # 1. Tarkista rajoitukset
        limit_check = self._check_reservation_limits(node_id)
        if not limit_check["allowed"]:
            return {
                "success": False,
                "error": "Reservation limit exceeded",
                "details": limit_check
            }
        
        # 2. Laske aikaikkuna
        time_slot = self._calculate_time_slot(reservation_type)
        
        # 3. Tarkista konfliktit
        conflict_check = self._check_schedule_conflicts(time_slot)
        
        if conflict_check["has_conflicts"] and urgency != "critical":
            return {
                "success": False,
                "error": "Schedule conflict detected",
                "conflicts": conflict_check["conflicts"],
                "suggested_times": conflict_check["suggestions"]
            }
        
        # 4. Luo varaus
        reservation = self._create_reservation(reservation_type, node_id, time_slot, urgency, metadata)
        
        # 5. Lisää ajanvaraukseen
        self.schedule["reservations"].append(reservation)
        self.schedule["metadata"]["total_reservations"] = len(self.schedule["reservations"])
        
        # 6. Tallenna
        self._save_schedule()
        
        print(f"✅ Ajanvaraus vahvistettu: {reservation['reservation_id']}")
        
        return {
            "success": True,
            "reservation_id": reservation["reservation_id"],
            "time_slot": time_slot,
            "status": ReservationStatus.CONFIRMED.value,
            "conflicts_resolved": conflict_check["has_conflicts"]
        }
    
    def _calculate_time_slot(self, reservation_type: ReservationType) -> Dict[str, datetime]:
        """Laske aikaikkuna varaukselle"""
        time_slots = self.config["schedule_config"]["time_slots"]
        now = datetime.now(timezone.utc)
        
        # Määritä kesto
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
            "total_duration_minutes": duration + buffer_before + buffer_after
        }
    
    def _check_schedule_conflicts(self, time_slot: Dict) -> Dict:
        """Tarkista aikaikkunakonfliktit"""
        conflicts = []
        
        for reservation in self.schedule["reservations"]:
            if reservation["status"] in ["confirmed", "in_progress"]:
                # Tarkista päällekkäisyys
                if self._time_slots_overlap(time_slot, reservation["time_slot"]):
                    conflicts.append({
                        "conflicting_reservation": reservation["reservation_id"],
                        "conflicting_node": reservation["node_id"]
                    })
        
        # Etsi ehdotuksia konfliktittomille ajoille
        suggestions = self._find_conflict_free_times(time_slot) if conflicts else []
        
        return {
            "has_conflicts": len(conflicts) > 0,
            "conflicts": conflicts,
            "suggestions": suggestions
        }
    
    def _time_slots_overlap(self, slot1: Dict, slot2: Dict) -> bool:
        """Tarkista päällekkäisyys kahden aikaikkunan välillä"""
        start1 = datetime.fromisoformat(slot1["reservation_start"]) if isinstance(slot1["reservation_start"], str) else slot1["reservation_start"]
        end1 = datetime.fromisoformat(slot1["reservation_end"]) if isinstance(slot1["reservation_end"], str) else slot1["reservation_end"]
        start2 = datetime.fromisoformat(slot2["reservation_start"]) if isinstance(slot2["reservation_start"], str) else slot2["reservation_start"]
        end2 = datetime.fromisoformat(slot2["reservation_end"]) if isinstance(slot2["reservation_end"], str) else slot2["reservation_end"]
        
        return (start1 < end2) and (start2 < end1)
    
    def _find_conflict_free_times(self, original_slot: Dict) -> List[Dict]:
        """Etsi konfliktittomia aikoja"""
        suggestions = []
        now = datetime.now(timezone.utc)
        duration = original_slot["total_duration_minutes"]
        
        # Ehdotus 1: 15 minuutin päästä
        suggestion1 = now + timedelta(minutes=15)
        if self._is_time_slot_available(suggestion1, duration):
            suggestions.append({
                "suggestion": "15_minutes",
                "time": suggestion1.isoformat(),
                "confidence": "high"
            })
        
        # Ehdotus 2: 30 minuutin päästä
        suggestion2 = now + timedelta(minutes=30)
        if self._is_time_slot_available(suggestion2, duration):
            suggestions.append({
                "suggestion": "30_minutes", 
                "time": suggestion2.isoformat(),
                "confidence": "high"
            })
        
        return suggestions
    
    def _is_time_slot_available(self, start_time: datetime, duration_minutes: int) -> bool:
        """Tarkista onko aikaikkuna vapaa"""
        test_slot = {
            "reservation_start": start_time,
            "reservation_end": start_time + timedelta(minutes=duration_minutes)
        }
        
        conflict_check = self._check_schedule_conflicts(test_slot)
        return not conflict_check["has_conflicts"]
    
    def _check_reservation_limits(self, node_id: str) -> Dict:
        """Tarkista noden varausrajat"""
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Laske tämän päivän varaukset
        todays_reservations = [
            r for r in self.schedule["reservations"]
            if r["node_id"] == node_id and 
            datetime.fromisoformat(r["created_at"]) > today_start
        ]
        
        rules = self.config["schedule_config"]["scheduling_rules"]
        max_per_day = rules.get("max_reservations_per_day", 24)
        
        if len(todays_reservations) >= max_per_day:
            return {
                "allowed": False,
                "reason": "Daily reservation limit exceeded",
                "reservations_today": len(todays_reservations),
                "limit": max_per_day
            }
        
        return {"allowed": True, "reservations_today": len(todays_reservations)}
    
    def _create_reservation(self, reservation_type: ReservationType, node_id: str, 
                          time_slot: Dict, urgency: str, metadata: Dict = None) -> Dict:
        """Luo uusi varaus"""
        reservation_id = f"res_{node_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            "reservation_id": reservation_id,
            "type": reservation_type.value,
            "node_id": node_id,
            "urgency": urgency,
            "time_slot": {
                "buffer_start": time_slot["buffer_start"].isoformat(),
                "reservation_start": time_slot["reservation_start"].isoformat(),
                "reservation_end": time_slot["reservation_end"].isoformat(),
                "buffer_end": time_slot["buffer_end"].isoformat()
            },
            "status": ReservationStatus.CONFIRMED.value,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
            "reservation_metadata": {
                "duration_minutes": time_slot["total_duration_minutes"],
                "timezone": "UTC"
            }
        }
    
    def get_schedule_status(self, node_id: str = None) -> Dict:
        """Hae ajanvarauksen tila"""
        now = datetime.now(timezone.utc)
        
        if node_id:
            node_reservations = [r for r in self.schedule["reservations"] if r["node_id"] == node_id]
        else:
            node_reservations = self.schedule["reservations"]
        
        # Erota menneet ja tulevat
        upcoming_reservations = [
            r for r in node_reservations
            if datetime.fromisoformat(r["time_slot"]["reservation_start"]) >= now
        ]
        
        return {
            "total_reservations": len(node_reservations),
            "upcoming": len(upcoming_reservations),
            "upcoming_reservations": upcoming_reservations[:3]
        }

# Testaus
if __name__ == "__main__":
    manager = IPFSScheduleManager()
    
    # Testaa varaus
    result = manager.request_reservation(
        ReservationType.NODE_SYNC,
        "test_node_123",
        urgency="normal"
    )
    
    print(f"Varauksen tulos: {result['success']}")
    if result["success"]:
        print(f"Varaus ID: {result['reservation_id']}")
    
    # Näytä status
    status = manager.get_schedule_status()
    print(f"Varauksia yhteensä: {status['total_reservations']}")
