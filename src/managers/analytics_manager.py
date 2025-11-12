#!/usr/bin/env python3
"""
Analytics ja tilastojen hallinta - testausversio
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

class AnalyticsManager:
    def __init__(self, election_id: str):
        self.election_id = election_id
        self.data_dir = Path("data/runtime")
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Hae järjestelmän tilastot"""
        stats = {
            "election_id": self.election_id,
            "generated_at": datetime.now().isoformat(),
            "file_stats": {},
            "content_stats": {}
        }
        
        # Tiedostotilastot
        files = [
            "meta.json", "questions.json", "candidates.json", "parties.json"
        ]
        
        for file in files:
            file_path = self.data_dir / file
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    stats["file_stats"][file] = {
                        "exists": True,
                        "size_kb": round(file_path.stat().st_size / 1024, 2)
                    }
                    
                    # Sisältötilastot
                    if file == "questions.json":
                        stats["content_stats"]["questions"] = len(data.get("questions", []))
                    
                    elif file == "candidates.json":
                        candidates = data.get("candidates", [])
                        stats["content_stats"]["candidates"] = len(candidates)
                        
                        # Vastaustilastot
                        total_answers = sum(len(c.get("answers", [])) for c in candidates)
                        candidates_with_answers = sum(1 for c in candidates if c.get("answers"))
                        stats["content_stats"]["total_answers"] = total_answers
                        stats["content_stats"]["candidates_with_answers"] = candidates_with_answers
                    
                    elif file == "parties.json":
                        parties = data.get("parties", [])
                        stats["content_stats"]["parties"] = len(parties)
                        
                except Exception as e:
                    stats["file_stats"][file] = {"exists": True, "error": str(e)}
            else:
                stats["file_stats"][file] = {"exists": False}
        
        return stats
    
    def get_question_analytics(self) -> Dict[str, Any]:
        """Hae kysymysten analytics-tiedot"""
        questions_file = self.data_dir / "questions.json"
        if not questions_file.exists():
            return {}
        
        try:
            with open(questions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            questions = data.get("questions", [])
            if not questions:
                return {}
            
            # Kysymysten analytics
            analytics = {
                "total_questions": len(questions),
                "categories": {},
                "elo_distribution": {
                    "top_5": [],
                    "bottom_5": []
                }
            }
            
            # Kategoriat
            for question in questions:
                category = question.get("content", {}).get("category", "unknown")
                analytics["categories"][category] = analytics["categories"].get(category, 0) + 1
            
            return analytics
            
        except Exception as e:
            print(f"Analytics-virhe: {e}")
            return {}
    
    def generate_health_report(self) -> Dict[str, Any]:
        """Luo järjestelmän terveysraportti"""
        stats = self.get_system_stats()
        question_analytics = self.get_question_analytics()
        
        report = {
            "election_id": self.election_id,
            "report_generated": datetime.now().isoformat(),
            "system_health": "healthy",
            "issues": [],
            "recommendations": []
        }
        
        # Tarkista ongelmat
        if stats["content_stats"].get("candidates", 0) == 0:
            report["issues"].append("Ei ehdokkaita")
            report["recommendations"].append("Lisää ehdokkaita")
        
        if stats["content_stats"].get("questions", 0) < 2:
            report["issues"].append("Liian vähän kysymyksiä")
            report["recommendations"].append("Lisää vähintään 2 kysymystä")
        
        if report["issues"]:
            report["system_health"] = "needs_attention"
        
        report["stats"] = stats
        report["question_analytics"] = question_analytics
        
        return report
