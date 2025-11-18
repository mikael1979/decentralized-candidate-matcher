#!/usr/bin/env python3
import click
import json
from datetime import datetime
import os
import sys
from pathlib import Path

# LISÄTTY: Lisää src hakemisto Python-polkuun
sys.path.insert(0, str(Path(__file__).parent.parent))

"""
Vastausten raportointi ja listaus - UUSI MODULAARINEN
"""
import click
from typing import Dict, List

# KORJATTU: Käytetään yhteisiä file_utils-funktioita
try:
    from core.file_utils import read_json_file
    from core.validators import validate_candidate_id, validate_question_id
except ImportError:
    from core.file_utils import read_json_file
    from core.validators import validate_candidate_id, validate_question_id

class AnswerReports:
    """Vastausten raportointi ja listaus"""
    
    def __init__(self, election_id: str):
        self.election_id = election_id
        self.candidates_file = f"data/runtime/candidates.json"
        self.questions_file = f"data/runtime/questions.json"
    
    def list_candidate_answers(self, candidate_id: str) -> bool:
        """Listaa tietyn ehdokkaan vastaukset"""
        
        if not validate_candidate_id(candidate_id):
            click.echo(f"❌ Virheellinen ehdokas ID: {candidate_id}")
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
        
        click.echo(f"📝 EHDOKKAAN {candidate_id} VASTAUKSET")
        click.echo("=" * 50)
        
        if "answers" not in candidate or not candidate["answers"]:
            click.echo("❌ Ei vastauksia")
            return True
        
        # Lataa kysymykset nimeä varten
        questions_map = self._load_questions_map()
        
        for answer in candidate["answers"]:
            question_text = questions_map.get(answer["question_id"], answer["question_id"])
            click.echo(f"❓ {question_text}")
            click.echo(f"   📊 Vastaus: {answer['answer_value']}/5")
            click.echo(f"   🎯 Varmuus: {answer['confidence']}/5")
            if answer["explanation"]["fi"]:
                click.echo(f"   💬 Perustelu: {answer['explanation']['fi']}")
            click.echo()
        
        return True
    
    def list_question_answers(self, question_id: str) -> bool:
        """Listaa tietyn kysymyksen vastaukset"""
        
        if not validate_question_id(question_id):
            click.echo(f"❌ Virheellinen kysymys ID: {question_id}")
            return False
        
        try:
            candidates_data = read_json_file(self.candidates_file, {"candidates": []})
        except Exception as e:
            click.echo(f"❌ Ehdokasrekisterin lukuvirhe: {e}")
            return False
        
        # Lataa kysymykset nimeä varten
        questions_map = self._load_questions_map()
        
        click.echo(f"📝 KYSYMYKSEN {question_id} VASTAUKSET")
        click.echo("=" * 50)
        
        question_text = questions_map.get(question_id, question_id)
        click.echo(f"Kysymys: {question_text}")
        click.echo()
        
        found_answers = False
        for candidate in candidates_data.get("candidates", []):
            if "answers" in candidate:
                answer = next((a for a in candidate["answers"] if a["question_id"] == question_id), None)
                if answer:
                    found_answers = True
                    click.echo(f"👤 {candidate['basic_info']['name']['fi']} ({candidate['candidate_id']})")
                    click.echo(f"   📊 Vastaus: {answer['answer_value']}/5")
                    click.echo(f"   🎯 Varmuus: {answer['confidence']}/5")
                    if answer["explanation"]["fi"]:
                        click.echo(f"   💬 Perustelu: {answer['explanation']['fi']}")
                    click.echo()
        
        if not found_answers:
            click.echo("❌ Ei vastauksia tähän kysymykseen")
        
        return True
    
    def show_summary(self) -> bool:
        """Näytä kaikkien ehdokkaiden vastausyhteenveto"""
        
        try:
            candidates_data = read_json_file(self.candidates_file, {"candidates": []})
        except Exception as e:
            click.echo(f"❌ Ehdokasrekisterin lukuvirhe: {e}")
            return False
        
        click.echo("📊 EHDOKKAIDEN VASTAUSYHTEENVETO")
        click.echo("=" * 50)
        
        total_answers = 0
        candidates_with_answers = 0
        
        for candidate in candidates_data.get("candidates", []):
            answer_count = len(candidate.get("answers", []))
            total_answers += answer_count
            if answer_count > 0:
                candidates_with_answers += 1
            
            candidate_name = candidate["basic_info"]["name"]["fi"]
            click.echo(f"👤 {candidate_name} ({candidate['candidate_id']}): {answer_count} vastausta")
        
        click.echo()
        click.echo(f"📈 YHTEENVETO:")
        click.echo(f"   Ehdokkaita: {len(candidates_data['candidates'])}")
        click.echo(f"   Vastanneita: {candidates_with_answers}")
        click.echo(f"   Vastauksia yhteensä: {total_answers}")
        
        if len(candidates_data["candidates"]) > 0:
            coverage = (candidates_with_answers / len(candidates_data["candidates"])) * 100
            click.echo(f"   Vastauskattavuus: {coverage:.1f}%")
        
        return True
    
    def _load_questions_map(self) -> Dict[str, str]:
        """Lataa kysymysten mappaus ID -> teksti"""
        questions_map = {}
        try:
            questions_data = read_json_file(self.questions_file, {"questions": []})
            questions_map = {q["local_id"]: q["content"]["question"]["fi"] for q in questions_data.get("questions", [])}
        except Exception:
            # Jos kysymysrekisteriä ei voi lukea, käytetään ID:itä suoraan
            pass
        return questions_map
