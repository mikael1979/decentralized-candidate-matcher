#!/usr/bin/env python3
"""
Demo Comparisons - Testaa ELO-vertailuja
"""

import sys
from pathlib import Path

# Lisää polku
sys.path.append(str(Path(__file__).parent))

def main():
    print("🎲 ELO-VERTAILUTESTI")
    print("=" * 40)
    
    try:
        from elo_manager import ELOManager
        from complete_elo_calculator import ComparisonResult, UserTrustLevel
        
        # Alusta manager
        manager = ELOManager()
        questions = manager.load_questions()
        
        if len(questions) < 2:
            print("❌ Tarvitaan vähintään 2 kysymystä vertailuun")
            return
        
        print(f"📊 Kysymyksiä saatavilla: {len(questions)}")
        
        # Valitse 2 satunnaista kysymystä
        import random
        selected_questions = random.sample(questions, 2)
        
        question_a = selected_questions[0]
        question_b = selected_questions[1]
        
        print(f"🔀 VERTAILU:")
        print(f"   A: {question_a['content']['question']['fi'][:50]}...")
        print(f"   B: {question_b['content']['question']['fi'][:50]}...")
        
        # Simuloi vertailu (A voittaa)
        result = manager.handle_comparison(
            user_id="demo_user",
            question_a_id=question_a["local_id"],
            question_b_id=question_b["local_id"],
            result="a_wins",
            user_trust="regular_user"
        )
        
        if result["success"]:
            changes = result["changes"]
            print("✅ Vertailu käsitelty!")
            print(f"   A: {changes['question_a']['change']:+d} → {changes['question_a']['new_rating']:.1f}")
            print(f"   B: {changes['question_b']['change']:+d} → {changes['question_b']['new_rating']:.1f}")
        else:
            print(f"❌ Vertailu epäonnistui: {result.get('error')}")
            
    except ImportError as e:
        print(f"❌ Moduulia ei saatavilla: {e}")
    except Exception as e:
        print(f"❌ Odottamaton virhe: {e}")

if __name__ == "__main__":
    main()
