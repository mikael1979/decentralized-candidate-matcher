#!/usr/bin/env python3
"""
Demo: Tee useita vertailuja testataksesi ELO-järjestelmää
"""

import json
import sys
sys.path.append('.')

from complete_elo_calculator import ComparisonResult, UserTrustLevel
from elo_manager import ELOManager

def main():
    print("🔀 DEMO: VERTAILUTESTIT")
    print("=" * 40)
    
    manager = ELOManager("runtime/questions.json")
    
    # Lataa kysymykset
    with open('runtime/questions.json', 'r') as f:
        data = json.load(f)
    
    questions = data['questions']
    print(f"✅ Ladattu {len(questions)} kysymystä")
    
    # Valitse 4 kysymystä testaamiseen
    test_questions = questions[:4]
    
    # Tee useita vertailuja
    comparisons = [
        (0, 1, ComparisonResult.A_WINS, "A voittaa"),
        (1, 2, ComparisonResult.B_WINS, "B voittaa"), 
        (2, 3, ComparisonResult.TIE, "Tasapeli"),
        (0, 3, ComparisonResult.A_WINS, "A voittaa"),
        (1, 3, ComparisonResult.B_WINS, "B voittaa")
    ]
    
    for i, (idx_a, idx_b, result, description) in enumerate(comparisons):
        q_a = test_questions[idx_a]
        q_b = test_questions[idx_b]
        
        print(f"\n🔄 Vertailu {i+1}: {description}")
        print(f"   A: {q_a['content']['question']['fi'][:30]}...")
        print(f"   B: {q_b['content']['question']['fi'][:30]}...")
        
        comparison_result = manager.handle_comparison(
            user_id=f"demo_user_{i}",
            question_a_id=q_a["local_id"],
            question_b_id=q_b["local_id"],
            result=result,
            user_trust=UserTrustLevel.REGULAR_USER
        )
        
        if comparison_result["success"]:
            changes = comparison_result["rating_changes"]
            print(f"   ✅ Muutokset:")
            print(f"      A: {changes['question_a']['old_rating']:.1f} → {changes['question_a']['new_rating']:.1f} ({changes['question_a']['change']:+.1f})")
            print(f"      B: {changes['question_b']['old_rating']:.1f} → {changes['question_b']['new_rating']:.1f} ({changes['question_b']['change']:+.1f})")
        else:
            print(f"   ⚠️  Estetty: {comparison_result['error']}")
    
    # Näytä lopulliset ratingit
    print(f"\n📊 LOPPUTILA - TESTIKYSYMYKSET:")
    print("-" * 40)
    
    with open("runtime/questions.json", 'r') as f:
        updated_data = json.load(f)
    
    for i, q in enumerate(test_questions):
        updated_q = next((uq for uq in updated_data["questions"] if uq["local_id"] == q["local_id"]), None)
        if updated_q:
            rating = updated_q["elo_rating"]["current_rating"]
            comparisons = updated_q["elo_rating"].get("total_comparisons", 0)
            print(f"{i+1}. {rating:.1f} pts (vertailut: {comparisons}) - {updated_q['content']['question']['fi'][:30]}...")

if __name__ == "__main__":
    main()
