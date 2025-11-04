#!/usr/bin/env python3
# elo_manager.py - KORJATTU VERSIO
"""
ELO Manager - Hallitsee kysymysten ELO-luokituksia
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from datetime import timezone

class ELOManager:
    """Hallinnoi kysymysten ELO-luokituksia - KORJATTU VERSIO"""
    
    def __init__(self, questions_file: str = "runtime/questions.json"):
        self.questions_file = Path(questions_file)
        self.questions = self._load_questions()
    
    def _load_questions(self) -> List[Dict]:
        """Lataa kysymykset tiedostosta"""
        if not self.questions_file.exists():
            return []
        
        try:
            with open(self.questions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('questions', [])
        except Exception as e:
            print(f"❌ Virhe ladattaessa kysymyksiä: {e}")
            return []
    
    def _save_questions(self):
        """Tallenna kysymykset tiedostoon"""
        try:
            data = {
                "metadata": {
                    "version": "2.0.0",
                    "total_questions": len(self.questions),
                    "last_updated": datetime.now(timezone.utc).isoformat()
                },
                "questions": self.questions
            }
            
            with open(self.questions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"❌ Virhe tallentaessa kysymyksiä: {e}")
    
    # TEHDÄÄN METODIT JULKISIKSI
    def load_questions(self) -> List[Dict]:
        """Lataa kysymykset (julkinen metodi)"""
        return self._load_questions()
    
    def save_questions(self):
        """Tallenna kysymykset (julkinen metodi)"""
        self._save_questions()
    
    def update_question_rating(self, question_id: str, rating_data: Dict):
        """Päivitä kysymyksen rating"""
        for question in self.questions:
            if question["local_id"] == question_id:
                # Päivitä rating
                question["elo_rating"]["current_rating"] = rating_data["new_rating"]
                
                # Päivitä deltat
                old_rating = rating_data["old_rating"]
                new_rating = rating_data["new_rating"]
                change = new_rating - old_rating
                
                if "comparison" in rating_data.get("type", ""):
                    question["elo_rating"]["comparison_delta"] += change
                elif "vote" in rating_data.get("type", ""):
                    question["elo_rating"]["vote_delta"] += change
                
                # Päivitä tilastot
                question["elo_rating"]["total_comparisons"] = question["elo_rating"].get("total_comparisons", 0) + 1
                
                break
    
    def get_question_by_id(self, question_id: str) -> Optional[Dict]:
        """Hae kysymys ID:llä"""
        for question in self.questions:
            if question["local_id"] == question_id:
                return question
        return None
    
    def get_top_questions(self, limit: int = 10) -> List[Dict]:
        """Hae parhaat kysymykset ratingin perusteella"""
        sorted_questions = sorted(self.questions, 
                                key=lambda x: x["elo_rating"]["current_rating"], 
                                reverse=True)
        return sorted_questions[:limit]
    
    def get_random_questions(self, count: int = 2) -> List[Dict]:
        """Hae satunnaisia kysymyksiä"""
        import random
        if len(self.questions) <= count:
            return self.questions
        return random.sample(self.questions, count)
    
    def add_question(self, question_data: Dict) -> bool:
        """Lisää uusi kysymys"""
        try:
            # Varmista että kysymyksellä on kaikki tarvittavat kentät
            required_fields = ["local_id", "content", "elo_rating", "timestamps"]
            for field in required_fields:
                if field not in question_data:
                    print(f"❌ Puuttuva kenttä: {field}")
                    return False
            
            # Lisää kysymys
            self.questions.append(question_data)
            self._save_questions()
            return True
            
        except Exception as e:
            print(f"❌ Virhe lisättäessä kysymystä: {e}")
            return False

    def handle_vote(self, user_id: str, question_id: str, vote_type: str, 
                   confidence: int, user_trust: str) -> Dict:
        """Käsittele ääni ELO-järjestelmässä - UUSI METODI"""
        try:
            from complete_elo_calculator import CompleteELOCalculator, VoteType, UserTrustLevel
            
            # Muunna enum-arvoiksi
            vote_enum = VoteType.UPVOTE if vote_type.lower() == "upvote" else VoteType.DOWNVOTE
            trust_enum = UserTrustLevel(user_trust)
            
            question = self.get_question_by_id(question_id)
            if not question:
                return {"success": False, "error": "Question not found"}
            
            calculator = CompleteELOCalculator()
            result = calculator.process_vote(question, vote_enum, confidence, trust_enum)
            
            if result["success"]:
                # Päivitä kysymys
                question["elo_rating"]["current_rating"] = result["change"]["new_rating"]
                question["elo_rating"]["vote_delta"] = result["change"]["change"]
                question["elo_rating"]["total_votes"] = question["elo_rating"].get("total_votes", 0) + 1
                
                if vote_enum == VoteType.UPVOTE:
                    question["elo_rating"]["up_votes"] = question["elo_rating"].get("up_votes", 0) + 1
                else:
                    question["elo_rating"]["down_votes"] = question["elo_rating"].get("down_votes", 0) + 1
                
                self._save_questions()
                
                # Kirjaa system_chainiin
                try:
                    from system_chain_manager import log_action
                    log_action(
                        "vote_processed",
                        f"Ääni käsitelty: {vote_type} kysymykselle {question_id}",
                        question_ids=[question_id],
                        user_id=user_id,
                        metadata={
                            "vote_type": vote_type,
                            "confidence": confidence,
                            "user_trust": user_trust,
                            "rating_change": result["change"]["change"],
                            "new_rating": result["change"]["new_rating"]
                        }
                    )
                except ImportError:
                    pass  # System chain ei saatavilla
            
            return result
            
        except ImportError as e:
            return {"success": False, "error": f"ELO-calculator not available: {e}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def handle_comparison(self, user_id: str, question_a_id: str, question_b_id: str, 
                         result: str, user_trust: str) -> Dict:
        """Käsittele kysymysvertailu ELO-järjestelmässä - UUSI METODI"""
        try:
            from complete_elo_calculator import CompleteELOCalculator, ComparisonResult, UserTrustLevel
            
            # Muunna enum-arvoiksi
            if result.lower() == "a_wins":
                comparison_result = ComparisonResult.A_WINS
            elif result.lower() == "b_wins":
                comparison_result = ComparisonResult.B_WINS
            else:
                comparison_result = ComparisonResult.TIE
            
            trust_enum = UserTrustLevel(user_trust)
            
            question_a = self.get_question_by_id(question_a_id)
            question_b = self.get_question_by_id(question_b_id)
            
            if not question_a or not question_b:
                return {"success": False, "error": "One or both questions not found"}
            
            calculator = CompleteELOCalculator()
            result_data = calculator.process_comparison(question_a, question_b, comparison_result, trust_enum)
            
            if result_data["success"]:
                # Päivitä kysymykset
                changes = result_data["changes"]
                
                # Päivitä kysymys A
                question_a["elo_rating"]["current_rating"] = changes["question_a"]["new_rating"]
                question_a["elo_rating"]["comparison_delta"] = changes["question_a"]["change"]
                question_a["elo_rating"]["total_comparisons"] = question_a["elo_rating"].get("total_comparisons", 0) + 1
                
                # Päivitä kysymys B
                question_b["elo_rating"]["current_rating"] = changes["question_b"]["new_rating"]
                question_b["elo_rating"]["comparison_delta"] = changes["question_b"]["change"]
                question_b["elo_rating"]["total_comparisons"] = question_b["elo_rating"].get("total_comparisons", 0) + 1
                
                self._save_questions()
                
                # Kirjaa system_chainiin
                try:
                    from system_chain_manager import log_action
                    log_action(
                        "comparison_processed",
                        f"Vertailu käsitelty: {question_a_id} vs {question_b_id} - {result}",
                        question_ids=[question_a_id, question_b_id],
                        user_id=user_id,
                        metadata={
                            "result": result,
                            "user_trust": user_trust,
                            "question_a_change": changes["question_a"]["change"],
                            "question_b_change": changes["question_b"]["change"],
                            "question_a_new_rating": changes["question_a"]["new_rating"],
                            "question_b_new_rating": changes["question_b"]["new_rating"]
                        }
                    )
                except ImportError:
                    pass  # System chain ei saatavilla
            
            return result_data
            
        except ImportError as e:
            return {"success": False, "error": f"ELO-calculator not available: {e}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_question_stats(self, question_id: str) -> Dict:
        """Hae kysymyksen tilastot - UUSI METODI"""
        question = self.get_question_by_id(question_id)
        if not question:
            return {"success": False, "error": "Question not found"}
        
        elo = question["elo_rating"]
        return {
            "success": True,
            "question_id": question_id,
            "current_rating": elo["current_rating"],
            "base_rating": elo["base_rating"],
            "comparison_delta": elo.get("comparison_delta", 0),
            "vote_delta": elo.get("vote_delta", 0),
            "total_comparisons": elo.get("total_comparisons", 0),
            "total_votes": elo.get("total_votes", 0),
            "up_votes": elo.get("up_votes", 0),
            "down_votes": elo.get("down_votes", 0),
            "content_preview": question["content"]["question"]["fi"][:50] + "..."
        }

    def recalculate_all_ratings(self) -> Dict:
        """Laske kaikkien kysymysten ratingit uudelleen - UUSI METODI"""
        try:
            from complete_elo_calculator import CompleteELOCalculator
            
            calculator = CompleteELOCalculator()
            recalculated_count = 0
            
            for question in self.questions:
                # Tässä voitaisiin tehdä monimutkaisempi uudelleenlaskenta
                # Nyt vain varmistetaan että rating on järkevissä rajoissa
                current_rating = question["elo_rating"]["current_rating"]
                base_rating = question["elo_rating"]["base_rating"]
                
                # Varmista että rating ei mene negatiiviseksi
                if current_rating < 0:
                    question["elo_rating"]["current_rating"] = max(0, current_rating)
                    recalculated_count += 1
                
                # Varmista että rating ei ole liian korkea
                if current_rating > 3000:
                    question["elo_rating"]["current_rating"] = min(3000, current_rating)
                    recalculated_count += 1
            
            if recalculated_count > 0:
                self._save_questions()
            
            return {
                "success": True,
                "recalculated_count": recalculated_count,
                "total_questions": len(self.questions),
                "message": f"Recalculated {recalculated_count} question ratings"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def export_ratings(self, output_file: str = "elo_ratings_export.json") -> Dict:
        """Vie ELO-luokitukset tiedostoon - UUSI METODI"""
        try:
            export_data = {
                "metadata": {
                    "exported_at": datetime.now(timezone.utc).isoformat(),
                    "total_questions": len(self.questions),
                    "system_version": "2.0.0"
                },
                "questions": []
            }
            
            for question in self.questions:
                export_data["questions"].append({
                    "local_id": question["local_id"],
                    "content_preview": question["content"]["question"]["fi"][:100],
                    "elo_rating": question["elo_rating"],
                    "timestamps": question["timestamps"]
                })
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return {
                "success": True,
                "export_file": output_file,
                "exported_questions": len(self.questions),
                "message": f"ELO ratings exported to {output_file}"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

# Testaus
if __name__ == "__main__":
    manager = ELOManager()
    questions = manager.load_questions()
    print(f"📊 Kysymyksiä ladattu: {len(questions)}")
    
    if questions:
        top_questions = manager.get_top_questions(3)
        print("🏆 TOP 3 KYSYMYSTÄ:")
        for i, q in enumerate(top_questions, 1):
            rating = q["elo_rating"]["current_rating"]
            print(f"{i}. {rating:.1f} - {q['content']['question']['fi'][:50]}...")
        
        # Testaa uusia metodeja
        if len(questions) >= 2:
            print("\n🧪 TESTATAAN UUSIA METODEJA:")
            
            # Testaa tilastot
            stats = manager.get_question_stats(questions[0]["local_id"])
            if stats["success"]:
                print(f"📈 Kysymyksen tilastot: {stats['current_rating']:.1f} rating")
            
            # Testaa vienti
            export_result = manager.export_ratings("test_export.json")
            if export_result["success"]:
                print(f"💾 Vienti: {export_result['message']}")
            
            # Testaa uudelleenlaskenta
            recalc_result = manager.recalculate_all_ratings()
            if recalc_result["success"]:
                print(f"🔄 Uudelleenlaskenta: {recalc_result['message']}")
    else:
        print("ℹ️  Ei kysymyksiä saatavilla testaamiseen")
