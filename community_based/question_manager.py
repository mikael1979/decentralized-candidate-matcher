# question_manager.py
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import threading

class QuestionManager:
    def __init__(self, runtime_dir: str = "runtime"):
        self.runtime_dir = Path(runtime_dir)
        self.tmp_file = self.runtime_dir / "tmp_new_questions.json"
        self.new_file = self.runtime_dir / "new_questions.json"
        self.questions_file = self.runtime_dir / "questions.json"
        
        # Synkronointisäännöt
        self.sync_rules = {
            "batch_size": 5,           # Vähimmäismäärä ennen synkronointia
            "time_interval_hours": 24, # Maksimiaika ennen pakkosynkronointia
            "max_batch_size": 20,      # Enimmäismäärä per synkronointi
            "auto_sync_enabled": True
        }
        
        # Seuraava synkronointi
        self.next_sync_time = datetime.now() + timedelta(hours=self.sync_rules["time_interval_hours"])
        self._start_background_sync()
    
    def _start_background_sync(self):
        """Käynnistä taustasynkronointi"""
        def sync_worker():
            while True:
                time.sleep(300)  # Tarkista 5 minuutin välein
                self._check_auto_sync()
        
        if self.sync_rules["auto_sync_enabled"]:
            thread = threading.Thread(target=sync_worker, daemon=True)
            thread.start()
    
    def _check_auto_sync(self):
        """Tarkista automaattisen synkronoinnin ehdot"""
        tmp_data = self._load_tmp_questions()
        current_count = len(tmp_data.get("questions", []))
        
        # 1. Määräpohjainen ehto
        if current_count >= self.sync_rules["batch_size"]:
            print(f"🔄 Määräehto täyttynyt: {current_count}/{self.sync_rules['batch_size']} kysymystä")
            self.sync_tmp_to_new()
            return
        
        # 2. Aikapohjainen ehto
        if datetime.now() >= self.next_sync_time and current_count > 0:
            print(f"🔄 Aikaehto täyttynyt: {current_count} kysymystä odottamassa")
            self.sync_tmp_to_new()
            return
    
    def sync_tmp_to_new(self, force: bool = False) -> Dict:
        """Synkronoi tmp_new_questions.json -> new_questions.json"""
        
        tmp_data = self._load_tmp_questions()
        tmp_questions = tmp_data.get("questions", [])
        
        if not tmp_questions and not force:
            return {"success": False, "error": "Ei kysymyksiä synkronoitavaksi"}
        
        # Lataa nykyinen new_questions.json
        new_data = self._load_new_questions()
        
        # Valitse synkronoitavat kysymykset
        if not force:
            batch_size = min(len(tmp_questions), self.sync_rules["max_batch_size"])
            questions_to_sync = tmp_questions[:batch_size]
        else:
            questions_to_sync = tmp_questions
        
        # Päivitä statukset
        for question in questions_to_sync:
            question["status"] = "awaiting_moderation"
            question["moved_to_new_at"] = datetime.now().isoformat()
            question["batch_id"] = f"batch_{int(datetime.now().timestamp())}"
        
        # Lisää new_questions.json:ään
        new_data["questions"].extend(questions_to_sync)
        
        # Poista synkroidut tmp:stä
        remaining_questions = tmp_questions[len(questions_to_sync):]
        tmp_data["questions"] = remaining_questions
        
        # Tallenna muutokset
        self._save_new_questions(new_data)
        self._save_tmp_questions(tmp_data)
        
        # Päivitä seuraava synkronointiaika
        self.next_sync_time = datetime.now() + timedelta(hours=self.sync_rules["time_interval_hours"])
        
        # Kirjaa system_chainiin
        from system_chain_manager import log_action
        log_action(
            "question_sync",
            f"Synkronoitu {len(questions_to_sync)} kysymystä tmp -> new",
            question_ids=[q.get("submission_id") for q in questions_to_sync],
            user_id="auto_sync_system",
            metadata={
                "batch_size": len(questions_to_sync),
                "remaining_in_tmp": len(remaining_questions),
                "trigger": "auto_batch" if not force else "manual_force"
            }
        )
        
        return {
            "success": True,
            "synced_count": len(questions_to_sync),
            "remaining_in_tmp": len(remaining_questions),
            "batch_id": questions_to_sync[0]["batch_id"] if questions_to_sync else None,
            "next_sync_time": self.next_sync_time.isoformat()
        }
    
    def submit_question(self, question_data: Dict, user_id: str) -> Dict:
        """Lähetä kysymys tmp-jonoon ja tarkista synkronointi"""
        
        # 1. Tallenna tmp-tiedostoon
        tmp_data = self._load_tmp_questions()
        
        submission_id = f"sub_{int(datetime.now().timestamp())}_{user_id}"
        question_data.update({
            "submission_id": submission_id,
            "user_id": user_id,
            "status": "pending",
            "submitted_at": datetime.now().isoformat(),
            "initial_elo_rating": 1000
        })
        
        tmp_data["questions"].append(question_data)
        self._save_tmp_questions(tmp_data)
        
        # 2. Tarkista synkronointiehdot heti
        current_count = len(tmp_data["questions"])
        if current_count >= self.sync_rules["batch_size"]:
            sync_result = self.sync_tmp_to_new()
            return {
                "success": True, 
                "submission_id": submission_id,
                "auto_synced": True,
                "sync_result": sync_result
            }
        
        return {
            "success": True,
            "submission_id": submission_id, 
            "auto_synced": False,
            "queue_position": current_count,
            "estimated_sync_time": self.next_sync_time.isoformat()
        }
    
    def get_sync_status(self) -> Dict:
        """Hae synkronoinnin nykytila"""
        tmp_data = self._load_tmp_questions()
        new_data = self._load_new_questions()
        
        return {
            "tmp_questions_count": len(tmp_data.get("questions", [])),
            "new_questions_count": len(new_data.get("questions", [])),
            "sync_rules": self.sync_rules,
            "next_sync_time": self.next_sync_time.isoformat(),
            "time_until_sync": str(self.next_sync_time - datetime.now()),
            "batch_size_progress": f"{len(tmp_data.get('questions', []))}/{self.sync_rules['batch_size']}"
        }
    
    def update_sync_rules(self, new_rules: Dict) -> bool:
        """Päivitä synkronointisääntöjä"""
        self.sync_rules.update(new_rules)
        self.next_sync_time = datetime.now() + timedelta(hours=self.sync_rules["time_interval_hours"])
        return True
    
    def _load_tmp_questions(self) -> Dict:
        """Lataa tmp_new_questions.json"""
        return self._load_json_file(self.tmp_file, default_structure={"questions": []})
    
    def _load_new_questions(self) -> Dict:
        """Lataa new_questions.json"""
        return self._load_json_file(self.new_file, default_structure={"questions": []})
    
    def _save_tmp_questions(self, data: Dict):
        """Tallenna tmp_new_questions.json"""
        self._save_json_file(self.tmp_file, data)
    
    def _save_new_questions(self, data: Dict):
        """Tallenna new_questions.json"""
        self._save_json_file(self.new_file, data)
    
    def _load_json_file(self, file_path: Path, default_structure: Dict = None) -> Dict:
        """Apufunktio JSON-tiedostojen lataamiseen"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return default_structure or {}
    
    def _save_json_file(self, file_path: Path, data: Dict):
        """Apufunktio JSON-tiedostojen tallentamiseen"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
