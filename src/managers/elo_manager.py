#!/usr/bin/env python3
import json
from datetime import datetime

class ELOManager:
    def __init__(self, election_id: str):
        self.election_id = election_id
        self.k_factor = 32
    
    def calculate_expected(self, rating_a: int, rating_b: int) -> float:
        """Laske odotettu tulos kahden kysymyksen välillä"""
        return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    
    def update_ratings(self, question_a: str, question_b: str, winner: str):
        """Päivitä ELO-luokitukset vertailun perusteella"""
        # Lataa kysymykset
        with open("data/runtime/questions.json", "r") as f:
            data = json.load(f)
        
        # Etsi kysymykset
        q_a = next((q for q in data["questions"] if q["local_id"] == question_a), None)
        q_b = next((q for q in data["questions"] if q["local_id"] == question_b), None)
        
        if not q_a or not q_b:
            raise ValueError("Kysymyksiä ei löydy")
        
        rating_a = q_a["elo_rating"]["current_rating"]
        rating_b = q_b["elo_rating"]["current_rating"]
        
        # Laske odotetut tulokset
        expected_a = self.calculate_expected(rating_a, rating_b)
        expected_b = self.calculate_expected(rating_b, rating_a)
        
        # Päivitä ratingit voittajan mukaan
        if winner == "a":
            actual_a, actual_b = 1.0, 0.0
        elif winner == "b":
            actual_a, actual_b = 0.0, 1.0
        else:  # tasapeli
            actual_a, actual_b = 0.5, 0.5
        
        # Laske uudet ratingit
        new_rating_a = rating_a + self.k_factor * (actual_a - expected_a)
        new_rating_b = rating_b + self.k_factor * (actual_b - expected_b)
        
        # Päivitä data
        q_a["elo_rating"]["current_rating"] = int(new_rating_a)
        q_a["elo_rating"]["comparison_delta"] = int(new_rating_a - rating_a)
        q_b["elo_rating"]["current_rating"] = int(new_rating_b)
        q_b["elo_rating"]["comparison_delta"] = int(new_rating_b - rating_b)
        
        # Tallenna
        with open("data/runtime/questions.json", "w") as f:
            json.dump(data, f, indent=2)
        
        return {
            "question_a": {"old": rating_a, "new": new_rating_a, "delta": new_rating_a - rating_a},
            "question_b": {"old": rating_b, "new": new_rating_b, "delta": new_rating_b - rating_b}
        }
    
    def get_question_stats(self):
        """Hae kysymysten tilastot"""
        with open("data/runtime/questions.json", "r") as f:
            data = json.load(f)
        
        questions = data["questions"]
        total = len(questions)
        
        if total == 0:
            return {
                "total_questions": 0,
                "average_rating": 0,
                "max_rating": 0,
                "min_rating": 0,
                "questions": []
            }
        
        avg_rating = sum(q["elo_rating"]["current_rating"] for q in questions) / total
        max_rating = max(q["elo_rating"]["current_rating"] for q in questions)
        min_rating = min(q["elo_rating"]["current_rating"] for q in questions)
        
        return {
            "total_questions": total,
            "average_rating": round(avg_rating, 1),
            "max_rating": max_rating,
            "min_rating": min_rating,
            "questions": [
                {
                    "id": q["local_id"],
                    "question": q["content"]["question"]["fi"],
                    "rating": q["elo_rating"]["current_rating"],
                    "category": q["content"]["category"],
                    "delta": q["elo_rating"].get("comparison_delta", 0)
                }
                for q in sorted(questions, key=lambda x: x["elo_rating"]["current_rating"], reverse=True)
            ]
        }
    
    def get_leaderboard(self, top_n: int = 10):
        """Hae kysymysten ranking-lista"""
        stats = self.get_question_stats()
        return stats["questions"][:top_n]
    
    def reset_ratings(self):
        """Nollaa kaikki ELO-luokitukset"""
        with open("data/runtime/questions.json", "r") as f:
            data = json.load(f)
        
        for question in data["questions"]:
            question["elo_rating"]["current_rating"] = 1000
            question["elo_rating"]["comparison_delta"] = 0
            question["elo_rating"]["vote_delta"] = 0
        
        with open("data/runtime/questions.json", "w") as f:
            json.dump(data, f, indent=2)
        
        return len(data["questions"])
