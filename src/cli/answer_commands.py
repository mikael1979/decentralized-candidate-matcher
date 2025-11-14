#!/usr/bin/env python3
"""
Vastausten peruskomentojen hallinta - UUSI MODULAARINEN
"""
import click
from datetime import datetime
from typing import Dict, List

# KORJATTU: Käytetään yhteisiä file_utils-funktioita
try:
    from src.core.file_utils import read_json_file, write_json_file
    from src.core.validators import DataValidator, validate_candidate_id, validate_question_id
except ImportError:
    from core.file_utils import read_json_file, write_json_file
    from core.validators import DataValidator, validate_candidate_id, validate_question_id

class AnswerCommands:
    """Vastausten peruskomentojen hallinta"""
    
    def __init__(self, election_id: str):
        self.election_id = election_id
        self.candidates_file = f"data/runtime/candidates.json"
        self.questions_file = f"data/runtime/questions.json"
    
    def _validate_answer_data(self, answer_value: int, confidence: int) -> bool:
        """Validoi vastausdata"""
        return DataValidator.validate_answer_value(answer_value) and \
               DataValidator.validate_confidence_level(confidence)
    
    def _check_duplicate_answer(self, candidate_data: dict, question_id: str) -> bool:
        """Tarkista onko vastaus jo olemassa"""
        return any(a["question_id"] == question_id for a in candidate_data.get("answers", []))
    
    def add_answer(self, candidate_id: str, question_id: str, answer_value: int, 
                  confidence: int, explanation_fi: str = None, explanation_en: str = None, 
                  explanation_sv: str = None) -> bool:
        """Lisää ehdokkaan vastaus kysymykseen"""
        
        # Validoi syötteet
        if not validate_candidate_id(candidate_id):
            click.echo(f"❌ Virheellinen ehdokas ID: {candidate_id}")
            return False
        
        if not validate_question_id(question_id):
            click.echo(f"❌ Virheellinen kysymys ID: {question_id}")
            return False
        
        if not self._validate_answer_data(answer_value, confidence):
            click.echo("❌ Virheellinen vastausdata. Vastaus: -5 - +5, Varmuus: 1-5")
            return False
        
        # Tarkista että ehdokas on olemassa
        try:
            candidates_data = read_json_file(self.candidates_file, {"candidates": []})
        except Exception as e:
            click.echo(f"❌ Ehdokasrekisterin lukuvirhe: {e}")
            return False
        
        candidate = next((c for c in candidates_data.get("candidates", []) if c["candidate_id"] == candidate_id), None)
        if not candidate:
            click.echo(f"❌ Ehdokasta '{candidate_id}' ei löydy")
            return False
        
        # Tarkista että kysymys on olemassa
        try:
            questions_data = read_json_file(self.questions_file, {"questions": []})
        except Exception as e:
            click.echo(f"❌ Kysymysrekisterin lukuvirhe: {e}")
            return False
        
        question = next((q for q in questions_data.get("questions", []) if q["local_id"] == question_id), None)
        if not question:
            click.echo(f"❌ Kysymystä '{question_id}' ei löydy")
            return False
        
        # Tarkista duplikaatti
        if self._check_duplicate_answer(candidate, question_id):
            click.echo(f"❌ Ehdokkaalla on jo vastaus kysymykseen {question_id}")
            return False
        
        # Luo tai päivitä vastaus
        if "answers" not in candidate:
            candidate["answers"] = []
        
        # Luo uusi vastaus
        new_answer = {
            "question_id": question_id,
            "answer_value": answer_value,
            "confidence": confidence,
            "explanation": {
                "fi": explanation_fi or "",
                "en": explanation_en or "",
                "sv": explanation_sv or ""
            },
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        candidate["answers"].append(new_answer)
        
        # Tallenna
        try:
            write_json_file(self.candidates_file, candidates_data)
            click.echo(f"✅ Vastaus lisätty: {candidate_id} → {question_id}")
            click.echo(f"📊 Arvo: {answer_value}/5, Varmuus: {confidence}/5")
            if explanation_fi:
                click.echo(f"💬 Perustelu: {explanation_fi}")
            return True
        except Exception as e:
            click.echo(f"❌ Vastauksen tallennus epäonnistui: {e}")
            return False
    
    def remove_answer(self, candidate_id: str, question_id: str) -> bool:
        """Poista ehdokkaan vastaus"""
        
        # Validoi syötteet
        if not validate_candidate_id(candidate_id):
            click.echo(f"❌ Virheellinen ehdokas ID: {candidate_id}")
            return False
        
        if not validate_question_id(question_id):
            click.echo(f"❌ Virheellinen kysymys ID: {question_id}")
            return False
        
        try:
            candidates_data = read_json_file(self.candidates_file, {"candidates": []})
        except Exception as e:
            click.echo(f"❌ Ehdokasrekisterin lukuvirhe: {e}")
            return False
        
        candidate = next((c for c in candidates_data.get("candidates", []) if c["candidate_id"] == candidate_id), None)
        if not candidate:
            click.echo(f"❌ Ehdokasta '{candidate_id}' ei löydy")
            return False
        
        if "answers" not in candidate:
            click.echo("❌ Ehdokkaalla ei ole vastauksia")
            return False
        
        # Etsi ja poista vastaus
        initial_count = len(candidate["answers"])
        candidate["answers"] = [a for a in candidate["answers"] if a["question_id"] != question_id]
        
        if len(candidate["answers"]) == initial_count:
            click.echo(f"❌ Vastausta ei löytynyt: {candidate_id} → {question_id}")
            return False
        
        # Tallenna
        try:
            write_json_file(self.candidates_file, candidates_data)
            click.echo(f"✅ Vastaus poistettu: {candidate_id} → {question_id}")
            click.echo(f"📊 Ehdokkaalla on nyt {len(candidate['answers'])} vastausta")
            return True
        except Exception as e:
            click.echo(f"❌ Vastauksen poisto epäonnistui: {e}")
            return False
