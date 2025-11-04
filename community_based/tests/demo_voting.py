#!/usr/bin/env python3
"""
Demo: Äänestys - Korjattu versio
"""

import json
import random
import sys
import os
from datetime import datetime

# Lisää polku jotta importit toimivat
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from complete_elo_calculator import VoteType, UserTrustLevel, CompleteELOCalculator
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def load_questions():
    """Lataa kysymykset"""
    try:
        with open('runtime/questions.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('questions', [])
    except Exception as e:
        print(f"❌ Virhe ladattaessa kysymyksiä: {e}")
        return []

def main():
    print("🗳️ DEMO: ÄÄNESTYSTESTIT")
    print("=" * 50)
    
    # Lataa kysymykset
    questions = load_questions()
    print(f"✅ Ladattu {len(questions)} kysymystä")
    
    if not questions:
        print("❌ Ei kysymyksiä saatavilla")
        return
    
    calculator = CompleteELOCalculator()
    successful_votes = 0
    
    # Äänestä 5 satunnaista kysymystä
    votes_to_cast = min(5, len(questions))
    voted_questions = random.sample(questions, votes_to_cast)
    
    for i, question in enumerate(voted_questions, 1):
        print(f"\n📋 KYSYMYS {i}/{votes_to_cast}:")
        print(f"   {question['content']['question']['fi']}")
        
        # Satunnainen ääni
        vote_type = random.choice([VoteType.UPVOTE, VoteType.DOWNVOTE])
        confidence = random.randint(1, 5)
        
        print(f"   🗳️ Ääni: {vote_type.value} (luottamus: {confidence}/5)")
        
        # Käytä ELO-laskinta
        try:
            vote_result = calculator.process_vote(question, vote_type, confidence, UserTrustLevel.REGULAR_USER)
            
            if vote_result["success"]:
                # Päivitä kysymys
                change_data = vote_result["change"]
                question['elo_rating']['current_rating'] = change_data["new_rating"]
                question['elo_rating']['total_votes'] = question['elo_rating'].get('total_votes', 0) + 1
                
                if vote_type == VoteType.UPVOTE:
                    question['elo_rating']['up_votes'] = question['elo_rating'].get('up_votes', 0) + 1
                else:
                    question['elo_rating']['down_votes'] = question['elo_rating'].get('down_votes', 0) + 1
                
                print(f"   📈 Rating: {change_data['new_rating']} (Δ{'+' if change_data['change'] > 0 else ''}{change_data['change']})")
                successful_votes += 1
            else:
                print("   ❌ Äänen käsittely epäonnistui")
                
        except Exception as e:
            print(f"   ❌ Virhe äänestyksessä: {e}")
    
    # Tallenna päivitetyt kysymykset
    if successful_votes > 0:
        try:
            with open('runtime/questions.json', 'w', encoding='utf-8') as f:
                data = {
                    "metadata": {
                        "version": "2.0.0",
                        "last_updated": datetime.now().isoformat(),
                        "total_questions": len(questions),
                        "votes_cast": successful_votes
                    },
                    "questions": questions
                }
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\n✅ Äänestys suoritettu! {successful_votes} ääntä annettu")
        except Exception as e:
            print(f"\n⚠️ Tallennus epäonnistui: {e}")
    else:
        print("\n❌ Ei ääniä annettu")
    
    print("\n🎉 DEMO VALMIS!")

if __name__ == "__main__":
    main()
