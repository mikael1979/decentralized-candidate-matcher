"""
Data-mallit kysymysten hallintaan.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
import uuid


@dataclass
class Question:
    """Yksittäinen kysymys."""
    id: str
    question_fi: str
    question_en: str
    category: str
    elo_rating: int
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def create_new(cls, question_fi: str, category: str = "Yleinen", 
                   question_en: Optional[str] = None, elo_rating: int = 1000) -> 'Question':
        """Luo uusi kysymys."""
        question_id = f"q_{uuid.uuid4().hex[:8]}"
        now = datetime.now()
        question_en_value = question_en or question_fi
        
        return cls(
            id=question_id,
            question_fi=question_fi,
            question_en=question_en_value,
            category=category,
            elo_rating=elo_rating,
            created_at=now,
            updated_at=now
        )


@dataclass
class QuestionCollection:
    """Kokoelma kysymyksiä."""
    questions: List[Question] = field(default_factory=list)
    
    def add_question(self, question: Question) -> None:
        """Lisää kysymys kokoelmaan."""
        self.questions.append(question)
    
    def remove_question(self, question_id: str) -> bool:
        """Poista kysymys ID:llä."""
        initial_count = len(self.questions)
        self.questions = [q for q in self.questions if q.id != question_id]
        return len(self.questions) < initial_count
    
    def find_question(self, identifier: str) -> Optional[Question]:
        """Etsi kysymys ID:llä tai tekstillä."""
        for question in self.questions:
            if question.id == identifier or question.question_fi == identifier:
                return question
        return None
    
    def get_category_stats(self) -> Dict[str, int]:
        """Hae kysymystilastot kategorioittain."""
        categories = {}
        for question in self.questions:
            categories[question.category] = categories.get(question.category, 0) + 1
        return categories
    
    def get_elo_stats(self) -> Dict[str, float]:
        """Hae ELO-tilastot."""
        if not self.questions:
            return {"average": 1000, "min": 1000, "max": 1000}
        
        elo_ratings = [q.elo_rating for q in self.questions]
        return {
            "average": round(sum(elo_ratings) / len(elo_ratings), 1),
            "min": min(elo_ratings),
            "max": max(elo_ratings)
        }
