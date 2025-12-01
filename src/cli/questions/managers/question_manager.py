"""
Päämanageri kysymysten CRUD-toiminnoille.
"""
from datetime import datetime
from typing import Tuple, Optional, List, Dict, Any

from ..models import Question, QuestionCollection
from .base_manager import BaseQuestionManager


class QuestionManager(BaseQuestionManager):
    """Päämanageri kysymysten hallinnalle."""
    
    def add_question(self, question_fi: str, category: str = "Yleinen", 
                     question_en: Optional[str] = None, elo_rating: int = 1000) -> Tuple[bool, Any]:
        """Lisää uusi kysymys."""
        questions_data = self.load_questions()
        
        # Tarkista onko kysymys jo olemassa
        for question in questions_data["questions"]:
            if question.get("question_fi") == question_fi:
                return False, "Kysymys samalla tekstillä on jo olemassa"
        
        # Luo uusi kysymys
        new_question = Question.create_new(
            question_fi=question_fi,
            category=category,
            question_en=question_en,
            elo_rating=elo_rating
        )
        
        # Muunna dataclass dictiksi tallennusta varten
        question_dict = {
            "id": new_question.id,
            "question_fi": new_question.question_fi,
            "question_en": new_question.question_en,
            "category": new_question.category,
            "elo_rating": new_question.elo_rating,
            "created_at": new_question.created_at.isoformat(),
            "updated_at": new_question.updated_at.isoformat()
        }
        
        questions_data["questions"].append(question_dict)
        self.save_questions(questions_data)
        
        return True, question_dict
    
    def remove_question(self, question_identifier: str) -> Tuple[bool, str]:
        """Poista kysymys."""
        questions_data = self.load_questions()
        
        # Etsi kysymys
        question_to_remove = None
        for question in questions_data["questions"]:
            if (question["id"] == question_identifier or 
                question["question_fi"] == question_identifier):
                question_to_remove = question
                break
        
        if not question_to_remove:
            return False, "Kysymystä ei löydy"
        
        # Poista kysymys
        initial_count = len(questions_data["questions"])
        questions_data["questions"] = [
            question for question in questions_data["questions"]
            if question["id"] != question_to_remove["id"]
        ]
        
        removed_count = initial_count - len(questions_data["questions"])
        if removed_count > 0:
            self.save_questions(questions_data)
            return True, f"Poistettu kysymys: {question_to_remove['question_fi']}"
        else:
            return False, "Kysymystä ei löytynyt"
    
    def update_question(self, question_identifier: str, 
                        question_fi: Optional[str] = None,
                        question_en: Optional[str] = None,
                        category: Optional[str] = None,
                        elo_rating: Optional[int] = None) -> Tuple[bool, str]:
        """Päivitä kysymys."""
        questions_data = self.load_questions()
        
        # Etsi kysymys
        question_to_update = None
        question_index = -1
        
        for i, question in enumerate(questions_data["questions"]):
            if (question["id"] == question_identifier or 
                question["question_fi"] == question_identifier):
                question_to_update = question
                question_index = i
                break
        
        if not question_to_update:
            return False, "Kysymystä ei löydy"
        
        # Päivitä kentät
        updated = False
        
        if question_fi is not None:
            questions_data["questions"][question_index]["question_fi"] = question_fi
            updated = True
        
        if question_en is not None:
            questions_data["questions"][question_index]["question_en"] = question_en
            updated = True
        
        if category is not None:
            questions_data["questions"][question_index]["category"] = category
            updated = True
        
        if elo_rating is not None:
            questions_data["questions"][question_index]["elo_rating"] = elo_rating
            updated = True
        
        if updated:
            questions_data["questions"][question_index]["updated_at"] = datetime.now().isoformat()
            self.save_questions(questions_data)
            return True, f"Kysymys päivitetty: {question_to_update['question_fi']}"
        else:
            return False, "Ei muutoksia"
    
    def list_questions(self, category_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Listaa kysymykset."""
        questions_data = self.load_questions()
        questions = questions_data.get("questions", [])
        
        if category_filter:
            questions = [q for q in questions if q["category"] == category_filter]
        
        return questions
    
    def get_question_stats(self) -> Dict[str, Any]:
        """Hae kysymystilastot."""
        questions_data = self.load_questions()
        questions = questions_data.get("questions", [])
        
        # Luo QuestionCollection tilastoja varten
        question_objs = []
        for q in questions:
            question_objs.append(Question(
                id=q["id"],
                question_fi=q["question_fi"],
                question_en=q["question_en"],
                category=q["category"],
                elo_rating=q["elo_rating"],
                created_at=datetime.fromisoformat(q["created_at"]),
                updated_at=datetime.fromisoformat(q["updated_at"])
            ))
        
        collection = QuestionCollection(questions=question_objs)
        
        stats = {
            "total_questions": len(questions),
            "categories": collection.get_category_stats(),
            "average_elo": collection.get_elo_stats()["average"],
            "min_elo": collection.get_elo_stats()["min"],
            "max_elo": collection.get_elo_stats()["max"]
        }
        
        return stats
