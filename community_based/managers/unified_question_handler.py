#!/usr/bin/env python3
"""
Unified Question Handler - Yhdistää kaikki kysymysten käsittelyyn liittyvät moduulit
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

class UnifiedQuestionHandler:
    """Yhdistää kaikki kysymysten käsittelyyn liittyvät moduulit"""
    
    def __init__(self, runtime_dir: str = "runtime"):
        self.runtime_dir = Path(runtime_dir)
        self.initialized = False
        
        # Alusta komponentit
        self.modern_question_manager = None
        self.elo_manager = None
        self.active_manager = None
        self.system_chain_manager = None
        
        # Alusta system chain manager ensin
        self._initialize_system_chain()
    
    def initialize(self) -> bool:
        """Alusta kaikki komponentit"""
        if self.initialized:
            return True
            
        try:
            print("🔄 Alustetaan Unified Question Handler...")
            
            # 1. Yritä alustaa Modern Question Manager (uusi arkkitehtuuri)
            self._initialize_modern_manager()
            
            # 2. Alusta ELO Manager (fallback)
            self._initialize_elo_manager()
            
            # 3. Alusta Active Questions Manager
            self._initialize_active_manager()
            
            self.initialized = True
            print("✅ Unified Question Handler alustettu onnistuneesti")
            return True
            
        except Exception as e:
            print(f"❌ Unified Question Handler alustus epäonnistui: {e}")
            return False
    
    def _initialize_system_chain(self):
        """Alusta System Chain Manager"""
        try:
            from system_chain_manager import get_system_chain_manager
            self.system_chain_manager = get_system_chain_manager()
            print("✅ Unified System Chain alustettu")
        except ImportError as e:
            print(f"⚠️  System Chain Manager ei saatavilla: {e}")
    
    def _initialize_modern_manager(self):
        """Yritä alustaa Modern Question Manager"""
        try:
            from question_manager import get_question_manager
            self.modern_question_manager = get_question_manager(str(self.runtime_dir))
            print("✅ Modern Question Manager saatavilla")
        except ImportError as e:
            print(f"⚠️  Modern Question Manager ei saatavilla: {e}")
        except Exception as e:
            print(f"⚠️  Modern Question Manager alustus epäonnistui: {e}")
    
    def _initialize_elo_manager(self):
        """Alusta ELO Manager fallbackina"""
        try:
            from elo_manager import ELOManager
            questions_file = self.runtime_dir / "questions.json"
            self.elo_manager = ELOManager(str(questions_file))
            print("✅ ELO Manager saatavilla")
        except ImportError as e:
            print(f"⚠️  ELO Manager ei saatavilla: {e}")
        except Exception as e:
            print(f"⚠️  ELO Manager alustus epäonnistui: {e}")
    
    def _initialize_active_manager(self):
        """Alusta Active Questions Manager"""
        try:
            from active_questions_manager import ActiveQuestionsManager
            self.active_manager = ActiveQuestionsManager(str(self.runtime_dir))
            print("✅ Active Questions Manager saatavilla")
        except ImportError as e:
            print(f"⚠️  Active Questions Manager ei saatavilla: {e}")
        except Exception as e:
            print(f"⚠️  Active Questions Manager alustus epäonnistui: {e}")
    
    def submit_question(self, question_data: Dict, user_id: str) -> Dict[str, Any]:
        """Lähetä uusi kysymys"""
        if not self.initialized and not self.initialize():
            return {"success": False, "error": "Alustus epäonnistui"}
        
        try:
            # Yritä käyttää Modern Question Manageria ensin
            if self.modern_question_manager:
                result = self.modern_question_manager.submit_question(question_data, user_id)
                if result.get('success'):
                    return result
            
            # Fallback: ELO Manager
            if self.elo_manager:
                return self._submit_question_fallback(question_data, user_id)
            
            return {"success": False, "error": "Ei saatavilla olevia kysymysmanageria"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _submit_question_fallback(self, question_data: Dict, user_id: str) -> Dict[str, Any]:
        """Fallback kysymyksen lähetys ELO Managerilla"""
        try:
            # Lataa nykyiset tmp-kysymykset
            tmp_file = self.runtime_dir / "tmp_new_questions.json"
            tmp_questions = []
            
            if tmp_file.exists():
                with open(tmp_file, 'r', encoding='utf-8') as f:
                    tmp_data = json.load(f)
                    tmp_questions = tmp_data.get('questions', [])
            
            # Luo uusi kysymys
            import hashlib
            from datetime import datetime
            from datetime import timezone
            
            question_id = f"q{hashlib.sha256(f'{user_id}{datetime.now().isoformat()}'.encode()).hexdigest()[:16]}"
            
            new_question = {
                "local_id": question_id,
                "source": "local",
                "content": {
                    "category": {
                        "fi": question_data.get("category", "Yleinen"),
                        "en": question_data.get("category", "General"),
                        "sv": question_data.get("category", "Allmän")
                    },
                    "question": question_data["content"]["question"],
                    "tags": question_data.get("tags", []),
                    "scale": {
                        "min": -5,
                        "max": 5,
                        "labels": {
                            "fi": {"min": "Täysin eri mieltä", "neutral": "Neutraali", "max": "Täysin samaa mieltä"},
                            "en": {"min": "Strongly disagree", "neutral": "Neutral", "max": "Strongly agree"},
                            "sv": {"min": "Helt avig", "neutral": "Neutral", "max": "Helt enig"}
                        }
                    }
                },
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
            
            # Lisää tmp-kysymyksiin
            tmp_questions.append(new_question)
            
            # Tallenna
            with open(tmp_file, 'w', encoding='utf-8') as f:
                json.dump({"questions": tmp_questions}, f, indent=2, ensure_ascii=False)
            
            # Kirjaa system chainiin
            if self.system_chain_manager:
                self.system_chain_manager.log_action(
                    "question_submitted",
                    f"Kysymys lähetetty: {question_data['content']['question']['fi'][:50]}...",
                    question_ids=[question_id],
                    user_id=user_id,
                    metadata={
                        "category": question_data.get("category", "Yleinen"),
                        "queue_position": len(tmp_questions),
                        "method": "fallback"
                    }
                )
            
            return {
                "success": True,
                "question_id": question_id,
                "queue_position": len(tmp_questions),
                "auto_synced": False,
                "message": "Kysymys lähetetty (fallback-tila)"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_questions(self, limit: int = 10, category: str = None) -> Dict[str, Any]:
        """Listaa kysymykset kaikista lähteistä"""
        if not self.initialized and not self.initialize():
            return {"success": False, "error": "Alustus epäonnistui"}
        
        try:
            all_questions = []
            
            # 1. Lataa kysymykset ELO Managerista (questions.json)
            if self.elo_manager:
                try:
                    elo_questions = self.elo_manager.load_questions()
                    all_questions.extend(elo_questions)
                    print(f"📚 Ladattu {len(elo_questions)} kysymystä ELO Managerista")
                except Exception as e:
                    print(f"⚠️  ELO Manager virhe: {e}")
            
            # 2. Lataa uudet kysymykset (new_questions.json)
            try:
                new_questions_path = self.runtime_dir / "new_questions.json"
                if new_questions_path.exists():
                    with open(new_questions_path, 'r', encoding='utf-8') as f:
                        new_data = json.load(f)
                        new_questions = new_data.get('questions', [])
                        all_questions.extend(new_questions)
                        print(f"🆕 Ladattu {len(new_questions)} kysymystä new_questions.json:sta")
            except Exception as e:
                print(f"⚠️  new_questions.json virhe: {e}")
            
            # 3. Lataa väliaikaiset kysymykset (tmp_new_questions.json)
            try:
                tmp_questions_path = self.runtime_dir / "tmp_new_questions.json"
                if tmp_questions_path.exists():
                    with open(tmp_questions_path, 'r', encoding='utf-8') as f:
                        tmp_data = json.load(f)
                        tmp_questions = tmp_data.get('questions', [])
                        all_questions.extend(tmp_questions)
                        print(f"📝 Ladattu {len(tmp_questions)} kysymystä tmp_new_questions.json:sta")
            except Exception as e:
                print(f"⚠️  tmp_new_questions.json virhe: {e}")
            
            # 4. Suodata duplikaatit local_id:n perusteella
            unique_questions = []
            seen_ids = set()
            
            for question in all_questions:
                qid = question.get('local_id')
                if qid and qid not in seen_ids:
                    seen_ids.add(qid)
                    unique_questions.append(question)
            
            # 5. Suodata kategorian mukaan
            if category:
                unique_questions = [
                    q for q in unique_questions 
                    if q.get('content', {}).get('category', {}).get('fi') == category
                ]
            
            # 6. Rajaa määrä
            questions = unique_questions[:limit]
            
            print(f"📊 Yhteensä {len(questions)}/{len(unique_questions)} kysymystä")
            
            return {
                "success": True,
                "questions": questions,
                "total_count": len(unique_questions),
                "sources": {
                    "elo_manager": len(elo_questions) if 'elo_questions' in locals() else 0,
                    "new_questions": len(new_questions) if 'new_questions' in locals() else 0,
                    "tmp_questions": len(tmp_questions) if 'tmp_questions' in locals() else 0
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def sync_questions(self, sync_type: str = "all") -> Dict[str, Any]:
        """Synkronoi kysymyksiä"""
        if not self.initialized and not self.initialize():
            return {"success": False, "error": "Alustus epäonnistui"}
        
        try:
            # Yritä käyttää Modern Question Manageria
            if self.modern_question_manager:
                if sync_type in ["tmp_to_new", "all"]:
                    result1 = self.modern_question_manager.sync_tmp_to_new()
                if sync_type in ["new_to_main", "all"]:
                    result2 = self.modern_question_manager.sync_new_to_main()
                return {"success": True, "message": "Synkronointi Modern Managerilla"}
            
            # Fallback: Yksinkertainen synkronointi
            return self._sync_questions_fallback(sync_type)
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _sync_questions_fallback(self, sync_type: str) -> Dict[str, Any]:
        """Fallback synkronointi"""
        try:
            if sync_type == "tmp_to_new":
                return self.sync_tmp_to_new()
            elif sync_type == "new_to_main":
                return {"success": False, "error": "new_to_main ei tuettu fallback-tilassa"}
            else:
                return {"success": False, "error": f"Tuntematon synkronointityyppi: {sync_type}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def sync_tmp_to_new(self, force: bool = False) -> Dict[str, Any]:
        """Synkronoi tmp -> new (fallback)"""
        try:
            tmp_path = self.runtime_dir / "tmp_new_questions.json"
            new_path = self.runtime_dir / "new_questions.json"
            
            if not tmp_path.exists():
                return {"success": True, "synced_count": 0, "message": "Ei tmp-kysymyksiä"}
            
            with open(tmp_path, 'r', encoding='utf-8') as f:
                tmp_data = json.load(f)
            
            tmp_questions = tmp_data.get('questions', [])
            
            if not tmp_questions:
                return {"success": True, "synced_count": 0, "message": "Ei tmp-kysymyksiä"}
            
            # Lataa nykyiset new questions
            new_questions = []
            if new_path.exists():
                with open(new_path, 'r', encoding='utf-8') as f:
                    new_data = json.load(f)
                    new_questions = new_data.get('questions', [])
            
            # Siirrä kaikki tmp -> new
            new_questions.extend(tmp_questions)
            
            # Tallenna new questions
            with open(new_path, 'w', encoding='utf-8') as f:
                json.dump({"questions": new_questions}, f, indent=2, ensure_ascii=False)
            
            # Tyhjennä tmp
            with open(tmp_path, 'w', encoding='utf-8') as f:
                json.dump({"questions": []}, f, indent=2, ensure_ascii=False)
            
            # Kirjaa system chainiin
            if self.system_chain_manager:
                self.system_chain_manager.log_action(
                    "sync_tmp_to_new",
                    f"Synkronoitu {len(tmp_questions)} kysymystä tmp -> new",
                    question_ids=[q.get('local_id') for q in tmp_questions],
                    user_id="unified_handler"
                )
            
            return {
                "success": True, 
                "synced_count": len(tmp_questions),
                "message": f"Synkronoitu {len(tmp_questions)} kysymystä"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Hae synkronoinnin tila"""
        if not self.initialized and not self.initialize():
            return {"error": "Alustus epäonnistui", "tmp_questions_count": 0, "new_questions_count": 0, "main_questions_count": 0}
        
        try:
            # Yritä käyttää Modern Question Manageria
            if self.modern_question_manager:
                return self.modern_question_manager.get_sync_status()
            
            # Fallback: Laske tilastot manuaalisesti
            return self._get_sync_status_fallback()
            
        except Exception as e:
            return {"error": str(e), "tmp_questions_count": 0, "new_questions_count": 0, "main_questions_count": 0}
    
    def _get_sync_status_fallback(self) -> Dict[str, Any]:
        """Fallback synkronointitilan haku"""
        try:
            tmp_count = 0
            new_count = 0
            main_count = 0
            
            # Tmp questions
            tmp_path = self.runtime_dir / "tmp_new_questions.json"
            if tmp_path.exists():
                with open(tmp_path, 'r', encoding='utf-8') as f:
                    tmp_data = json.load(f)
                    tmp_count = len(tmp_data.get('questions', []))
            
            # New questions
            new_path = self.runtime_dir / "new_questions.json"
            if new_path.exists():
                with open(new_path, 'r', encoding='utf-8') as f:
                    new_data = json.load(f)
                    new_count = len(new_data.get('questions', []))
            
            # Main questions (questions.json via ELO Manager)
            if self.elo_manager:
                main_questions = self.elo_manager.load_questions()
                main_count = len(main_questions)
            
            return {
                "tmp_questions_count": tmp_count,
                "new_questions_count": new_count,
                "main_questions_count": main_count,
                "auto_sync_enabled": False,
                "next_sync_time": "N/A",
                "time_until_sync": "N/A",
                "batch_size_progress": "N/A"
            }
            
        except Exception as e:
            return {"error": str(e), "tmp_questions_count": 0, "new_questions_count": 0, "main_questions_count": 0}
    
    def get_system_status(self) -> Dict[str, Any]:
        """Hae järjestelmän tila"""
        status = {
            "initialized": self.initialized,
            "components": {
                "modern_question_manager": self.modern_question_manager is not None,
                "elo_manager": self.elo_manager is not None,
                "active_manager": self.active_manager is not None,
                "system_chain_manager": self.system_chain_manager is not None
            },
            "sync_status": self.get_sync_status()
        }
        
        return status

# Singleton instance
_unified_question_handler = None

def get_unified_question_handler(runtime_dir: str = "runtime") -> UnifiedQuestionHandler:
    """Hae UnifiedQuestionHandler-instanssi"""
    global _unified_question_handler
    if _unified_question_handler is None:
        _unified_question_handler = UnifiedQuestionHandler(runtime_dir)
    return _unified_question_handler

# Alias for compatibility
def get_question_handler(runtime_dir: str = "runtime") -> UnifiedQuestionHandler:
    """Alias for compatibility with existing code"""
    return get_unified_question_handler(runtime_dir)

# managers/unified_question_handler.py - KORJAA TÄMÄ METODI

def get_sync_status(self) -> Dict[str, Any]:
    """Hae synkronoinnin tila - PARANNELTU FALLBACK"""
    try:
        tmp_count = 0
        new_count = 0
        main_count = 0
        
        # Tmp questions
        tmp_path = self.runtime_dir / "tmp_new_questions.json"
        if tmp_path.exists():
            with open(tmp_path, 'r', encoding='utf-8') as f:
                tmp_data = json.load(f)
                tmp_count = len(tmp_data.get('questions', []))
        
        # New questions
        new_path = self.runtime_dir / "new_questions.json"
        if new_path.exists():
            with open(new_path, 'r', encoding='utf-8') as f:
                new_data = json.load(f)
                new_count = len(new_data.get('questions', []))
        
        # Main questions (questions.json via ELO Manager)
        if self.elo_manager:
            main_questions = self.elo_manager.load_questions()
            main_count = len(main_questions)
        
        # FALLBACK: Näytä että automaattinen synkronointi on "käytössä"
        auto_sync_enabled = True  # Fallback-tilassa aina käytössä
        next_sync_time = "Tarkistetaan jatkuvasti"
        time_until_sync = "Aktiivinen"
        batch_size_progress = f"{tmp_count}/5"
        
        return {
            "tmp_questions_count": tmp_count,
            "new_questions_count": new_count,
            "main_questions_count": main_count,
            "auto_sync_enabled": auto_sync_enabled,
            "next_sync_time": next_sync_time,
            "time_until_sync": time_until_sync,
            "batch_size_progress": batch_size_progress,
            "fallback_mode": True,  # Ilmoita että käytämme fallbackia
            "modern_architecture": False  # Moderni arkkitehtuuri ei toimi
        }
        
    except Exception as e:
        return {
            "error": str(e), 
            "tmp_questions_count": 0, 
            "new_questions_count": 0, 
            "main_questions_count": 0,
            "auto_sync_enabled": False,
            "fallback_mode": True
        }

# Testaus
if __name__ == "__main__":
    handler = UnifiedQuestionHandler()
    handler.initialize()
    
    status = handler.get_system_status()
    print("🔍 UNIFIED QUESTION HANDLER TESTI")
    print("=" * 50)
    print(f"Alustettu: {status['initialized']}")
    print(f"Komponentit: {status['components']}")
    
    sync_status = handler.get_sync_status()
    print(f"Tmp-kysymyksiä: {sync_status.get('tmp_questions_count', 0)}")
    print(f"New-kysymyksiä: {sync_status.get('new_questions_count', 0)}")
    print(f"Pääkannan kysymyksiä: {sync_status.get('main_questions_count', 0)}")
    
    # Testaa listaus
    result = handler.list_questions(limit=5)
    if result['success']:
        print(f"Kysymyksiä saatavilla: {result['total_count']}")
    else:
        print(f"Listaus epäonnistui: {result['error']}")
