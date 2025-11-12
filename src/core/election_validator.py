"""Vaalidien validointi ja tarkistus"""
from .error_handling import validate_election_exists, validate_answer_value, validate_confidence_level

class ElectionValidator:
    @staticmethod
    def validate_candidate_exists(candidate_id: str, data_manager):
        """Tarkista että ehdokas on olemassa"""
        candidates = data_manager.get_candidates()
        return any(c["candidate_id"] == candidate_id for c in candidates.get("candidates", []))
    
    @staticmethod
    def validate_question_exists(question_id: str, data_manager):
        """Tarkista että kysymys on olemassa"""
        questions = data_manager.get_questions()
        return any(q["local_id"] == question_id for q in questions.get("questions", []))

