#!/usr/bin/env python3
"""
Testit AnswerCommands-luokalle
"""
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from src.cli.answer_commands import AnswerCommands

class TestAnswerCommands:
    """Testit AnswerCommands-luokalle"""
    
    def setup_method(self):
        """Testien alustus"""
        self.temp_dir = tempfile.mkdtemp()
        self.election_id = "Testivaali2026"
        self.commands = AnswerCommands(self.election_id)
        
        # Aseta väliaikaiset tiedostopolut
        self.commands.candidates_file = str(Path(self.temp_dir) / "candidates.json")
        self.commands.questions_file = str(Path(self.temp_dir) / "questions.json")
    
    def teardown_method(self):
        """Testien siivous"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def create_test_data(self):
        """Luo testidata tiedostoihin"""
        # Luo ehdokasdata
        candidates_data = {
            "candidates": [
                {
                    "candidate_id": "cand_test_001",
                    "basic_info": {
                        "name": {"fi": "Testi Ehdokas", "en": "Test Candidate", "sv": "Testkandidat"},
                        "party": "Testipuolue",
                        "domain": "Testialue"
                    },
                    "answers": []
                }
            ],
            "metadata": {"election_id": self.election_id}
        }
        
        with open(self.commands.candidates_file, 'w', encoding='utf-8') as f:
            json.dump(candidates_data, f)
        
        # Luo kysymysdata
        questions_data = {
            "questions": [
                {
                    "local_id": "q_test_001",
                    "content": {
                        "category": "testaus",
                        "question": {
                            "fi": "Mitä mieltä olet testauksesta?",
                            "en": "What do you think about testing?",
                            "sv": "Vad tycker du om testning?"
                        }
                    },
                    "elo_rating": {
                        "current_rating": 1000,
                        "comparison_delta": 0,
                        "vote_delta": 0
                    }
                }
            ],
            "metadata": {"election_id": self.election_id}
        }
        
        with open(self.commands.questions_file, 'w', encoding='utf-8') as f:
            json.dump(questions_data, f)
    
    @patch('click.echo')
    def test_add_answer_success(self, mock_echo):
        """Testaa onnistunut vastauksen lisäys"""
        self.create_test_data()
        
        result = self.commands.add_answer(
            candidate_id="cand_test_001",
            question_id="q_test_001",
            answer_value=4,
            confidence=5,
            explanation_fi="Testiperustelu"
        )
        
        assert result == True
        
        # Tarkista että vastaus lisättiin
        with open(self.commands.candidates_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        candidate = data["candidates"][0]
        assert len(candidate["answers"]) == 1
        assert candidate["answers"][0]["question_id"] == "q_test_001"
        assert candidate["answers"][0]["answer_value"] == 4
        assert candidate["answers"][0]["confidence"] == 5
        assert candidate["answers"][0]["explanation"]["fi"] == "Testiperustelu"
        
        # Tarkista että success-viesti näytettiin
        assert any("✅ Vastaus lisätty" in str(call) for call in mock_echo.call_args_list)
    
    @patch('click.echo')
    def test_add_answer_duplicate_prevention(self, mock_echo):
        """Testaa että samaa vastausta ei voi lisätä kahteen kertaan"""
        self.create_test_data()
        
        # Ensimmäinen lisäys
        self.commands.add_answer("cand_test_001", "q_test_001", 4, 5)
        
        # Toinen lisäys samalle kysymykselle
        result = self.commands.add_answer("cand_test_001", "q_test_001", 3, 4)
        
        assert result == False
        mock_echo.assert_called_with("❌ Ehdokkaalla on jo vastaus kysymykseen q_test_001")
    
    @patch('click.echo')
    def test_add_answer_validation(self, mock_echo):
        """Testaa vastausdatan validointia"""
        self.create_test_data()
        
        # Testaa virheellistä ehdokas ID:tä
        result = self.commands.add_answer("invalid_id", "q_test_001", 4, 5)
        assert result == False
        
        # Testaa virheellistä kysymys ID:tä
        result = self.commands.add_answer("cand_test_001", "invalid_q", 4, 5)
        assert result == False
        
        # Testaa virheellistä vastausarvoa
        result = self.commands.add_answer("cand_test_001", "q_test_001", 10, 5)  # Liian suuri
        assert result == False
        
        # Testaa virheellistä luottamustasoa
        result = self.commands.add_answer("cand_test_001", "q_test_001", 4, 10)  # Liian suuri
        assert result == False
    
    @patch('click.echo')
    def test_remove_answer_success(self, mock_echo):
        """Testaa onnistunut vastauksen poisto"""
        self.create_test_data()
        
        # Lisää vastaus ensin
        self.commands.add_answer("cand_test_001", "q_test_001", 4, 5)
        
        # Poista vastaus
        result = self.commands.remove_answer("cand_test_001", "q_test_001")
        
        assert result == True
        
        # Tarkista että vastaus poistettiin
        with open(self.commands.candidates_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        candidate = data["candidates"][0]
        assert len(candidate["answers"]) == 0
        
        # Tarkista että success-viesti näytettiin
        assert any("✅ Vastaus poistettu" in str(call) for call in mock_echo.call_args_list)
    
    @patch('click.echo')
    def test_remove_answer_not_found(self, mock_echo):
        """Testaa vastauksen poisto kun vastausta ei löydy"""
        self.create_test_data()
        
        result = self.commands.remove_answer("cand_test_001", "q_nonexistent")
        
        assert result == False
        mock_echo.assert_called_with("❌ Vastausta ei löytynyt: cand_test_001 → q_nonexistent")
