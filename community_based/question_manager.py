# question_manager.py
#!/usr/bin/env python3
"""
Question Manager - Kysymysten hallinta ja synkronointi - KORJATTU VERSIO
"""

import json
import time
import threading
from datetime import datetime, timedelta
from datetime import timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
import hashlib

# 🔒 LISÄTTY: Järjestelmän käynnistystarkistus
try:
    from system_bootstrap import verify_system_startup
    # HUOM: Ei pakoteta pysäytystä, vain varoitus
    startup_ok = verify_system_startup()
    if not startup_ok:
        print("⚠️  System bootstrap tarkistus epäonnistui - jatketaan varoituksella")
except ImportError:
    print("⚠️  System bootstrap ei saatavilla - jatketaan ilman tarkistusta")

class QuestionManager:
    """Hallinnoi kysymysten synkronointia tmp_new_questions -> new_questions -> questions"""
    
    def __init__(self, runtime_dir: str = "runtime"):
        self.runtime_dir = Path(runtime_dir)
        self.tmp_file = self.runtime_dir / "tmp_new_questions.json"
        self.new_file = self.runtime_dir / "new_questions.json" 
        self.questions_file = self.runtime_dir / "questions.json"
        
        # Synkronointisäännöt
        self.sync_rules = {
            "batch_size": 5,
            "max_batch_size": 20,
            "time_interval_hours": 24,
            "auto_sync": True
        }
        
        # Taustasynkronointi
        self._sync_thread = None
        self._stop_sync = False
        
        # Käynnistä taustasynkronointi
        if self.sync_rules["auto_sync"]:
            self._start_background_sync()
    
    def submit_question(self, question_data: Dict, user_id: str) -> Dict:
        """
        Lähetä uusi kysymys järjestelmään
        
        Returns:
            Dict jossa tieto onnistumisesta ja synkronoinnista
        """
        try:
            # Lataa nykyiset tmp-kysymykset
            tmp_questions = self._load_tmp_questions()
            
            # Lisää metadata
            question_data["submitted_by"] = user_id
            question_data["submitted_at"] = datetime.now(timezone.utc).isoformat()
            question_data["status"] = "pending"
            
            # Generoi ID jos ei ole
            if "local_id" not in question_data:
                question_data["local_id"] = f"q_{int(time.time())}_{hashlib.md5(user_id.encode()).hexdigest()[:8]}"
            
            # Lisää tmp-listalle
            tmp_questions.append(question_data)
            
            # Tallenna
            self._save_tmp_questions(tmp_questions)
            
            # Tarkista automaattinen synkronointi
            auto_synced = False
            sync_result = None
            
            if len(tmp_questions) >= self.sync_rules["batch_size"] and self.sync_rules["auto_sync"]:
                sync_result = self.sync_tmp_to_new()
                auto_synced = sync_result["success"]
            
            return {
                "success": True,
                "question_id": question_data["local_id"],
                "auto_synced": auto_synced,
                "sync_result": sync_result,
                "queue_position": len(tmp_questions),
                "estimated_sync_time": self._get_next_sync_time()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def sync_tmp_to_new(self, force: bool = False) -> Dict:
        """
        Synkronoi kysymykset tmp_new_questions.json -> new_questions.json
        
        Args:
            force: Pakota synkronointi vaikka batch-koko ei täyttyisi
            
        Returns:
            Synkronoinnin tulos
        """
        try:
            # Lataa tmp-kysymykset
            tmp_questions = self._load_tmp_questions()
            
            if not tmp_questions:
                return {
                    "success": True,
                    "synced_count": 0,
                    "remaining_in_tmp": 0,
                    "message": "Ei kysymyksiä synkronoitavaksi"
                }
            
            # Päätä kuinka monta kysymystä synkronoidaan
            if force:
                sync_count = min(len(tmp_questions), self.sync_rules["max_batch_size"])
            else:
                sync_count = min(len(tmp_questions), self.sync_rules["batch_size"])
            
            if sync_count == 0:
                return {
                    "success": True,
                    "synced_count": 0,
                    "remaining_in_tmp": len(tmp_questions),
                    "message": "Batch-koko ei täyty"
                }
            
            # Valitse synkronoitavat kysymykset
            questions_to_sync = tmp_questions[:sync_count]
            remaining_questions = tmp_questions[sync_count:]
            
            # Lataa nykyiset new-kysymykset
            new_questions = self._load_new_questions()
            
            # Lisää uudet kysymykset
            for question in questions_to_sync:
                question["synced_at"] = datetime.now(timezone.utc).isoformat()
                question["status"] = "awaiting_moderation"
                new_questions.append(question)
            
            # Tallenna
            self._save_new_questions(new_questions)
            self._save_tmp_questions(remaining_questions)
            
            # Kirjaa system_chainiin
            try:
                from system_chain_manager import log_action
                log_action(
                    "question_sync",
                    f"Synkronoitu {sync_count} kysymystä tmp -> new",
                    question_ids=[q["local_id"] for q in questions_to_sync],
                    user_id="question_manager",
                    metadata={
                        "synced_count": sync_count,
                        "remaining_in_tmp": len(remaining_questions),
                        "total_in_new": len(new_questions),
                        "batch_size": self.sync_rules["batch_size"]
                    }
                )
            except ImportError:
                pass  # System chain ei saatavilla
            
            return {
                "success": True,
                "synced_count": sync_count,
                "remaining_in_tmp": len(remaining_questions),
                "batch_id": f"batch_{int(time.time())}",
                "synced_questions": [q["local_id"] for q in questions_to_sync]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "synced_count": 0
            }
    
    def get_sync_status(self) -> Dict:
        """Hae synkronoinnin tila"""
        try:
            tmp_questions = self._load_tmp_questions()
            new_questions = self._load_new_questions()
            
            # Laske seuraava synkronointiaika
            next_sync = self._get_next_sync_time()
            time_until_sync = self._get_time_until_sync()
            
            # Laske edistyminen
            batch_progress = f"{len(tmp_questions)}/{self.sync_rules['batch_size']}"
            
            return {
                "tmp_questions_count": len(tmp_questions),
                "new_questions_count": len(new_questions),
                "batch_size_progress": batch_progress,
                "next_sync_time": next_sync,
                "time_until_sync": time_until_sync,
                "sync_rules": self.sync_rules,
                "auto_sync_enabled": self.sync_rules["auto_sync"]
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "tmp_questions_count": 0,
                "new_questions_count": 0
            }
    
    def update_sync_rules(self, new_rules: Dict):
        """Päivitä synkronointisääntöjä"""
        self.sync_rules.update(new_rules)
        
        # Käynnistä uudelleen taustasynkronointi jos tarpeen
        if self._sync_thread and not self.sync_rules["auto_sync"]:
            self._stop_background_sync()
        elif not self._sync_thread and self.sync_rules["auto_sync"]:
            self._start_background_sync()
    
    def _load_tmp_questions(self) -> List[Dict]:
        """Lataa tmp-kysymykset"""
        return self._load_json_file(self.tmp_file, [])
    
    def _save_tmp_questions(self, questions: List[Dict]):
        """Tallenna tmp-kysymykset"""
        self._save_json_file(self.tmp_file, questions)
    
    def _load_new_questions(self) -> List[Dict]:
        """Lataa new-kysymykset"""
        return self._load_json_file(self.new_file, [])
    
    def _save_new_questions(self, questions: List[Dict]):
        """Tallenna new-kysymykset"""
        self._save_json_file(self.new_file, questions)
    
    def _load_json_file(self, file_path: Path, default: Any = None) -> Any:
        """Lataa JSON-tiedosto"""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return default if default is not None else []
    
    def _save_json_file(self, file_path: Path, data: Any):
        """Tallenna JSON-tiedosto"""
        file_path.parent.mkdir(exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _get_next_sync_time(self) -> str:
        """Laske seuraava synkronointiaika"""
        next_sync = datetime.now(timezone.utc) + timedelta(hours=self.sync_rules["time_interval_hours"])
        return next_sync.isoformat()
    
    def _get_time_until_sync(self) -> str:
        """Laske aikaa seuraavaan synkronointiin"""
        next_sync = datetime.now(timezone.utc) + timedelta(hours=self.sync_rules["time_interval_hours"])
        time_left = next_sync - datetime.now(timezone.utc)
        
        hours = int(time_left.total_seconds() // 3600)
        minutes = int((time_left.total_seconds() % 3600) // 60)
        
        return f"{hours}h {minutes}min"
    
    def _start_background_sync(self):
        """Käynnistä taustasynkronointi"""
        if self._sync_thread and self._sync_thread.is_alive():
            return
        
        self._stop_sync = False
        
        def sync_loop():
            while not self._stop_sync:
                try:
                    self._check_auto_sync()
                    time.sleep(300)  # 5 minuuttia
                except:
                    time.sleep(60)  # 1 minuutti virhetilanteessa
        
        self._sync_thread = threading.Thread(target=sync_loop, daemon=True)
        self._sync_thread.start()
    
    def _stop_background_sync(self):
        """Pysäytä taustasynkronointi"""
        self._stop_sync = True
        if self._sync_thread:
            self._sync_thread.join(timeout=5)
            self._sync_thread = None
    
    def _check_auto_sync(self):
        """Tarkista ja suorita automaattinen synkronointi"""
        if not self.sync_rules["auto_sync"]:
            return
        
        tmp_questions = self._load_tmp_questions()
        
        # Synkronoi jos batch-koko täyttyy
        if len(tmp_questions) >= self.sync_rules["batch_size"]:
            self.sync_tmp_to_new()

# Singleton instance
_question_manager = None

def QuestionManager(runtime_dir: str = "runtime") -> QuestionManager:
    """Hae QuestionManager-instanssi"""
    global _question_manager
    if _question_manager is None:
        _question_manager = QuestionManager(runtime_dir)
    return _question_manager

# Yhteensopivuus vanhan koodin kanssa
get_question_manager = QuestionManager
