# question_manager.py - LOPULLINEN KORJAUS
#!/usr/bin/env python3
"""
Kysymysten hallinta - KORJATTU REKURSIO-ONGELMA
"""

import json
import argparse
from datetime import datetime, timedelta
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

class QuestionManager:
    """Hallinnoi kysymysten elinkaarta ja synkronointia"""
    
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
            "auto_sync_enabled": True
        }
        
        # Taustasynkronointi
        self._sync_lock = threading.Lock()
        self._load_sync_config()
        self._start_background_sync()
    
    def _load_sync_config(self):
        """Lataa synkronointikonfiguraatio"""
        config_file = self.runtime_dir / "sync_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.sync_config.update(json.load(f))
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
        """Hae synkronoinnin tila - KORJATTU ILMAN REKURSIOA"""
        try:
            # Lataa tiedostot suoraan ilman muita funktiokutsuja
            tmp_count = self._count_questions_in_file(self.tmp_file)
            new_count = self._count_questions_in_file(self.new_file)
            main_count = self._count_questions_in_file(self.questions_file)
            
            next_sync = self._get_next_sync_time()
            
            return {
                "tmp_questions_count": tmp_count,
                "new_questions_count": new_count,
                "main_questions_count": main_count,
                "batch_size": self.sync_config["batch_size"],
                "batch_size_progress": f"{tmp_count}/{self.sync_config['batch_size']}",
                "next_sync_time": next_sync,
                "time_until_sync": self._get_time_until_sync(next_sync),
                "auto_sync_enabled": self.sync_config["auto_sync_enabled"],
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
                    "created_local": datetime.now().isoformat(),
                    "modified_local": datetime.now().isoformat()
                },
                "metadata": {
                    "submitted_by": user_id,
                    "status": "pending"
                }
            }
            
            # Lisää tmp-dataan
            tmp_data["questions"].append(new_question)
            tmp_data["metadata"]["last_updated"] = datetime.now().isoformat()
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
        """Synkronoi tmp-kysymykset new-kysymyksiin"""
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
                    question["metadata"]["approved_at"] = datetime.now().isoformat()
                
                # Lisää new-dataan
                new_data["questions"].extend(questions_to_sync)
                new_data["metadata"]["last_updated"] = datetime.now().isoformat()
                new_data["metadata"]["total_questions"] = len(new_data["questions"])
                
                # Tallenna
                self._save_tmp_data(tmp_data)
                self._save_new_data(new_data)
                
                # Kirjaa system_chainiin
                self._log_sync_to_chain(batch_size, "tmp_to_new")
                
                return {
                    "success": True,
                    "synced_count": batch_size,
                    "remaining_in_tmp": len(tmp_data["questions"]),
                    "batch_id": f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "synced_count": 0
                }
    
    def sync_new_to_main(self) -> Dict:
        """Synkronoi new-kysymykset pääkantaan"""
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
            questions_data["metadata"]["last_updated"] = datetime.now().isoformat()
            questions_data["metadata"]["total_questions"] = len(questions_data["questions"])
            
            # Tallenna
            self._save_new_data(new_data)
            self._save_questions_data(questions_data)
            
            # Kirjaa system_chainiin
            self._log_sync_to_chain(len(questions_to_sync), "new_to_main")
            
            return {
                "success": True,
                "synced_count": len(questions_to_sync),
                "batch_id": f"main_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_sync_rules(self, new_rules: Dict):
        """Päivitä synkronointisääntöjä"""
        self.sync_config.update(new_rules)
        self._save_sync_config()
    
    def _load_tmp_data(self) -> Dict:
        """Lataa tmp-data"""
        if self.tmp_file.exists():
            with open(self.tmp_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                "metadata": {
                    "created": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
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
                    "created": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
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
                    "created": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
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
            last_sync = datetime.now()
        
        next_sync = last_sync + timedelta(hours=self.sync_config["time_interval_hours"])
        return next_sync.isoformat()
    
    def _get_time_until_sync(self, next_sync_time: str) -> str:
        """Laske aikaa seuraavaan synkronointiin"""
        next_sync = datetime.fromisoformat(next_sync_time)
        now = datetime.now()
        
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
                    if datetime.now() >= datetime.fromisoformat(next_sync):
                        self.sync_tmp_to_new()
                        
                        # Päivitä viimeisen synkronoinnin aika
                        with open(self.runtime_dir / "last_sync.txt", 'w') as f:
                            f.write(datetime.now().isoformat())
                            
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
        if datetime.now() >= datetime.fromisoformat(next_sync):
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
                    "batch_size": self.sync_config["batch_size"]
                }
            )
        except ImportError:
            pass  # System chain ei saatavilla

# Testaus
if __name__ == "__main__":
    manager = get_question_manager()
    status = manager.get_sync_status()
    
    print("🔍 QUESTION MANAGER TESTI")
    print("=" * 40)
    print(f"Tmp-kysymyksiä: {status['tmp_questions_count']}")
    print(f"New-kysymyksiä: {status['new_questions_count']}")
    print(f"Pääkannan kysymyksiä: {status['main_questions_count']}")
    print(f"Seuraava synkronointi: {status['next_sync_time']}")
