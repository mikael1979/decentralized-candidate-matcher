#!/usr/bin/env python3
import json

def debug_elo_system():
    """Debuggaa ELO-järjestelmän toimintaa"""
    
    print("🐛 ELO-JÄRJESTELMÄN DEBUG")
    print("=" * 40)
    
    # Tarkista questions.json
    try:
        with open("data/runtime/questions.json", "r") as f:
            data = json.load(f)
        
        print("✅ questions.json ladattu onnistuneesti")
        print(f"📊 Kysymyksiä: {len(data['questions'])}")
        
        for i, q in enumerate(data["questions"]):
            print(f"  {i+1}. {q['local_id']}: {q['content']['question']['fi']}")
            print(f"     Luokitus: {q['elo_rating']['current_rating']}")
        
    except Exception as e:
        print(f"❌ Virhe questions.json lukemisessa: {e}")
        return
    
    # Testaa ELO-laskenta
    print()
    print("🧮 ELO-LASKENTATESTI:")
    
    rating_a = 1000
    rating_b = 1000
    k_factor = 32
    
    expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    expected_b = 1 / (1 + 10 ** ((rating_a - rating_b) / 400))
    
    print(f"  Rating A: {rating_a}, Rating B: {rating_b}")
    print(f"  Odotettu A: {expected_a:.3f}, Odotettu B: {expected_b:.3f}")
    
    # Testaa eri tulokset
    test_cases = [
        ("A voittaa", 1.0, 0.0),
        ("B voittaa", 0.0, 1.0), 
        ("Tasapeli", 0.5, 0.5)
    ]
    
    for desc, actual_a, actual_b in test_cases:
        new_a = rating_a + k_factor * (actual_a - expected_a)
        new_b = rating_b + k_factor * (actual_b - expected_b)
        print(f"  {desc}: A={new_a:.1f} ({new_a-rating_a:+.1f}), B={new_b:.1f} ({new_b-rating_b:+.1f})")

if __name__ == "__main__":
    debug_elo_system()
