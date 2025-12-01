"""
Päämanageri vastausten CRUD-toiminnoille.
"""
import sys
from pathlib import Path
from typing import Tuple, Optional, List, Dict, Any
import click

# Lisää src hakemisto Python-polkuun
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from core import get_election_id, get_data_path
from core.file_utils import read_json_file, write_json_file, ensure_directory

from ..models import Answer, AnswerCollection
from .base_manager import BaseAnswerManager


class AnswerManager(BaseAnswerManager):
    """Päämanageri vastausten hallinnalle."""
    
    def __init__(self, election_id: str = None):
        super().__init__(election_id)
    
    def add_answer(self, candidate_id: str, question_id: str, value: int, 
                   confidence: Optional[float] = None,
                   explanation_fi: Optional[str] = None,
                   explanation_en: Optional[str] = None) -> Tuple[bool, Any]:
        """Lisää uusi vastaus."""
        answers_data = self.load_answers()
        
        # Tarkista onko vastaus jo olemassa
        for answer_dict in answers_data["answers"]:
            if (answer_dict.get("candidate_id") == candidate_id and 
                answer_dict.get("question_id") == question_id):
                return False, "Ehdokkaalla on jo vastaus kysymykseen"
        
        # Luo uusi vastaus
        new_answer = Answer.create_new(
            candidate_id=candidate_id,
            question_id=question_id,
            value=value,
            confidence=confidence,
            explanation_fi=explanation_fi,
            explanation_en=explanation_en
        )
        
        # Lisää vastaus dataan
        answers_data["answers"].append(new_answer.to_dict())
        self.save_answers(answers_data)
        
        return True, new_answer.to_dict()
    
    def remove_answer(self, candidate_id: str, question_id: str) -> Tuple[bool, str]:
        """Poista vastaus."""
        answers_data = self.load_answers()
        
        initial_count = len(answers_data["answers"])
        answers_data["answers"] = [
            answer for answer in answers_data["answers"]
            if not (answer.get("candidate_id") == candidate_id and 
                   answer.get("question_id") == question_id)
        ]
        
        removed_count = initial_count - len(answers_data["answers"])
        if removed_count > 0:
            self.save_answers(answers_data)
            return True, f"Poistettu {removed_count} vastaus"
        else:
            return False, "Vastausta ei löytynyt"
    
    def update_answer(self, candidate_id: str, question_id: str, 
                      value: Optional[int] = None, 
                      confidence: Optional[float] = None, 
                      explanation_fi: Optional[str] = None,
                      explanation_en: Optional[str] = None) -> Tuple[bool, str]:
        """Päivitä olemassa oleva vastaus."""
        answers_data = self.load_answers()
        updated = False
        
        for answer in answers_data["answers"]:
            if (answer.get("candidate_id") == candidate_id and 
                answer.get("question_id") == question_id):
                
                if value is not None:
                    answer["value"] = value
                    updated = True
                if confidence is not None:
                    answer["confidence"] = confidence
                    updated = True
                if explanation_fi is not None:
                    answer["explanation_fi"] = explanation_fi
                    updated = True
                if explanation_en is not None:
                    answer["explanation_en"] = explanation_en
                    updated = True
                
                if updated:
                    answer["updated_at"] = datetime.now().isoformat()
        
        if updated:
            self.save_answers(answers_data)
            return True, "Vastaus päivitetty"
        else:
            return False, "Vastausta ei löytynyt tai ei muutoksia"
    
    def list_answers(self, candidate_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Listaa vastaukset."""
        answers_data = self.load_answers()
        
        if candidate_id:
            answers = [a for a in answers_data["answers"] if a.get("candidate_id") == candidate_id]
        else:
            answers = answers_data["answers"]
        
        return answers
    
    def get_answer_stats(self) -> Dict[str, Any]:
        """Hae vastaustilastot."""
        answers_data = self.load_answers()
        answers = answers_data["answers"]
        
        # Ehdokkaat joilla on vastauksia
        candidates_with_answers = set(a["candidate_id"] for a in answers)
        
        # Lataa ehdokkaat yhteensä
        candidates_file = Path(self.data_path) / "candidates.json"
        total_candidates = 0
        if candidates_file.exists():
            candidates_data = read_json_file(candidates_file)
            total_candidates = len(candidates_data.get("candidates", []))
        
        return {
            "total_answers": len(answers),
            "candidates_with_answers": len(candidates_with_answers),
            "total_candidates": total_candidates,
            "answer_coverage": round((len(candidates_with_answers) / total_candidates * 100) if total_candidates > 0 else 0, 1)
        }
