# question_manager.py - PÄIVITETTY VERSIO IPFS-AJANVARAUKSELLA
#!/usr/bin/env python3
"""
Kysymysten hallinta - PÄIVITETTY IPFS-AJANVARAUKSELLA
"""

import json
import argparse
from datetime import datetime, timedelta
from datetime import timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
import threading
import time
import hashlib

# Singleton instance
_question_manager_instance = None

def get_question_manager(runtime_dir: str = "runtime"):
    """Singleton-funktio ilman rekursiota"""
    global _question_manager_instance
    if _question_manager_instance is None:
        _question_manager_instance = QuestionManager(runtime_dir)
    return _question_manager_instance

class ReservationType:
    """Ajanvarauksen tyypit"""
    URGENT = "urgent_reservation"
    NODE_SYNC = "node_reservation"
    DATA_BACKUP = "data_backup"
    SYSTEM_SYNC = "system_sync"

class ReservationStatus:
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
    
    def request_reservation(self, reservation_type: str, node_id: str, 
                          urgency: str = "normal") -> Dict:
        """
        Pyydä ajanvarausta IPFS-synkronointiin
        """
        print(f"📅 Pyydetään ajanvarausta: {reservation_type} ({urgency})")
        
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
        reservation = self._create_reservation(reservation_type, node_id, time_slot, urgency)
        
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
            "status": ReservationStatus.CONFIRMED,
            "conflicts_resolved": conflict_check["has_conflicts"]
        }
    
    def _calculate_time_slot(self, reservation_type: str) -> Dict[str, datetime]:
        """Laske aikaikkuna varaukselle"""
        time_slots = self.config["schedule_config"]["time_slots"]
        now = datetime.now(timezone.utc)
        
        # Määritä kesto
        slot_config = time_slots.get(reservation_type, {})
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
    
    def _create_reservation(self, reservation_type: str, node_id: str, 
                          time_slot: Dict, urgency: str) -> Dict:
        """Luo uusi varaus"""
        reservation_id = f"res_{node_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            "reservation_id": reservation_id,
            "type": reservation_type,
            "node_id": node_id,
            "urgency": urgency,
            "time_slot": {
                "buffer_start": time_slot["buffer_start"].isoformat(),
                "reservation_start": time_slot["reservation_start"].isoformat(),
                "reservation_end": time_slot["reservation_end"].isoformat(),
                "buffer_end": time_slot["buffer_end"].isoformat()
            },
            "status": ReservationStatus.CONFIRMED,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metadata": {
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

class QuestionManager:
    """Hallinnoi kysymysten elinkaarta ja synkronointia - PÄIVITETTY IPFS-AJANVARAUKSELLA"""
    
    def __init__(self, runtime_dir: str = "runtime"):
        self.runtime_dir = Path(runtime_dir)
        self.tmp_file = self.runtime_dir / "tmp_new_questions.json"
        self.new_file = self.runtime_dir / "new_questions.json"
        self.questions_file = self.runtime_dir / "questions.json"
        self.active_file = self.runtime_dir / "active_questions.json"
        
        # Synkronointiasetukset
        self.sync_config = {
            "batch_size": 5,
            "max_batch_size": 20,
            "time_interval_hours": 24,
            "auto_sync_enabled": True,
            "use_schedule": True  # UUSI: Käytä ajanvarausta
        }
        
        # IPFS Ajanvarausmanageri
        self.schedule_manager = IPFSScheduleManager()
        
        # Synkronointi
        self._sync_lock = threading.Lock()
        self._load_sync_config()
        self._start_background_sync()
    
    def _load_sync_config(self):
        """Lataa synkronointikonfiguraatio"""
        config_file = self.runtime_dir / "sync_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.sync_config.update(loaded_config)
            except Exception as e:
                print(f"⚠️  Virhe synkronointikonfiguraatiota ladatessa: {e}")
    
    def _save_sync_config(self):
        """Tallenna synkronointikonfiguraatio"""
        config_file = self.runtime_dir / "sync_config.json"
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.sync_config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Virhe synkronointikonfiguraatiota tallennettaessa: {e}")
    
    def get_sync_status(self) -> Dict:
        """Hae synkronoinnin tila - PÄIVITETTY AJANVARAUSTIEDOILLA"""
        try:
            # Lataa tiedostot suoraan ilman muita funktiokutsuja
            tmp_count = self._count_questions_in_file(self.tmp_file)
            new_count = self._count_questions_in_file(self.new_file)
            main_count = self._count_questions_in_file(self.questions_file)
            
            next_sync = self._get_next_sync_time()
            
            # Hae ajanvarauksen tila
            schedule_status = self.schedule_manager.get_schedule_status(self._get_node_id())
            
            return {
                "tmp_questions_count": tmp_count,
                "new_questions_count": new_count,
                "main_questions_count": main_count,
                "batch_size": self.sync_config["batch_size"],
                "batch_size_progress": f"{tmp_count}/{self.sync_config['batch_size']}",
                "next_sync_time": next_sync,
                "time_until_sync": self._get_time_until_sync(next_sync),
                "auto_sync_enabled": self.sync_config["auto_sync_enabled"],
                "use_schedule": self.sync_config.get("use_schedule", True),
                "schedule_status": schedule_status,
                "sync_rules": self.sync_config
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "tmp_questions_count": 0,
                "new_questions_count": 0,
                "main_questions_count": 0
            }
    
    def _count_questions_in_file(self, file_path: Path) -> int:
        """Laske kysymysten määrä tiedostossa suoraan"""
        if not file_path.exists():
            return 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return len(data.get("questions", []))
        except:
            return 0
    
    def submit_question(self, question_data: Dict, user_id: str) -> Dict:
        """Lähetä uusi kysymys järjestelmään"""
        try:
            # Lataa nykyinen tmp-data
            tmp_data = self._load_tmp_data()
            
            # Luo uusi kysymys
            new_question = {
                "local_id": f"q{hashlib.sha256(str(datetime.now().isoformat()).encode()).hexdigest()[:8]}",
                "ipfs_cid": None,
                "source": "local",
                "content": question_data["content"],
                "elo_rating": {
                    "base_rating": 1000,
                    "current_rating": 1000,
                    "comparison_delta": 0,
                    "vote_delta": 0,
                    "total_comparisons": 0,
                    "total_votes": 0,
                    "up_votes": 0,
                    "down_votes": 0
                },
                "timestamps": {
                    "created_local": datetime.now(timezone.utc).isoformat(),
                    "modified_local": datetime.now(timezone.utc).isoformat()
                },
                "metadata": {
                    "submitted_by": user_id,
                    "status": "pending"
                }
            }
            
            # Lisää tmp-dataan
            tmp_data["questions"].append(new_question)
            tmp_data["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()
            tmp_data["metadata"]["total_questions"] = len(tmp_data["questions"])
            
            # Tallenna
            self._save_tmp_data(tmp_data)
            
            # Tarkista automaattinen synkronointi
            auto_synced = False
            sync_result = None
            
            if (self.sync_config["auto_sync_enabled"] and 
                len(tmp_data["questions"]) >= self.sync_config["batch_size"]):
                sync_result = self.sync_tmp_to_new()
                auto_synced = sync_result["success"]
            
            return {
                "success": True,
                "question_id": new_question["local_id"],
                "auto_synced": auto_synced,
                "sync_result": sync_result,
                "queue_position": len(tmp_data["questions"]),
                "estimated_sync_time": self._get_next_sync_time()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def sync_tmp_to_new(self, force: bool = False) -> Dict:
        """Synkronoi tmp-kysymykset new-kysymyksiin AJANVARAUKSEN KANSSA"""
        
        # Käytä ajanvarausta jos käytössä
        if self.sync_config.get("use_schedule", True) and not force:
            reservation = self.schedule_manager.request_reservation(
                ReservationType.NODE_SYNC,
                self._get_node_id(),
                urgency="high" if force else "normal"
            )
            
            if not reservation["success"]:
                return {
                    "success": False,
                    "error": f"Ei saatavilla aikaa synkronointiin: {reservation.get('error')}",
                    "suggested_times": reservation.get("suggested_times", []),
                    "use_force": "Käytä --force ohittaaksesi ajanvarauksen"
                }
            
            print(f"🕒 Synkronointi ajastettu: {reservation['reservation_id']}")
        
        # Suorita synkronointi
        with self._sync_lock:
            try:
                # Lataa data
                tmp_data = self._load_tmp_data()
                new_data = self._load_new_data()
                
                if not tmp_data["questions"]:
                    return {
                        "success": True,
                        "synced_count": 0,
                        "message": "Ei synkronoituvia kysymyksiä"
                    }
                
                # Määritä synkronoinnin koko
                if force:
                    batch_size = len(tmp_data["questions"])
                else:
                    batch_size = min(
                        self.sync_config["batch_size"],
                        len(tmp_data["questions"])
                    )
                
                # Siirrä kysymykset
                questions_to_sync = tmp_data["questions"][:batch_size]
                tmp_data["questions"] = tmp_data["questions"][batch_size:]
                
                # Päivitä statukset
                for question in questions_to_sync:
                    question["metadata"]["status"] = "approved"
                    question["metadata"]["approved_at"] = datetime.now(timezone.utc).isoformat()
                    question["timestamps"]["synced_to_new"] = datetime.now(timezone.utc).isoformat()
                
                # Lisää new-dataan
                new_data["questions"].extend(questions_to_sync)
                new_data["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()
                new_data["metadata"]["total_questions"] = len(new_data["questions"])
                
                # Tallenna
                self._save_tmp_data(tmp_data)
                self._save_new_data(new_data)
                
                # Kirjaa system_chainiin
                self._log_sync_to_chain(batch_size, "tmp_to_new")
                
                result = {
                    "success": True,
                    "synced_count": batch_size,
                    "remaining_in_tmp": len(tmp_data["questions"]),
                    "batch_id": f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
                
                # Lisää ajanvarauksen tiedot jos käytettiin
                if self.sync_config.get("use_schedule", True) and not force:
                    result["reservation_id"] = reservation["reservation_id"]
                    result["scheduled_sync"] = True
                
                return result
                
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "synced_count": 0
                }
    
    def sync_new_to_main(self, force: bool = False) -> Dict:
        """Synkronoi new-kysymykset pääkantaan AJANVARAUKSEN KANSSA"""
        
        # Käytä ajanvarausta jos käytössä
        if self.sync_config.get("use_schedule", True) and not force:
            reservation = self.schedule_manager.request_reservation(
                ReservationType.SYSTEM_SYNC,
                self._get_node_id(),
                urgency="high" if force else "normal"
            )
            
            if not reservation["success"]:
                return {
                    "success": False,
                    "error": f"Ei saatavilla aikaa synkronointiin: {reservation.get('error')}",
                    "suggested_times": reservation.get("suggested_times", [])
                }
            
            print(f"🕒 Pääkantaan synkronointi ajastettu: {reservation['reservation_id']}")
        
        try:
            # Lataa data
            new_data = self._load_new_data()
            questions_data = self._load_questions_data()
            
            if not new_data["questions"]:
                return {
                    "success": True,
                    "synced_count": 0,
                    "message": "Ei synkronoituvia kysymyksiä"
                }
            
            # Siirrä kaikki kysymykset
            questions_to_sync = new_data["questions"]
            new_data["questions"] = []
            
            # Lisää questions-dataan
            questions_data["questions"].extend(questions_to_sync)
            questions_data["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()
            questions_data["metadata"]["total_questions"] = len(questions_data["questions"])
            
            # Tallenna
            self._save_new_data(new_data)
            self._save_questions_data(questions_data)
            
            # Kirjaa system_chainiin
            self._log_sync_to_chain(len(questions_to_sync), "new_to_main")
            
            result = {
                "success": True,
                "synced_count": len(questions_to_sync),
                "batch_id": f"main_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
            
            # Lisää ajanvarauksen tiedot jos käytettiin
            if self.sync_config.get("use_schedule", True) and not force:
                result["reservation_id"] = reservation["reservation_id"]
                result["scheduled_sync"] = True
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def emergency_sync(self) -> Dict:
        """Hätäsynkronointi - ohittaa ajanvarauksen"""
        print("🚨 HÄTÄSYNKRONOINTI AKTIVOITU!")
        
        # Synkronoi kaikki välittömästi
        tmp_result = self.sync_tmp_to_new(force=True)
        main_result = self.sync_new_to_main(force=True)
        
        return {
            "emergency_sync": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tmp_sync": tmp_result,
            "main_sync": main_result,
            "node_id": self._get_node_id()
        }
    
    def update_sync_rules(self, new_rules: Dict):
        """Päivitä synkronointisääntöjä"""
        self.sync_config.update(new_rules)
        self._save_sync_config()
        
        # Ilmoita muutoksesta
        print(f"✅ Synkronointisäännöt päivitetty: {new_rules}")
    
    def _load_tmp_data(self) -> Dict:
        """Lataa tmp-data"""
        if self.tmp_file.exists():
            with open(self.tmp_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                "metadata": {
                    "created": datetime.now(timezone.utc).isoformat(),
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "total_questions": 0
                },
                "questions": []
            }
    
    def _save_tmp_data(self, data: Dict):
        """Tallenna tmp-data"""
        with open(self.tmp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _load_new_data(self) -> Dict:
        """Lataa new-data"""
        if self.new_file.exists():
            with open(self.new_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                "metadata": {
                    "created": datetime.now(timezone.utc).isoformat(),
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "total_questions": 0
                },
                "questions": []
            }
    
    def _save_new_data(self, data: Dict):
        """Tallenna new-data"""
        with open(self.new_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _load_questions_data(self) -> Dict:
        """Lataa questions-data"""
        if self.questions_file.exists():
            with open(self.questions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                "metadata": {
                    "created": datetime.now(timezone.utc).isoformat(),
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "total_questions": 0
                },
                "questions": []
            }
    
    def _save_questions_data(self, data: Dict):
        """Tallenna questions-data"""
        with open(self.questions_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _get_next_sync_time(self) -> str:
        """Laske seuraavan synkronoinnin aika"""
        last_sync_file = self.runtime_dir / "last_sync.txt"
        
        if last_sync_file.exists():
            with open(last_sync_file, 'r') as f:
                last_sync = datetime.fromisoformat(f.read().strip())
        else:
            last_sync = datetime.now(timezone.utc)
        
        next_sync = last_sync + timedelta(hours=self.sync_config["time_interval_hours"])
        return next_sync.isoformat()
    
    def _get_time_until_sync(self, next_sync_time: str) -> str:
        """Laske aikaa seuraavaan synkronointiin"""
        next_sync = datetime.fromisoformat(next_sync_time)
        now = datetime.now(timezone.utc)
        
        if now >= next_sync:
            return "Nyt"
        
        delta = next_sync - now
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        
        return f"{hours}h {minutes}min"
    
    def _start_background_sync(self):
        """Käynnistä taustasynkronointi"""
        def background_sync():
            while True:
                try:
                    # Tarkista synkronointi 5 minuutin välein
                    time.sleep(300)
                    
                    # Tarkista onko aika synkronoida
                    next_sync = self._get_next_sync_time()
                    if datetime.now(timezone.utc) >= datetime.fromisoformat(next_sync):
                        print("🔄 Taustasynkronointi käynnistyy...")
                        self.sync_tmp_to_new()
                        
                        # Päivitä viimeisen synkronoinnin aika
                        with open(self.runtime_dir / "last_sync.txt", 'w') as f:
                            f.write(datetime.now(timezone.utc).isoformat())
                            
                except Exception as e:
                    print(f"⚠️  Taustasynkronointivirhe: {e}")
        
        sync_thread = threading.Thread(target=background_sync, daemon=True)
        sync_thread.start()
    
    def _check_auto_sync(self) -> bool:
        """Tarkista täyttävätkö ehdot automaattiselle synkronointiin"""
        tmp_data = self._load_tmp_data()
        
        # Tarkista määrä
        if len(tmp_data["questions"]) >= self.sync_config["batch_size"]:
            return True
        
        # Tarkista aika
        next_sync = self._get_next_sync_time()
        if datetime.now(timezone.utc) >= datetime.fromisoformat(next_sync):
            return True
        
        return False
    
    def _log_sync_to_chain(self, count: int, sync_type: str):
        """Kirjaa synkronointi system_chainiin"""
        try:
            from system_chain_manager import log_action
            log_action(
                "question_sync",
                f"Synkronoitu {count} kysymystä ({sync_type})",
                question_ids=[],
                user_id="question_manager",
                metadata={
                    "sync_type": sync_type,
                    "question_count": count,
                    "batch_size": self.sync_config["batch_size"],
                    "node_id": self._get_node_id(),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        except ImportError:
            pass  # System chain ei saatavilla
    
    def _get_node_id(self) -> str:
        """Hae noden ID"""
        try:
            from metadata_manager import get_metadata_manager
            manager = get_metadata_manager()
            info = manager.get_machine_info()
            return info.get('machine_id', 'unknown_node')
        except:
            return 'unknown_node'
    
    def get_schedule_info(self) -> Dict:
        """Hae ajanvarauksen tiedot"""
        return self.schedule_manager.get_schedule_status(self._get_node_id())

# Testaus
if __name__ == "__main__":
    manager = get_question_manager()
    status = manager.get_sync_status()
    
    print("🔍 QUESTION MANAGER TESTI - PÄIVITETTY")
    print("=" * 50)
    print(f"Tmp-kysymyksiä: {status['tmp_questions_count']}")
    print(f"New-kysymyksiä: {status['new_questions_count']}")
    print(f"Pääkannan kysymyksiä: {status['main_questions_count']}")
    print(f"Seuraava synkronointi: {status['next_sync_time']}")
    print(f"Ajanvaraus käytössä: {status.get('use_schedule', False)}")
    
    # Näytä ajanvarauksen tila
    schedule_info = status.get('schedule_status', {})
    print(f"Tulevat varaukset: {schedule_info.get('upcoming', 0)}")
    
    # Testaa hätäsynkronointi
    print("\n🚨 Testaa hätäsynkronointi:")
    emergency_result = manager.emergency_sync()
    print(f"Hätäsynkronointi: {'✅ ONNISTUI' if emergency_result['tmp_sync']['success'] else '❌ EPÄONNISTUI'}")
