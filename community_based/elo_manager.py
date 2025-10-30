#!/usr/bin/env python3
# elo_manager.py
"""
ELO Manager - Integroi ELO-laskenta koko vaalikonejärjestelmään
Käyttö:
  from elo_manager import ELOManager
  manager = ELOManager()
  result = manager.handle_comparison(user_id, q1_id, q2_id, result, trust_level)
"""

import json
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

# System chain integraatio
try:
    from system_chain_manager import log_action
    SYSTEM_CHAIN_AVAILABLE = True
except ImportError:
    SYSTEM_CHAIN_AVAILABLE = False
    print("⚠️  System chain manager ei saatavilla - toiminnot eivät kirjaudu ketjuun")

# ELO-laskenta moduuli
try:
    from complete_elo_calculator import CompleteELOCalculator, ComparisonResult, VoteType, UserTrustLevel
    ELO_CALCULATOR_AVAILABLE = True
except ImportError as e:
    ELO_CALCULATOR_AVAILABLE = False
    print(f"⚠️  ELO-calculator ei saatavilla: {e}")

# Integriteettivalvonta
try:
    from integrity_manager import verify_system_integrity
    INTEGRITY_CHECK_AVAILABLE = True
except ImportError:
    INTEGRITY_CHECK_AVAILABLE = False
    print("⚠️  Integrity manager ei saatavilla - skipataan integriteettitarkistus")

class ELOManager:
    """
    Integroi ELO-laskenta koko vaalikonejärjestelmään
    Hallitsee kysymysten vertailuja, äänestyksiä ja rating-päivityksiä
    """
    
    def __init__(self, questions_file: str = "runtime/questions.json", 
                 runtime_dir: str = "runtime"):
        self.questions_file = Path(questions_file)
        self.runtime_dir = Path(runtime_dir)
        self.runtime_dir.mkdir(exist_ok=True)
        
        # Tarkista integriteetti
        if INTEGRITY_CHECK_AVAILABLE:
            if not verify_system_integrity():
                raise SecurityError("Järjestelmän integriteettitarkistus epäonnistui")
        
        # Alusta ELO-laskenta
        if ELO_CALCULATOR_AVAILABLE:
            self.elo_calculator = CompleteELOCalculator()
        else:
            self.elo_calculator = None
            print("❌ ELO-calculator puuttuu - rajoitettu toiminnallisuus")
    
    def handle_comparison(self, user_id: str, question_a_id: str, 
                        question_b_id: str, result: ComparisonResult,
                        user_trust: UserTrustLevel) -> Dict[str, Any]:
        """
        Käsittele käyttäjän tekemä vertailu kahden kysymyksen välillä
        
        Args:
            user_id: Käyttäjän yksilöllinen ID
            question_a_id: Ensimmäisen kysymyksen ID
            question_b_id: Toisen kysymyksen ID  
            result: Vertailun tulos (A_WINS, B_WINS, TIE)
            user_trust: Käyttäjän luottamustaso
            
        Returns:
            Dictionary joka sisältää onnistumistiedon ja rating-muutokset
        """
        # Tarkista ELO-calculatorin saatavuus
        if not ELO_CALCULATOR_AVAILABLE:
            return {
                "success": False, 
                "error": "ELO-calculator ei saatavilla",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # Lataa kysymykset
        questions_data = self._load_questions()
        question_a = self._find_question(questions_data, question_a_id)
        question_b = self._find_question(questions_data, question_b_id)
        
        if not question_a or not question_b:
            return {
                "success": False, 
                "error": "Questions not found",
                "details": {
                    "question_a_found": bool(question_a),
                    "question_b_found": bool(question_b)
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # Suorita ELO-laskenta
        try:
            elo_result = self.elo_calculator.process_comparison(
                question_a, question_b, result, user_trust
            )
        except Exception as e:
            return {
                "success": False,
                "error": f"ELO calculation failed: {e}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        if not elo_result["success"]:
            return {
                "success": False,
                "error": elo_result.get("error", "Unknown ELO error"),
                "details": elo_result.get("details", {}),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # Päivitä kysymysten ratingit
        self._update_question_rating(question_a_id, elo_result["changes"]["question_a"])
        self._update_question_rating(question_b_id, elo_result["changes"]["question_b"])
        
        # Tarkista automaattiset estoehdot
        block_check_a = self.elo_calculator.check_auto_block_conditions(question_a)
        block_check_b = self.elo_calculator.check_auto_block_conditions(question_b)
        
        # Tallenna muutokset
        self._save_questions(questions_data)
        
        # Kirjaa system_chainiin
        if SYSTEM_CHAIN_AVAILABLE:
            changes = elo_result["changes"]
            description = f"Vertailu: {changes['question_a']['change']:+.1f}/{changes['question_b']['change']:+.1f}"
            
            log_action(
                action_type="comparison",
                description=description,
                question_ids=[question_a_id, question_b_id],
                user_id=user_id,
                metadata={
                    "result": result.value,
                    "user_trust": user_trust.value,
                    "rating_changes": {
                        "question_a": changes["question_a"]["change"],
                        "question_b": changes["question_b"]["change"]
                    },
                    "old_ratings": {
                        "question_a": changes["question_a"]["old_rating"],
                        "question_b": changes["question_b"]["old_rating"]
                    },
                    "new_ratings": {
                        "question_a": changes["question_a"]["new_rating"],
                        "question_b": changes["question_b"]["new_rating"]
                    },
                    "block_checks": {
                        "question_a": block_check_a,
                        "question_b": block_check_b
                    }
                }
            )
        
        return {
            "success": True,
            "rating_changes": elo_result["changes"],
            "block_checks": {
                "question_a": block_check_a,
                "question_b": block_check_b
            },
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": {
                "question_a_text": question_a["content"]["question"]["fi"][:50] + "...",
                "question_b_text": question_b["content"]["question"]["fi"][:50] + "...",
                "result": result.value
            }
        }
    
    def handle_vote(self, user_id: str, question_id: str, vote_type: VoteType,
                  confidence: int, user_trust: UserTrustLevel) -> Dict[str, Any]:
        """
        Käsittele käyttäjän antama ääni (upvote/downvote)
        
        Args:
            user_id: Käyttäjän yksilöllinen ID
            question_id: Kysymyksen ID
            vote_type: Äänen tyyppi (UPVOTE/DOWNVOTE)
            confidence: Luottamustaso (1-5)
            user_trust: Käyttäjän luottamustaso
            
        Returns:
            Dictionary joka sisältää onnistumistiedon ja rating-muutokset
        """
        if not ELO_CALCULATOR_AVAILABLE:
            return {
                "success": False,
                "error": "ELO-calculator ei saatavilla",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # Lataa kysymys
        questions_data = self._load_questions()
        question = self._find_question(questions_data, question_id)
        
        if not question:
            return {
                "success": False, 
                "error": "Question not found",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # Suorita äänestyslaskenta
        try:
            vote_result = self.elo_calculator.process_vote(
                question, vote_type, confidence, user_trust
            )
        except Exception as e:
            return {
                "success": False,
                "error": f"Vote calculation failed: {e}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        if not vote_result["success"]:
            return {
                "success": False,
                "error": vote_result.get("error", "Unknown vote error"),
                "details": vote_result.get("details", {}),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # Päivitä kysymyksen rating
        self._update_question_rating(question_id, vote_result["change"])
        
        # Tarkista automaattiset estoehdot
        block_check = self.elo_calculator.check_auto_block_conditions(question)
        
        # Tallenna muutokset
        self._save_questions(questions_data)
        
        # Kirjaa system_chainiin
        if SYSTEM_CHAIN_AVAILABLE:
            change = vote_result["change"]
            vote_type_text = "upvote" if vote_type == VoteType.UPVOTE else "downvote"
            description = f"Äänestys: {change['change']:+.1f} ({vote_type_text}, conf: {confidence})"
            
            log_action(
                action_type="vote",
                description=description,
                question_ids=[question_id],
                user_id=user_id,
                metadata={
                    "vote_type": vote_type.value,
                    "vote_type_text": vote_type_text,
                    "confidence": confidence,
                    "user_trust": user_trust.value,
                    "rating_change": change["change"],
                    "old_rating": change["old_rating"],
                    "new_rating": change["new_rating"],
                    "block_check": block_check
                }
            )
        
        return {
            "success": True,
            "vote_result": vote_result,
            "block_check": block_check,
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": {
                "question_text": question["content"]["question"]["fi"][:50] + "...",
                "vote_type": vote_type.value,
                "confidence": confidence
            }
        }
    
    def add_question(self, user_id: str, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Lisää uusi kysymys järjestelmään
        
        Args:
            user_id: Käyttäjän yksilöllinen ID
            question_data: Kysymyksen tiedot
            
        Returns:
            Dictionary joka sisältää onnistumistiedon ja kysymyksen ID:n
        """
        # Tarkista että kysymyksellä on kaikki tarvittavat kentät
        required_fields = ["local_id", "content", "elo_rating", "timestamps"]
        missing_fields = [field for field in required_fields if field not in question_data]
        
        if missing_fields:
            return {
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # Lataa nykyiset kysymykset
        questions_data = self._load_questions()
        
        # Tarkista että kysymys-ID on uniikki
        existing_ids = [q['local_id'] for q in questions_data.get('questions', [])]
        if question_data['local_id'] in existing_ids:
            return {
                "success": False,
                "error": f"Question ID '{question_data['local_id']}' already exists",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # Lisää kysymys
        questions_data.setdefault("questions", []).append(question_data)
        
        # Tallenna
        self._save_questions(questions_data)
        
        # Kirjaa system_chainiin
        if SYSTEM_CHAIN_AVAILABLE:
            log_action(
                action_type="question_add",
                description=f"Uusi kysymys: {question_data['content']['question']['fi'][:50]}...",
                question_ids=[question_data["local_id"]],
                user_id=user_id,
                metadata={
                    "question_id": question_data["local_id"],
                    "category": question_data["content"].get("category", {}).get("fi", "unknown"),
                    "initial_rating": question_data["elo_rating"]["current_rating"],
                    "tags": question_data["content"].get("tags", [])
                }
            )
        
        return {
            "success": True,
            "question_id": question_data["local_id"],
            "message": "Question added successfully",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def get_question_stats(self, question_id: str) -> Optional[Dict[str, Any]]:
        """
        Hae kysymyksen tilastot
        
        Args:
            question_id: Kysymyksen ID
            
        Returns:
            Kysymyksen tilastot tai None jos ei löydy
        """
        questions_data = self._load_questions()
        question = self._find_question(questions_data, question_id)
        
        if not question:
            return None
        
        elo = question["elo_rating"]
        return {
            "question_id": question_id,
            "current_rating": elo["current_rating"],
            "total_comparisons": elo.get("total_comparisons", 0),
            "total_votes": elo.get("total_votes", 0),
            "up_votes": elo.get("up_votes", 0),
            "down_votes": elo.get("down_votes", 0),
            "comparison_delta": elo.get("comparison_delta", 0),
            "vote_delta": elo.get("vote_delta", 0),
            "question_text": question["content"]["question"]["fi"],
            "category": question["content"].get("category", {}).get("fi", "unknown")
        }
    
    def get_top_questions(self, limit: int = 10, min_comparisons: int = 0) -> Dict[str, Any]:
        """
        Hae parhaiten sijoitetut kysymykset
        
        Args:
            limit: Palautettavien kysymysten määrä
            min_comparisons: Vähimmäismäärä vertailuja
            
        Returns:
            Lista parhaista kysymyksistä
        """
        questions_data = self._load_questions()
        
        # Suodata kysymykset
        filtered_questions = [
            q for q in questions_data.get("questions", [])
            if q["elo_rating"].get("total_comparisons", 0) >= min_comparisons
        ]
        
        # Lajittele ratingin mukaan
        sorted_questions = sorted(
            filtered_questions,
            key=lambda x: x["elo_rating"]["current_rating"],
            reverse=True
        )[:limit]
        
        return {
            "success": True,
            "top_questions": [
                {
                    "question_id": q["local_id"],
                    "rating": q["elo_rating"]["current_rating"],
                    "comparisons": q["elo_rating"].get("total_comparisons", 0),
                    "votes": q["elo_rating"].get("total_votes", 0),
                    "up_votes": q["elo_rating"].get("up_votes", 0),
                    "down_votes": q["elo_rating"].get("down_votes", 0),
                    "question": q["content"]["question"]["fi"][:100] + "..." if len(q["content"]["question"]["fi"]) > 100 else q["content"]["question"]["fi"],
                    "category": q["content"].get("category", {}).get("fi", "unknown")
                }
                for q in sorted_questions
            ],
            "total_questions": len(questions_data.get("questions", [])),
            "filtered_questions": len(filtered_questions),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def get_question_history(self, question_id: str, limit: int = 20) -> Optional[Dict[str, Any]]:
        """
        Hae kysymyksen muutoshistoria
        
        Args:
            question_id: Kysymyksen ID
            limit: Historiatapahtumien määrä
            
        Returns:
            Kysymyksen historia tai None jos ei löydy
        """
        # Tämä voisi yhdistää system_chain dataan tulevaisuudessa
        questions_data = self._load_questions()
        question = self._find_question(questions_data, question_id)
        
        if not question:
            return None
        
        return {
            "question_id": question_id,
            "current_rating": question["elo_rating"]["current_rating"],
            "created": question["timestamps"]["created_local"],
            "modified": question["timestamps"]["modified_local"],
            "total_comparisons": question["elo_rating"].get("total_comparisons", 0),
            "total_votes": question["elo_rating"].get("total_votes", 0),
            "stats": {
                "comparison_delta": question["elo_rating"].get("comparison_delta", 0),
                "vote_delta": question["elo_rating"].get("vote_delta", 0),
                "up_votes": question["elo_rating"].get("up_votes", 0),
                "down_votes": question["elo_rating"].get("down_votes", 0)
            }
        }
    
    def _load_questions(self) -> Dict[str, Any]:
        """Lataa kysymystiedosto"""
        try:
            with open(self.questions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Luo uusi tyhjä kysymystiedosto
            default_structure = {
                "metadata": {
                    "created": datetime.now(timezone.utc).isoformat(),
                    "version": "1.0.0",
                    "total_questions": 0
                },
                "questions": []
            }
            self._save_questions(default_structure)
            return default_structure
        except json.JSONDecodeError as e:
            print(f"❌ Virhe ladattaessa questions.json: {e}")
            return {"questions": []}
    
    def _save_questions(self, questions_data: Dict[str, Any]):
        """Tallenna kysymystiedosto"""
        try:
            # Päivitä metadata
            questions_data["metadata"] = questions_data.get("metadata", {})
            questions_data["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()
            questions_data["metadata"]["total_questions"] = len(questions_data.get("questions", []))
            
            with open(self.questions_file, 'w', encoding='utf-8') as f:
                json.dump(questions_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Virhe tallennettaessa questions.json: {e}")
            raise
    
    def _find_question(self, questions_data: Dict[str, Any], question_id: str) -> Optional[Dict[str, Any]]:
        """Etsi kysymys ID:llä"""
        for question in questions_data.get("questions", []):
            if question["local_id"] == question_id:
                return question
        return None
    
    def _update_question_rating(self, question_id: str, change_data: Dict[str, Any]):
        """Päivitä kysymyksen ELO-rating"""
        questions_data = self._load_questions()
        
        for question in questions_data.get("questions", []):
            if question["local_id"] == question_id:
                # Päivitä rating
                question["elo_rating"]["current_rating"] = change_data["new_rating"]
                
                # Päivitä deltat ja tilastot
                if "expected_score" in change_data:  # Vertailu
                    question["elo_rating"]["comparison_delta"] = question["elo_rating"].get("comparison_delta", 0) + change_data["change"]
                    question["elo_rating"]["total_comparisons"] = question["elo_rating"].get("total_comparisons", 0) + 1
                else:  # Äänestys
                    question["elo_rating"]["vote_delta"] = question["elo_rating"].get("vote_delta", 0) + change_data["change"]
                    question["elo_rating"]["total_votes"] = question["elo_rating"].get("total_votes", 0) + 1
                    
                    if change_data["vote_type"] == "upvote":
                        question["elo_rating"]["up_votes"] = question["elo_rating"].get("up_votes", 0) + 1
                    else:
                        question["elo_rating"]["down_votes"] = question["elo_rating"].get("down_votes", 0) + 1
                
                # Päivitä aikaleima
                question["timestamps"]["modified_local"] = datetime.now(timezone.utc).isoformat()
                break
        
        self._save_questions(questions_data)

class SecurityError(Exception):
    """Turvallisuuspoikkeus integriteettitarkistuksen epäonnistuessa"""
    pass

# Demo ja testaus
if __name__ == "__main__":
    print("🧪 ELO_MANAGER TESTI")
    print("=" * 50)
    
    try:
        # Testaa managerin alustus
        manager = ELOManager("runtime/questions.json")
        print("✅ ELO Manager alustettu")
        
        # Testaa kysymysten lataus
        stats = manager.get_top_questions(3)
        if stats["success"]:
            print("✅ Kysymykset ladattu")
            for i, q in enumerate(stats["top_questions"]):
                print(f"   {i+1}. {q['rating']:.1f} pts - {q['question']}")
        else:
            print("❌ Kysymysten lataus epäonnistui")
        
        # Tarkista moduulien saatavuus
        print(f"\n📦 MODUULITILA:")
        print(f"   ELO-calculator: {'✅' if ELO_CALCULATOR_AVAILABLE else '❌'}")
        print(f"   System chain: {'✅' if SYSTEM_CHAIN_AVAILABLE else '❌'}")
        print(f"   Integrity check: {'✅' if INTEGRITY_CHECK_AVAILABLE else '❌'}")
        
        print("\n🎯 KÄYTTÖESIMERKKEJÄ:")
        print("""
# 1. Vertailun käsittely
from complete_elo_calculator import ComparisonResult, UserTrustLevel

result = manager.handle_comparison(
    user_id="user123",
    question_a_id="q1",
    question_b_id="q2", 
    result=ComparisonResult.A_WINS,
    user_trust=UserTrustLevel.REGULAR_USER
)

# 2. Äänestyksen käsittely
result = manager.handle_vote(
    user_id="user456",
    question_id="q1",
    vote_type=VoteType.UPVOTE,
    confidence=4,
    user_trust=UserTrustLevel.TRUSTED_USER
)

# 3. Top kysymykset
top = manager.get_top_questions(limit=10, min_comparisons=5)

# 4. Kysymyksen tilastot
stats = manager.get_question_stats("q1")
        """)
        
    except Exception as e:
        print(f"❌ TESTI EPÄONNISTUI: {e}")
        import traceback
        traceback.print_exc()
