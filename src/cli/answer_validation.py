#!/usr/bin/env python3
"""
Vastausten validointi ja tarkistus - UUSI MODULAARINEN
"""
import json
from typing import Dict, List, Tuple

# KORJATTU: Käytetään yhteisiä file_utils-funktioita
try:
    from src.core.file_utils import read_json_file
    from src.core.validators import DataValidator
except ImportError:
    from core.file_utils import read_json_file
    from core.validators import DataValidator

class AnswerValidation:
    """Vastausten validointi ja tarkistus"""
    
    def __init__(self, election_id: str):
        self.election_id = election_id
        self.candidates_file = f"data/runtime/candidates.json"
        self.questions_file = f"data/runtime/questions.json"
    
    def validate_all_answers(self) -> Dict:
        """Validoi kaikki vastaukset"""
        
        try:
            candidates_data = read_json_file(self.candidates_file, {"candidates": []})
            questions_data = read_json_file(self.questions_file, {"questions": []})
        except Exception as e:
            return {
                "status": "error",
                "message": f"Data-tiedostojen lukuvirhe: {e}",
                "valid_answers": 0,
                "invalid_answers": 0,
                "issues": []
            }
        
        valid_answers = 0
        invalid_answers = 0
        issues = []
        
        # Hae kysymysten ID:t
        valid_question_ids = {q["local_id"] for q in questions_data.get("questions", [])}
        
        for candidate in candidates_data.get("candidates", []):
            candidate_id = candidate["candidate_id"]
            
            if "answers" not in candidate:
                continue
                
            for answer in candidate["answers"]:
                # Tarkista kysymys ID
                if answer["question_id"] not in valid_question_ids:
                    invalid_answers += 1
                    issues.append(f"❌ {candidate_id}: Kysymys '{answer['question_id']}' ei ole olemassa")
                    continue
                
                # Tarkista vastausarvo
                if not DataValidator.validate_answer_value(answer["answer_value"]):
                    invalid_answers += 1
                    issues.append(f"❌ {candidate_id}: Virheellinen vastausarvo {answer['answer_value']}")
                    continue
                
                # Tarkista luottamustaso
                if not DataValidator.validate_confidence_level(answer.get("confidence", 3)):
                    invalid_answers += 1
                    issues.append(f"❌ {candidate_id}: Virheellinen luottamustaso {answer.get('confidence')}")
                    continue
                
                valid_answers += 1
        
        return {
            "status": "completed",
            "valid_answers": valid_answers,
            "invalid_answers": invalid_answers,
            "total_answers": valid_answers + invalid_answers,
            "issues": issues,
            "validity_percentage": (valid_answers / (valid_answers + invalid_answers)) * 100 if (valid_answers + invalid_answers) > 0 else 0
        }
    
    def find_duplicate_answers(self) -> List[Tuple[str, str]]:
        """Etsi duplikaattivastaukset (sama ehdokas + sama kysymys)"""
        
        try:
            candidates_data = read_json_file(self.candidates_file, {"candidates": []})
        except Exception:
            return []
        
        duplicates = []
        
        for candidate in candidates_data.get("candidates", []):
            if "answers" not in candidate:
                continue
            
            seen_questions = set()
            for answer in candidate["answers"]:
                if answer["question_id"] in seen_questions:
                    duplicates.append((candidate["candidate_id"], answer["question_id"]))
                else:
                    seen_questions.add(answer["question_id"])
        
        return duplicates
    
    def check_data_consistency(self) -> Dict:
        """Tarkista datan eheys"""
        
        try:
            candidates_data = read_json_file(self.candidates_file, {"candidates": []})
            questions_data = read_json_file(self.questions_file, {"questions": []})
        except Exception as e:
            return {"status": "error", "message": str(e)}
        
        # Tarkistukset
        checks = {
            "candidates_exist": len(candidates_data.get("candidates", [])) > 0,
            "questions_exist": len(questions_data.get("questions", [])) > 0,
            "answers_exist": any("answers" in c for c in candidates_data.get("candidates", [])),
            "no_duplicate_answers": len(self.find_duplicate_answers()) == 0
        }
        
        # Validoi vastaukset
        validation_result = self.validate_all_answers()
        checks["all_answers_valid"] = validation_result["invalid_answers"] == 0
        
        return {
            "status": "completed",
            "checks": checks,
            "validation": validation_result,
            "is_healthy": all(checks.values())
        }
