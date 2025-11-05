#!/usr/bin/env python3
"""
Unified Question Handler - Yhdistetty kysymysten käsittely
Käyttää: ModernQuestionManager + ELOManager + ActiveQuestionsManager
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from datetime import timezone

class UnifiedQuestionHandler:
    """Yhdistetty kysymysten käsittely - käyttää olemassa olevia moduuleja"""
    
    def __init__(self, runtime_dir: str = "runtime"):
        self.runtime_dir = Path(runtime_dir)
        self.initialized = False
        
    def initialize(self) -> bool:
        """Alusta kaikki tarvittavat komponentit"""
        try:
            # 1. Alusta Modern Question Manager (uusi arkkitehtuuri)
            try:
                from question_manager import get_question_manager
                self.modern_manager = get_question_manager(str(self.runtime_dir))
                print("✅ Modern Question Manager saatavilla")
            except ImportError as e:
                print(f"⚠️  Modern Question Manager ei saatavilla: {e}")
                self.modern_manager = None
            
            # 2. Alusta ELO Manager (perinteinen)
            try:
                from elo_manager import ELOManager
                self.elo_manager = ELOManager(str(self.runtime_dir / "questions.json"))
                print("✅ ELO Manager saatavilla")
            except ImportError as e:
                print(f"⚠️  ELO Manager ei saatavilla: {e}")
                self.elo_manager = None
            
            # 3. Alusta Active Questions Manager
            try:
                from active_questions_manager import ActiveQuestionsManager
                self.active_manager = ActiveQuestionsManager(str(self.runtime_dir))
                print("✅ Active Questions Manager saatavilla")
            except ImportError as e:
                print(f"⚠️  Active Questions Manager ei saatavilla: {e}")
                self.active_manager = None
            
            self.initialized = True
            print("✅ Unified Question Handler alustettu")
            return True
            
        except Exception as e:
            print(f"❌ Unified Question Handler alustus epäonnistui: {e}")
            return False
    
    def submit_question(self, question_data: Dict, user_id: str) -> Dict[str, Any]:
        """Lähetä kysymys - käyttää ModernQuestionManageria tai ELO Manageria fallbackina"""
        if not self.initialized and not self.initialize():
            return {"success": False, "error": "Alustus epäonnistui"}
        
        try:
            if self.modern_manager:
                # Käytä uutta arkkitehtuuria ensisijaisesti
                result = self.modern_manager.submit_question(question_data, user_id)
            elif self.elo_manager:
                # Fallback ELO Manageriin
                result = self._submit_with_elo_manager(question_data, user_id)
            else:
                return {"success": False, "error": "Kumpikaan kysymysmanageri ei saatavilla"}
            
            # Lokita unified system chainiin
            from managers.unified_system_chain import log_action
            log_action(
                action_type="question_submitted",
                description=f"Kysymys lähetetty: {question_data.get('content', {}).get('question', {}).get('fi', '')[:50]}...",
                question_ids=[result.get('question_id', 'unknown')],
                user_id=user_id,
                metadata={
                    "category": question_data.get('category', 'unknown'),
                    "manager_used": "modern" if self.modern_manager else "elo",
                    "success": result.get('success', False)
                }
            )
            
            return result
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _submit_with_elo_manager(self, question_data: Dict, user_id: str) -> Dict[str, Any]:
        """Lähetä kysymys käyttäen ELO Manageria"""
        try:
            # Luo kysymys ELO Managerin odottamassa muodossa
            new_question = {
                "local_id": f"q{hash(str(datetime.now(timezone.utc)))}",
                "content": {
                    "category": {
                        "fi": question_data.get("category", "general"),
                        "en": question_data.get("category", "general"),
                        "sv": question_data.get("category", "general")
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
                }
            }
            
            # Lisää kysymys ELO Managerin kautta
            success = self.elo_manager.add_question(new_question)
            
            if success:
                return {
                    "success": True,
                    "question_id": new_question["local_id"],
                    "queue_position": 1,
                    "auto_synced": False,
                    "message": "Kysymys lisätty ELO Managerin kautta"
                }
            else:
                return {"success": False, "error": "Kysymyksen lisäys epäonnistui"}
                
        except Exception as e:
            return {"success": False, "error": f"ELO Manager virhe: {str(e)}"}

    def handle_comparison(self, user_id: str, question_a_id: str, question_b_id: str,
                         result: str, user_trust: str = "regular_user") -> Dict[str, Any]:
        """Käsittele vertailu - käyttää ELO-manageria"""
        if not self.initialized and not self.initialize():
            return {"success": False, "error": "Alustus epäonnistui"}
        
        try:
            if self.elo_manager:
                result_data = self.elo_manager.handle_comparison(
                    user_id, question_a_id, question_b_id, result, user_trust
                )
                
                # Lokita unified system chainiin
                from managers.unified_system_chain import log_action
                log_action(
                    action_type="comparison_processed",
                    description=f"Vertailu: {question_a_id} vs {question_b_id} - {result}",
                    question_ids=[question_a_id, question_b_id],
                    user_id=user_id,
                    metadata={
                        "result": result,
                        "user_trust": user_trust,
                        "rating_changes": result_data.get('changes', {})
                    }
                )
                
                return result_data
            else:
                return {"success": False, "error": "ELO Manager ei saatavilla"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def handle_vote(self, user_id: str, question_id: str, vote_type: str,
                   confidence: int = 3, user_trust: str = "regular_user") -> Dict[str, Any]:
        """Käsittele ääni - käyttää ELO-manageria"""
        if not self.initialized and not self.initialize():
            return {"success": False, "error": "Alustus epäonnistui"}
        
        try:
            if self.elo_manager:
                result_data = self.elo_manager.handle_vote(
                    user_id, question_id, vote_type, confidence, user_trust
                )
                
                # Lokita unified system chainiin
                from managers.unified_system_chain import log_action
                log_action(
                    action_type="vote_processed",
                    description=f"Ääni: {vote_type} kysymykselle {question_id}",
                    question_ids=[question_id],
                    user_id=user_id,
                    metadata={
                        "vote_type": vote_type,
                        "confidence": confidence,
                        "user_trust": user_trust,
                        "rating_change": result_data.get('change', {})
                    }
                )
                
                return result_data
            else:
                return {"success": False, "error": "ELO Manager ei saatavilla"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def sync_questions(self, sync_type: str = "tmp_to_new", force: bool = False) -> Dict[str, Any]:
        """Synkronoi kysymykset - käyttää ModernQuestionManageria"""
        if not self.initialized and not self.initialize():
            return {"success": False, "error": "Alustus epäonnistui"}
        
        try:
            if self.modern_manager:
                if sync_type == "tmp_to_new":
                    result = self.modern_manager.sync_tmp_to_new(force)
                elif sync_type == "new_to_main":
                    result = self.modern_manager.sync_new_to_main(force)
                elif sync_type == "all":
                    # Suorita molemmat synkronoinnit
                    tmp_result = self.modern_manager.sync_tmp_to_new(force)
                    main_result = self.modern_manager.sync_new_to_main(force)
                    result = {
                        "success": tmp_result["success"] and main_result["success"],
                        "tmp_sync": tmp_result,
                        "main_sync": main_result
                    }
                else:
                    return {"success": False, "error": f"Tuntematon synkronointityyppi: {sync_type}"}
                
                # Lokita unified system chainiin
                from managers.unified_system_chain import log_action
                log_action(
                    action_type="questions_synced",
                    description=f"Kysymyksiä synkronoitu: {sync_type}",
                    user_id="system",
                    metadata={
                        "sync_type": sync_type,
                        "force": force,
                        "result": result
                    }
                )
                
                return result
            else:
                return {"success": False, "error": "Modern Question Manager ei saatavilla"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def sync_active_questions(self, election_id: str = None) -> Dict[str, Any]:
        """Synkronoi aktiiviset kysymykset"""
        if not self.initialized and not self.initialize():
            return {"success": False, "error": "Alustus epäonnistui"}
        
        try:
            if self.active_manager:
                result = self.active_manager.sync_active_questions(election_id)
                
                # Lokita unified system chainiin
                from managers.unified_system_chain import log_action
                log_action(
                    action_type="active_questions_synced",
                    description=f"Aktiivisia kysymyksiä synkronoitu",
                    user_id="system",
                    metadata=result
                )
                
                return result
            else:
                return {"success": False, "error": "Active Questions Manager ei saatavilla"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_system_status(self) -> Dict[str, Any]:
        """Hae järjestelmän tilanne"""
        if not self.initialized and not self.initialize():
            return {"error": "Alustus epäonnistui"}
        
        status = {
            "initialized": self.initialized,
            "managers_available": {
                "modern_question_manager": self.modern_manager is not None,
                "elo_manager": self.elo_manager is not None,
                "active_questions_manager": self.active_manager is not None
            }
        }
        
        # Hae kysymystilastot jos mahdollista
        try:
            if self.modern_manager:
                sync_status = self.modern_manager.get_sync_status()
                status["sync_status"] = sync_status
        except:
            status["sync_status"] = {"error": "Ei saatavilla"}
        
        return status

# Singleton instance
_question_handler = None

def get_question_handler(runtime_dir: str = "runtime") -> UnifiedQuestionHandler:
    """Hae UnifiedQuestionHandler-instanssi"""
    global _question_handler
    if _question_handler is None:
        _question_handler = UnifiedQuestionHandler(runtime_dir)
        _question_handler.initialize()
    return _question_handler

# Testaus
if __name__ == "__main__":
    print("🧪 UNIFIED QUESTION HANDLER TESTI")
    print("=" * 50)
    
    handler = UnifiedQuestionHandler()
    status = handler.get_system_status()
    
    print("📊 JÄRJESTELMÄN TILA:")
    print(f"   Alustettu: {status['initialized']}")
    print(f"   Modern Question Manager: {status['managers_available']['modern_question_manager']}")
    print(f"   ELO Manager: {status['managers_available']['elo_manager']}")
    print(f"   Active Questions Manager: {status['managers_available']['active_questions_manager']}")
    
    if status.get('sync_status'):
        print(f"   Synkronointitila: {status['sync_status'].get('tmp_questions_count', 0)} tmp-kysymystä")
    
    print("\n🎯 Unified Question Handler valmis!")

    def list_questions(self, limit: int = 10, category: str = None) -> Dict[str, Any]:
        """Listaa kysymykset"""
        if not self.initialized and not self.initialize():
            return {"success": False, "error": "Alustus epäonnistui"}
        
        try:
            if self.elo_manager:
                # Käytä ELO Manageria kysymysten listaukseen
                questions = self.elo_manager.load_questions()
                
                # Suodata kategorian mukaan jos annettu
                if category:
                    questions = [q for q in questions if q.get('content', {}).get('category', {}).get('fi') == category]
                
                # Rajaa määrä
                questions = questions[:limit]
                
                return {
                    "success": True,
                    "questions": questions,
                    "total_count": len(questions),
                    "limit": limit,
                    "category": category
                }
            else:
                return {"success": False, "error": "ELO Manager ei saatavilla"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
