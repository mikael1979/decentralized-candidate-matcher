#!/usr/bin/env python3
"""
Analytics ja tilastotyökalu
"""
import click
import json
from datetime import datetime
import os
import sys
from pathlib import Path

# LISÄTTY: Lisää src hakemisto Python-polkuun
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config_manager import get_election_id, get_data_path
from core.file_utils import read_json_file


def generate_system_stats(election_id):
    """Generoi järjestelmätilastot"""
    data_path = get_data_path(election_id)
    
    stats = {
        "election_id": election_id,
        "generated_at": datetime.now().isoformat(),
        "file_stats": {},
        "content_stats": {
            "questions": 0,
            "candidates": 0,
            "total_answers": 0,
            "candidates_with_answers": 0,
            "parties": 0
        }
    }
    
    # Tarkista tiedostot
    files_to_check = ["meta.json", "questions.json", "candidates.json", "parties.json"]
    
    for filename in files_to_check:
        file_path = Path(data_path) / filename
        file_stat = {"exists": file_path.exists(), "size_kb": 0}
        
        if file_path.exists():
            size_bytes = file_path.stat().st_size
            file_stat["size_kb"] = round(size_bytes / 1024, 2)
        
        stats["file_stats"][filename] = file_stat
    
    # Lataa sisältötiedot
    try:
        # Kysymykset
        questions_file = Path(data_path) / "questions.json"
        if questions_file.exists():
            questions_data = read_json_file(questions_file)
            stats["content_stats"]["questions"] = len(questions_data.get("questions", []))
        
        # Ehdokkaat
        candidates_file = Path(data_path) / "candidates.json"
        if candidates_file.exists():
            candidates_data = read_json_file(candidates_file)
            stats["content_stats"]["candidates"] = len(candidates_data.get("candidates", []))
        
        # Vastaukset
        answers_file = Path(data_path) / "candidate_answers.json"
        if answers_file.exists():
            answers_data = read_json_file(answers_file)
            answers = answers_data.get("answers", [])
            stats["content_stats"]["total_answers"] = len(answers)
            
            # Laske ehdokkaat joilla on vastauksia
            candidates_with_answers = set()
            for answer in answers:
                candidates_with_answers.add(answer.get("candidate_id"))
            stats["content_stats"]["candidates_with_answers"] = len(candidates_with_answers)
        
        # Puolueet
        parties_file = Path(data_path) / "parties.json"
        if parties_file.exists():
            parties_data = read_json_file(parties_file)
            stats["content_stats"]["parties"] = len(parties_data.get("parties", []))
            
    except Exception as e:
        print(f"⚠️  Virhe data-tiedostojen latauksessa: {e}")
    
    return stats


def generate_question_analytics(election_id):
    """Generoi kysymysten analytics"""
    data_path = get_data_path(election_id)
    
    analytics = {
        "total_questions": 0,
        "categories": {},
        "elo_distribution": {
            "top_5": [],
            "bottom_5": []
        }
    }
    
    try:
        questions_file = Path(data_path) / "questions.json"
        if questions_file.exists():
            questions_data = read_json_file(questions_file)
            questions = questions_data.get("questions", [])
            analytics["total_questions"] = len(questions)
            
            # Kategoriat
            for question in questions:
                category = question.get("category", "Muu")
                analytics["categories"][category] = analytics["categories"].get(category, 0) + 1
            
            # ELO-jakauma (jos saatavilla)
            elo_questions = [q for q in questions if "elo_rating" in q]
            if elo_questions:
                sorted_by_elo = sorted(elo_questions, key=lambda x: x.get("elo_rating", 1000), reverse=True)
                analytics["elo_distribution"]["top_5"] = [
                    {"id": q.get("id"), "elo": q.get("elo_rating"), "text": q.get("question_fi", "")[:50]}
                    for q in sorted_by_elo[:5]
                ]
                analytics["elo_distribution"]["bottom_5"] = [
                    {"id": q.get("id"), "elo": q.get("elo_rating"), "text": q.get("question_fi", "")[:50]}
                    for q in sorted_by_elo[-5:]
                ]
                
    except Exception as e:
        print(f"⚠️  Virhe kysymys-analytiikassa: {e}")
    
    return analytics


def generate_health_report(election_id):
    """Generoi terveysraportin"""
    stats = generate_system_stats(election_id)
    question_analytics = generate_question_analytics(election_id)
    
    health_report = {
        "election_id": election_id,
        "report_generated": datetime.now().isoformat(),
        "system_health": "healthy",
        "issues": [],
        "recommendations": [],
        "stats": stats,
        "question_analytics": question_analytics
    }
    
    # Tarkista ongelmat
    content_stats = stats["content_stats"]
    
    if content_stats["questions"] == 0:
        health_report["issues"].append("Ei kysymyksiä")
        health_report["recommendations"].append("Lisää kysymyksiä: python src/cli/manage_questions.py --add")
        health_report["system_health"] = "needs_attention"
    
    if content_stats["candidates"] == 0:
        health_report["issues"].append("Ei ehdokkaita")
        health_report["recommendations"].append("Lisää ehdokkaita: python src/cli/manage_candidates.py --add")
        health_report["system_health"] = "needs_attention"
    
    if content_stats["candidates_with_answers"] == 0:
        health_report["issues"].append("Ei ehdokkaita vastauksilla")
        health_report["recommendations"].append("Lisää vastauksia: python src/cli/manage_answers.py add")
        health_report["system_health"] = "needs_attention"
    
    if content_stats["candidates_with_answers"] < content_stats["candidates"]:
        answer_coverage = (content_stats["candidates_with_answers"] / content_stats["candidates"]) * 100
        if answer_coverage < 50:
            health_report["issues"].append(f"Alhainen vastauskattavuus: {answer_coverage:.1f}%")
            health_report["recommendations"].append("Kehota ehdokkaita vastaamaan kysymyksiin")
    
    return health_report


@click.group()
def analytics():
    """Analytics ja tilastotyökalut"""
    pass


@analytics.command()
@click.option('--election', required=False, help='Vaalin tunniste (valinnainen, käytetään configista)')
def wrapper(election):
    """
    Analytics wrapper - generoi kattavan analytics-raportin
    """
    # Hae election_id configista jos parametria ei annettu
    election_id = get_election_id(election)
    if not election_id:
        print("❌ Vaali-ID:tä ei annettu eikä config tiedostoa löydy.")
        print("💡 Käytä: --election VAALI_ID tai asenna järjestelmä ensin: python src/cli/install.py --first-install")
        sys.exit(1)
    
    print(f"📊 Analytics: {election_id}")
    
    try:
        # Generoi raportit
        system_stats = generate_system_stats(election_id)
        question_analytics = generate_question_analytics(election_id)
        health_report = generate_health_report(election_id)
        
        # Yhdistä raportit
        full_report = {
            "metadata": {
                "election_id": election_id,
                "generated_at": datetime.now().isoformat(),
                "report_type": "full_analytics"
            },
            "system_stats": system_stats,
            "question_analytics": question_analytics,
            "health_report": health_report
        }
        
        # Tulosta JSON-muodossa
        print(json.dumps(full_report, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"❌ Analytics-epäonnistui: {e}")
        sys.exit(1)


if __name__ == "__main__":
    analytics()
