#!/usr/bin/env python3
"""
Yksinkertainen testi ELO-vertailulle ilaan monimutkaisia importteja
"""
import sys
import os
import json
import random

def simple_elo_comparison():
    """Yksinkertainen ELO-vertailu testi"""
    print("🧪 Testataan ELO-vertailua (yksinkertainen versio)...")
    
    try:
        # Lataa kysymykset
        with open("data/runtime/questions.json", "r", encoding='utf-8') as f:
            questions_data = json.load(f)
        
        if len(questions_data["questions"]) < 2:
            print("❌ Tarvitaan vähintään 2 kysymystä")
            return False
        
        # Valitse kaksi ensimmäistä kysymystä
        q1 = questions_data["questions"][0]
        q2 = questions_data["questions"][1]
        
        print(f"\n📝 VERTAILTAVAT KYSYMYKSET:")
        print(f"1. {q1['content']['question']['fi']} (ELO: {q1['elo_rating']['current_rating']})")
        print(f"2. {q2['content']['question']['fi']} (ELO: {q2['elo_rating']['current_rating']})")
        
        # Yksinkertainen ELO-päivitys (testiversio)
        k_factor = 32
        old_rating_1 = q1['elo_rating']['current_rating']
        old_rating_2 = q2['elo_rating']['current_rating']
        
        # Oletetaan että ensimmäinen voittaa
        expected_1 = 1 / (1 + 10 ** ((old_rating_2 - old_rating_1) / 400))
        expected_2 = 1 / (1 + 10 ** ((old_rating_1 - old_rating_2) / 400))
        
        # Päivitä ratingit (ensimmäinen voittaa)
        new_rating_1 = old_rating_1 + k_factor * (1 - expected_1)
        new_rating_2 = old_rating_2 + k_factor * (0 - expected_2)
        
        # Päivitä data
        q1['elo_rating']['current_rating'] = int(new_rating_1)
        q1['elo_rating']['comparison_delta'] = int(new_rating_1 - old_rating_1)
        q2['elo_rating']['current_rating'] = int(new_rating_2)
        q2['elo_rating']['comparison_delta'] = int(new_rating_2 - old_rating_2)
        
        # Tallenna
        with open("data/runtime/questions.json", "w", encoding='utf-8') as f:
            json.dump(questions_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ ELO-vertailu suoritettu!")
        print(f"📊 {q1['local_id']}: {old_rating_1} → {new_rating_1:.0f} ({new_rating_1 - old_rating_1:+.0f})")
        print(f"📊 {q2['local_id']}: {old_rating_2} → {new_rating_2:.0f} ({new_rating_2 - old_rating_2:+.0f})")
        
        return True
        
    except Exception as e:
        print(f"❌ ELO-vertailu epäonnistui: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = simple_elo_comparison()
    sys.exit(0 if success else 1)
