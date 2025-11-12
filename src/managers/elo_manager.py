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
        try:
            # Lataa kysymykset
            with open("data/runtime/questions.json", "r", encoding='utf-8') as f:
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
            with open("data/runtime/questions.json", "w", encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return {
                "question_a": {"old": rating_a, "new": new_rating_a, "delta": new_rating_a - rating_a},
                "question_b": {"old": rating_b, "new": new_rating_b, "delta": new_rating_b - rating_b}
            }
            
        except Exception as e:
            print(f"ELO-päivitysvirhe: {e}")
            raise
