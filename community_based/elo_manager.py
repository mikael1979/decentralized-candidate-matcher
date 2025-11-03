#!/usr/bin/env python3
# elo_manager.py - KORJATTU VERSIO
"""
ELO Manager - Hallitsee kysymysten ELO-luokituksia
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

class ELOManager:
    """Hallinnoi kysymysten ELO-luokituksia"""
    
    def __init__(self, questions_file: str = "runtime/questions.json"):
        self.questions_file = Path(questions_file)
        self.questions = self._load_questions()
    
    def _load_questions(self) -> List[Dict]:
        """Lataa kysymykset tiedostosta"""
        if not self.questions_file.exists():
            return []
        
        try:
            with open(self.questions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('questions', [])
        except Exception as e:
            print(f"❌ Virhe ladattaessa kysymyksiä: {e}")
            return []
    
    def _save_questions(self):
        """Tallenna kysymykset tiedostoon"""
        try:
            data = {
                "metadata": {
                    "version": "2.0.0",
                    "total_questions": len(self.questions)
                },
                "questions": self.questions
            }
            
            with open(self.questions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"❌ Virhe tallentaessa kysymyksiä: {e}")
    
    # TEHDÄÄN METODIT JULKISIKSI
    def load_questions(self) -> List[Dict]:
        """Lataa kysymykset (julkinen metodi)"""
        return self._load_questions()
    
    def save_questions(self):
        """Tallenna kysymykset (julkinen metodi)"""
        self._save_questions()
    
    def update_question_rating(self, question_id: str, rating_data: Dict):
        """Päivitä kysymyksen rating"""
        for question in self.questions:
            if question["local_id"] == question_id:
                # Päivitä rating
                question["elo_rating"]["current_rating"] = rating_data["new_rating"]
                
                # Päivitä deltat
                old_rating = rating_data["old_rating"]
                new_rating = rating_data["new_rating"]
                change = new_rating - old_rating
                
                if "comparison" in rating_data.get("type", ""):
                    question["elo_rating"]["comparison_delta"] += change
                elif "vote" in rating_data.get("type", ""):
                    question["elo_rating"]["vote_delta"] += change
                
                # Päivitä tilastot
                question["elo_rating"]["total_comparisons"] = question["elo_rating"].get("total_comparisons", 0) + 1
                
                break
    
    def get_question_by_id(self, question_id: str) -> Optional[Dict]:
        """Hae kysymys ID:llä"""
        for question in self.questions:
            if question["local_id"] == question_id:
                return question
        return None
    
    def get_top_questions(self, limit: int = 10) -> List[Dict]:
        """Hae parhaat kysymykset ratingin perusteella"""
        sorted_questions = sorted(self.questions, 
                                key=lambda x: x["elo_rating"]["current_rating"], 
                                reverse=True)
        return sorted_questions[:limit]
    
    def get_random_questions(self, count: int = 2) -> List[Dict]:
        """Hae satunnaisia kysymyksiä"""
        import random
        if len(self.questions) <= count:
            return self.questions
        return random.sample(self.questions, count)
    
    def add_question(self, question_data: Dict) -> bool:
        """Lisää uusi kysymys"""
        try:
            # Varmista että kysymyksellä on kaikki tarvittavat kentät
            required_fields = ["local_id", "content", "elo_rating", "timestamps"]
            for field in required_fields:
                if field not in question_data:
                    print(f"❌ Puuttuva kenttä: {field}")
                    return False
            
            # Lisää kysymys
            self.questions.append(question_data)
            self._save_questions()
            return True
            
        except Exception as e:
            print(f"❌ Virhe lisättäessä kysymystä: {e}")
            return False

# Testaus
if __name__ == "__main__":
    manager = ELOManager()
    questions = manager.load_questions()
    print(f"📊 Kysymyksiä ladattu: {len(questions)}")
    
    if questions:
        top_questions = manager.get_top_questions(3)
        print("🏆 TOP 3 KYSYMYSTÄ:")
        for i, q in enumerate(top_questions, 1):
            rating = q["elo_rating"]["current_rating"]
            print(f"{i}. {rating:.1f} - {q['content']['question']['fi'][:50]}...")
