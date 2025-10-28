#!/usr/bin/env python3
"""
Demo: Tee useita äänestyksiä testataksesi äänestysjärjestelmää
"""

import json
import sys
sys.path.append('.')

from complete_elo_calculator import VoteType, UserTrustLevel
from elo_manager import ELOManager

def main():
    print("🗳️ DEMO: ÄÄNESTYSTESTIT")
    print("=" * 40)
    
    manager = ELOManager("runtime/questions.json")
    
    # Lataa kysymykset
    with open('runtime/questions.json', 'r') as f:
        data = json.load(f)
    
    questions = data['questions']
    print(f"✅ Ladattu {len(questions)} kysymystä")
    
    # Tee erilaisia äänestyksiä
    votes = [
        (0, VoteType.UPVOTE, 5, "Täysin samaa mieltä"),
        (1, VoteType.DOWNVOTE, 4, "Melkein eri mieltä"),
        (2, VoteType.UPVOTE, 3, "Samaa mieltä"),
        (3, VoteType.DOWNVOTE, 2, "Hieman eri mieltä"),
        (0, VoteType.UPVOTE, 1, "Hieman samaa mieltä")
    ]
    
    for i, (q_idx, vote_type, confidence, description) in enumerate(votes):
        question = questions[q_idx]
        
        print(f"\n📊 Äänestys {i+1}: {description}")
        print(f"   Kysymys: {question['content']['question']['fi'][:40]}...")
        print(f"   Ääni: {'👍 UP' if vote_type == VoteType.UPVOTE else '👎 DOWN'}, Luottamus: {confidence}/5")
        
        vote_result = manager.handle_vote(
            user_id=f"demo_voter_{i}",
            question_id=question["local_id"],
            vote_type=vote_type,
            confidence=confidence,
            user_trust=UserTrustLevel.REGULAR_USER
        )
        
        if vote_result["success"]:
            change = vote_result["vote_result"]["change"]
            print(f"   ✅ Vaikutus: {change['old_rating']:.1f} → {change['new_rating']:.1f} ({change['change']:+.1f})")
        else:
            print(f"   ⚠️  Estetty: {vote_result['error']}")
    
    # Näytä äänestystilastot
    print(f"\n📈 ÄÄNESTYSTILASTOT:")
    print("-" * 40)
    
    with open("runtime/questions.json", 'r') as f:
        updated_data = json.load(f)
    
    for i, q in enumerate(questions[:4]):
        updated_q = next((uq for uq in updated_data["questions"] if uq["local_id"] == q["local_id"]), None)
        if updated_q:
            rating = updated_q["elo_rating"]["current_rating"]
            votes = updated_q["elo_rating"].get("total_votes", 0)
            upvotes = updated_q["elo_rating"].get("up_votes", 0)
            downvotes = updated_q["elo_rating"].get("down_votes", 0)
            print(f"{i+1}. {rating:.1f} pts (äänet: {votes}, 👍: {upvotes}, 👎: {downvotes})")

if __name__ == "__main__":
    main()
