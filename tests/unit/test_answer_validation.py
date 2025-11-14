#!/usr/bin/env python3
"""
Testit AnswerValidation-luokalle
"""
import pytest
import json
import tempfile
from pathlib import Path
from src.cli.answer_validation import AnswerValidation

class TestAnswerValidation:
    """Testit AnswerValidation-luokalle"""
    
    def setup_method(self):
        """Testien alustus"""
        self.temp_dir = tempfile.mkdtemp()
        self.election_id = "Testivaali2026"
        self.validation = AnswerValidation(self.election_id)
        
        # Aseta väliaikaiset tiedostopolut
        self.validation.candidates_file = str(Path(self.temp_dir) / "candidates.json")
        self.validation.questions_file = str(Path(self.temp_dir) / "questions.json")
    
    def teardown_method(self):
        """Testien siivous"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def create_test_data(self, include_invalid=False):
        """Luo testidata tiedostoihin"""
        # Luo kysymysdata
        questions_data = {
            "questions": [
                {
                    "local_id": "q_valid_001",
                    "content": {"question": {"fi": "Kelvollinen kysymys"}}
                },
                {
                    "local_id": "q_valid_002", 
                    "content": {"question": {"fi": "Toinen kelvollinen kysymys"}}
                }
            ],
            "metadata": {"election_id": self.election_id}
        }
        
        with open(self.validation.questions_file, 'w', encoding='utf-8') as f:
            json.dump(questions_data, f)
        
        # Luo ehdokasdata
        candidates_data = {
            "candidates": [
                {
                    "candidate_id": "cand_001",
                    "basic_info": {"name": {"fi": "Ehdokas 1"}},
                    "answers": [
                        {
                            "question_id": "q_valid_001",
                            "answer_value": 4,
                            "confidence": 5,
                            "explanation": {"fi": "Kelvollinen vastaus"}
                        },
                        {
                            "question_id": "q_valid_002",
                            "answer_value": 3,
                            "confidence": 4,
                            "explanation": {"fi": "Toinen kelvollinen vastaus"}
                        }
                    ]
                }
            ],
            "metadata": {"election_id": self.election_id}
        }
        
        if include_invalid:
            # Lisää virheellisiä vastauksia
            candidates_data["candidates"][0]["answers"].extend([
                {
                    "question_id": "q_invalid_001",  # Olematon kysymys
                    "answer_value": 5,
                    "confidence": 5
                },
                {
                    "question_id": "q_valid_001",
                    "answer_value": 10,  # Liian suuri arvo
                    "confidence": 5
                },
                {
                    "question_id": "q_valid_002", 
                    "answer_value": 4,
                    "confidence": 10  # Liian suuri luottamustaso
                }
            ])
        
        with open(self.validation.candidates_file, 'w', encoding='utf-8') as f:
            json.dump(candidates_data, f)
    
    def test_validate_all_answers_all_valid(self):
        """Testaa validointi kun kaikki vastaukset ovat kelvollisia"""
        self.create_test_data(include_invalid=False)
        
        result = self.validation.validate_all_answers()
        
        assert result["status"] == "completed"
        assert result["valid_answers"] == 2
        assert result["invalid_answers"] == 0
        assert result["total_answers"] == 2
        assert result["validity_percentage"] == 100.0
        assert len(result["issues"]) == 0
    
    def test_validate_all_answers_with_invalid(self):
        """Testaa validointi kun osa vastauksista on virheellisiä"""
        self.create_test_data(include_invalid=True)
        
        result = self.validation.validate_all_answers()
        
        assert result["status"] == "completed"
        assert result["valid_answers"] == 2  # 2 kelvollista
        assert result["invalid_answers"] == 3  # 3 virheellistä
        assert result["total_answers"] == 5
        assert result["validity_percentage"] == 40.0  # 2/5 = 40%
        assert len(result["issues"]) == 3
        
        # Tarkista että issues sisältää odotetut virheet
        issues_text = " ".join(result["issues"])
        assert "q_invalid_001" in issues_text
        assert "ei ole olemassa" in issues_text
        assert "10" in issues_text  # Liian suuri vastausarvo
    
    def test_find_duplicate_answers_no_duplicates(self):
        """Testaa duplikaattien etsintä ilman duplikaatteja"""
        self.create_test_data(include_invalid=False)
        
        duplicates = self.validation.find_duplicate_answers()
        
        assert len(duplicates) == 0
    
    def test_find_duplicate_answers_with_duplicates(self):
        """Testaa duplikaattien etsintä duplikaateilla"""
        # Luo data duplikaateilla
        candidates_data = {
            "candidates": [
                {
                    "candidate_id": "cand_001",
                    "basic_info": {"name": {"fi": "Ehdokas 1"}},
                    "answers": [
                        {
                            "question_id": "q_duplicate",
                            "answer_value": 4,
                            "confidence": 5
                        },
                        {
                            "question_id": "q_duplicate",  # Duplikaatti!
                            "answer_value": 3, 
                            "confidence": 4
                        },
                        {
                            "question_id": "q_unique",
                            "answer_value": 5,
                            "confidence": 5
                        }
                    ]
                }
            ],
            "metadata": {"election_id": self.election_id}
        }
        
        with open(self.validation.candidates_file, 'w', encoding='utf-8') as f:
            json.dump(candidates_data, f)
        
        duplicates = self.validation.find_duplicate_answers()
        
        assert len(duplicates) == 1
        assert duplicates[0] == ("cand_001", "q_duplicate")
    
    def test_check_data_consistency_healthy(self):
        """Testaa datan eheyden tarkistus terveellä datalla"""
        self.create_test_data(include_invalid=False)
        
        result = self.validation.check_data_consistency()
        
        assert result["status"] == "completed"
        assert result["is_healthy"] == True
        
        checks = result["checks"]
        assert checks["candidates_exist"] == True
        assert checks["questions_exist"] == True
        assert checks["answers_exist"] == True
        assert checks["no_duplicate_answers"] == True
        assert checks["all_answers_valid"] == True
        
        validation = result["validation"]
        assert validation["invalid_answers"] == 0
    
    def test_check_data_consistency_unhealthy(self):
        """Testaa datan eheyden tarkistus epäterveellä datalla"""
        self.create_test_data(include_invalid=True)
        
        result = self.validation.check_data_consistency()
        
        assert result["status"] == "completed"
        assert result["is_healthy"] == False
        
        checks = result["checks"]
        assert checks["all_answers_valid"] == False
        
        validation = result["validation"]
        assert validation["invalid_answers"] > 0
