"""
Data-mallit vastausten hallintaan.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid


@dataclass
class Answer:
    """Yksittäinen vastaus."""
    id: str
    candidate_id: str
    question_id: str
    value: int  # -5 - +5 asteikolla
    confidence: Optional[float] = None
    explanation_fi: Optional[str] = None
    explanation_en: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def create_new(cls, candidate_id: str, question_id: str, value: int, 
                   confidence: Optional[float] = None, 
                   explanation_fi: Optional[str] = None,
                   explanation_en: Optional[str] = None) -> 'Answer':
        """Luo uusi vastaus."""
        answer_id = f"ans_{uuid.uuid4().hex[:8]}"
        now = datetime.now()
        
        return cls(
            id=answer_id,
            candidate_id=candidate_id,
            question_id=question_id,
            value=value,
            confidence=confidence,
            explanation_fi=explanation_fi,
            explanation_en=explanation_en,
            created_at=now,
            updated_at=now
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Muunna dictiksi tallennusta varten."""
        return {
            "id": self.id,
            "candidate_id": self.candidate_id,
            "question_id": self.question_id,
            "value": self.value,
            "confidence": self.confidence,
            "explanation_fi": self.explanation_fi,
            "explanation_en": self.explanation_en,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Answer':
        """Luo Answer oliosta dictistä."""
        return cls(
            id=data["id"],
            candidate_id=data["candidate_id"],
            question_id=data["question_id"],
            value=data["value"],
            confidence=data.get("confidence"),
            explanation_fi=data.get("explanation_fi"),
            explanation_en=data.get("explanation_en"),
            created_at=datetime.fromisoformat(data["created_at"]) if isinstance(data["created_at"], str) else data["created_at"],
            updated_at=datetime.fromisoformat(data["updated_at"]) if isinstance(data["updated_at"], str) else data["updated_at"]
        )


@dataclass
class AnswerCollection:
    """Kokoelma vastauksia."""
    answers: List[Answer] = field(default_factory=list)
    
    def add_answer(self, answer: Answer) -> None:
        """Lisää vastaus kokoelmaan."""
        self.answers.append(answer)
    
    def remove_answer(self, candidate_id: str, question_id: str) -> bool:
        """Poista vastaus."""
        initial_count = len(self.answers)
        self.answers = [
            answer for answer in self.answers
            if not (answer.candidate_id == candidate_id and answer.question_id == question_id)
        ]
        return len(self.answers) < initial_count
    
    def update_answer(self, candidate_id: str, question_id: str, **kwargs) -> bool:
        """Päivitä vastaus."""
        for answer in self.answers:
            if answer.candidate_id == candidate_id and answer.question_id == question_id:
                for key, value in kwargs.items():
                    if hasattr(answer, key) and value is not None:
                        setattr(answer, key, value)
                answer.updated_at = datetime.now()
                return True
        return False
    
    def get_by_candidate(self, candidate_id: str) -> List[Answer]:
        """Hae kaikki ehdokkaan vastaukset."""
        return [answer for answer in self.answers if answer.candidate_id == candidate_id]
    
    def get_stats(self) -> Dict[str, Any]:
        """Hae tilastot."""
        candidates_with_answers = set(answer.candidate_id for answer in self.answers)
        
        return {
            "total_answers": len(self.answers),
            "candidates_with_answers": len(candidates_with_answers),
            "unique_questions": len(set(answer.question_id for answer in self.answers)),
            "average_value": round(sum(answer.value for answer in self.answers) / len(self.answers), 2) if self.answers else 0
        }
