# simple_demo_comparisons.py
#!/usr/bin/env python3
"""
Yksinkertainen kysymysvertailu demo
"""

import json
import random
from datetime import datetime

def load_questions():
    """Lataa kysymykset"""
    try:
        with open('runtime/questions.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('questions', [])
    except:
        return []

def main():
    print("🎯 YKSINKERTAINEN KYSYMYSVERTAILU DEMO")
    print("=" * 50)
    
    # Lataa kysymykset
    questions = load_questions()
    print(f"📊 Ladattu {len(questions)} kysymystä")
    
    if len(questions) < 2:
        print("❌ Tarvitaan vähintään 2 kysymystä vertailuun")
        return
    
    # Tee 3 vertailua
    for i in range(3):
        print(f"\n🔀 VERTAILU {i+1}/3:")
        
        # Valitse kaksi satunnaista kysymystä
        q1, q2 = random.sample(questions, 2)
        
        print(f"   A: {q1['content']['question']['fi'][:50]}...")
        print(f"   B: {q2['content']['question']['fi'][:50]}...")
        
        # Satunnainen tulos
        result = random.choice(['A_WINS', 'B_WINS', 'TIE'])
        print(f"   📊 Tulos: {result}")
        
        # Päivitä ratingit (yksinkertainen)
        if result == 'A_WINS':
            q1['elo_rating']['current_rating'] += 10
            q2['elo_rating']['current_rating'] -= 10
        elif result == 'B_WINS':
            q1['elo_rating']['current_rating'] -= 10
            q2['elo_rating']['current_rating'] += 10
        else:  # TIE
            q1['elo_rating']['current_rating'] += 5
            q2['elo_rating']['current_rating'] += 5
        
        print(f"   📈 Uudet ratingit: A={q1['elo_rating']['current_rating']}, B={q2['elo_rating']['current_rating']}")
    
    # Tallenna päivitetyt kysymykset
    try:
        with open('runtime/questions.json', 'w', encoding='utf-8') as f:
            data = {
                "metadata": {
                    "version": "2.0.0",
                    "last_updated": datetime.now().isoformat(),
                    "total_questions": len(questions),
                    "demo_performed": True
                },
                "questions": questions
            }
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Kysymykset tallennettu ({len(questions)} kpl)")
    except Exception as e:
        print(f"⚠️  Tallennus epäonnistui: {e}")

if __name__ == "__main__":
    main()
