# elo_manager.py
from datetime import datetime
import json
from typing import Dict, Optional
from complete_elo_calculator import ComparisonResult, VoteType, UserTrustLevel

# System chain integraatio
try:
    from system_chain_manager import log_action
    SYSTEM_CHAIN_AVAILABLE = True
except ImportError:
    SYSTEM_CHAIN_AVAILABLE = False
    print("⚠️  System chain manager ei saatavilla - toiminnot eivät kirjaudu ketjuun")

class ELOManager:
    """Integroi ELO-laskenta koko vaalikonejärjestelmään"""
    
    def __init__(self, questions_file: str = "questions.json"):
        self.questions_file = questions_file
        from complete_elo_calculator import CompleteELOCalculator  # Lazy import välttääkseen circular dependency
        self.elo_calculator = CompleteELOCalculator()
    
    def handle_comparison(self, user_id: str, question_a_id: str, 
                        question_b_id: str, result: ComparisonResult,
                        user_trust: UserTrustLevel) -> Dict:
        """Käsittele käyttäjän tekemä vertailu"""
        # Lataa kysymykset
        questions_data = self._load_questions()
        question_a = self._find_question(questions_data, question_a_id)
        question_b = self._find_question(questions_data, question_b_id)
        
        if not question_a or not question_b:
            return {"success": False, "error": "Questions not found"}
        
        # Suorita ELO-laskenta
        elo_result = self.elo_calculator.process_comparison(
            question_a, question_b, result, user_trust
        )
        
        if not elo_result["success"]:
            return elo_result
        
        # Päivitä kysymysten ratingit
        self._update_question_rating(question_a_id, elo_result["changes"]["question_a"])
        self._update_question_rating(question_b_id, elo_result["changes"]["question_b"])
        
        # Tarkista estoehdot
        block_check_a = self.elo_calculator.check_auto_block_conditions(question_a)
        block_check_b = self.elo_calculator.check_auto_block_conditions(question_b)
        
        # Tallenna muutokset
        self._save_questions(questions_data)
        
        # Kirjaa system_chainiin
        if elo_result["success"] and SYSTEM_CHAIN_AVAILABLE:
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
            "timestamp": datetime.now().isoformat()
        }
    
    def handle_vote(self, user_id: str, question_id: str, vote_type: VoteType,
                  confidence: int, user_trust: UserTrustLevel) -> Dict:
        """Käsittele käyttäjän antama ääni"""
        # Lataa kysymys
        questions_data = self._load_questions()
        question = self._find_question(questions_data, question_id)
        
        if not question:
            return {"success": False, "error": "Question not found"}
        
        # Suorita äänestyslaskenta
        vote_result = self.elo_calculator.process_vote(
            question, vote_type, confidence, user_trust
        )
        
        if not vote_result["success"]:
            return vote_result
        
        # Päivitä kysymyksen rating
        self._update_question_rating(question_id, vote_result["change"])
        
        # Tarkista estoehdot
        block_check = self.elo_calculator.check_auto_block_conditions(question)
        
        # Tallenna muutokset
        self._save_questions(questions_data)
        
        # Kirjaa system_chainiin
        if vote_result["success"] and SYSTEM_CHAIN_AVAILABLE:
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
                    "new_rating": change["new_rating"]
                }
            )
        
        return {
            "success": True,
            "vote_result": vote_result,
            "block_check": block_check,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
    
    def add_question(self, user_id: str, question_data: Dict) -> Dict:
        """Lisää uusi kysymys järjestelmään"""
        questions_data = self._load_questions()
        
        # Varmista että kysymyksellä on kaikki tarvittavat kentät
        required_fields = ["local_id", "content", "elo_rating", "timestamps"]
        for field in required_fields:
            if field not in question_data:
                return {"success": False, "error": f"Missing required field: {field}"}
        
        # Lisää kysymys
        questions_data["questions"].append(question_data)
        
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
                    "initial_rating": question_data["elo_rating"]["current_rating"]
                }
            )
        
        return {
            "success": True,
            "question_id": question_data["local_id"],
            "message": "Question added successfully",
            "timestamp": datetime.now().isoformat()
        }
    
    def get_question_stats(self, question_id: str) -> Optional[Dict]:
        """Hae kysymyksen tilastot"""
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
            "vote_delta": elo.get("vote_delta", 0)
        }
    
    def get_top_questions(self, limit: int = 10) -> Dict:
        """Hae parhaiten sijoitetut kysymykset"""
        questions_data = self._load_questions()
        
        # Lajittele ratingin mukaan
        sorted_questions = sorted(
            questions_data["questions"],
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
                    "question": q["content"]["question"]["fi"][:100] + "..." if len(q["content"]["question"]["fi"]) > 100 else q["content"]["question"]["fi"]
                }
                for q in sorted_questions
            ],
            "timestamp": datetime.now().isoformat()
        }
    
    def _load_questions(self) -> Dict:
        """Lataa kysymystiedosto"""
        try:
            with open(self.questions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"questions": []}
    
    def _save_questions(self, questions_data: Dict):
        """Tallenna kysymystiedosto"""
        with open(self.questions_file, 'w', encoding='utf-8') as f:
            json.dump(questions_data, f, indent=2, ensure_ascii=False)
    
    def _find_question(self, questions_data: Dict, question_id: str) -> Optional[Dict]:
        """Etsi kysymys ID:llä"""
        for question in questions_data.get("questions", []):
            if question["local_id"] == question_id:
                return question
        return None
    
    def _update_question_rating(self, question_id: str, change_data: Dict):
        """Päivitä kysymyksen ELO-rating"""
        questions_data = self._load_questions()
        
        for question in questions_data.get("questions", []):
            if question["local_id"] == question_id:
                # Päivitä rating
                question["elo_rating"]["current_rating"] = change_data["new_rating"]
                
                # Päivitä deltat
                if "expected_score" in change_data:  # Vertailu
                    question["elo_rating"]["comparison_delta"] += change_data["change"]
                    question["elo_rating"]["total_comparisons"] = question["elo_rating"].get("total_comparisons", 0) + 1
                else:  # Äänestys
                    question["elo_rating"]["vote_delta"] += change_data["change"]
                    question["elo_rating"]["total_votes"] = question["elo_rating"].get("total_votes", 0) + 1
                    
                    if change_data["vote_type"] == "upvote":
                        question["elo_rating"]["up_votes"] = question["elo_rating"].get("up_votes", 0) + 1
                    else:
                        question["elo_rating"]["down_votes"] = question["elo_rating"].get("down_votes", 0) + 1
                
                # Päivitä aikaleima
                question["timestamps"]["modified_local"] = datetime.now().isoformat()
                break
        
        self._save_questions(questions_data)

# Demo ja testaus
if __name__ == "__main__":
    print("🧪 ELO_MANAGER TESTI")
    print("=" * 40)
    
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
    
    # Tarkista system chain tila
    if SYSTEM_CHAIN_AVAILABLE:
        print("✅ System chain integraatio käytössä")
    else:
        print("⚠️  System chain ei saatavilla")
    
    print("\n🎯 KÄYTTÖESIMERKKEJÄ:")
    print("""
# 1. Vertailun käsittely
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
top = manager.get_top_questions(10)
    """)
