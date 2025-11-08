# simple_demo_voting.py
#!/usr/bin/env python3
"""
Yksinkertainen äänestys demo
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
    print("🗳️ YKSINKERTAINEN ÄÄNESTYS DEMO")
    print("=" * 50)
    
    # Lataa kysymykset
    questions = load_questions()
    print(f"📊 Ladattu {len(questions)} kysymystä")
    
    if not questions:
        print("❌ Ei kysymyksiä saatavilla")
        return
    
    # Äänestä 5 kysymystä
    voted_questions = random.sample(questions, min(5, len(questions)))
    
    for i, question in enumerate(voted_questions, 1):
        print(f"\n📋 KYSYMYS {i}/{len(voted_questions)}:")
        print(f"   {question['content']['question']['fi']}")
        
        # Satunnainen ääni
        vote = random.choice(['UPVOTE', 'DOWNVOTE'])
        confidence = random.randint(1, 5)
        
        print(f"   🗳️ Ääni: {vote} (luottamus: {confidence}/5)")
        
        # Päivitä rating
        current_rating = question['elo_rating']['current_rating']
        if vote == 'UPVOTE':
            change = 2 * confidence
            new_rating = current_rating + change
        else:  # DOWNVOTE
            change = -2 * confidence
            new_rating = current_rating + change
        
        question['elo_rating']['current_rating'] = new_rating
        question['elo_rating']['total_votes'] = question['elo_rating'].get('total_votes', 0) + 1
        
        if vote == 'UPVOTE':
            question['elo_rating']['up_votes'] = question['elo_rating'].get('up_votes', 0) + 1
        else:
            question['elo_rating']['down_votes'] = question['elo_rating'].get('down_votes', 0) + 1
        
        print(f"   📈 Rating muutos: {current_rating} → {new_rating} (Δ{change})")
    
    # Tallenna päivitetyt kysymykset
    try:
        with open('runtime/questions.json', 'w', encoding='utf-8') as f:
            data = {
                "metadata": {
                    "version": "2.0.0", 
                    "last_updated": datetime.now().isoformat(),
                    "total_questions": len(questions),
                    "voting_demo_performed": True
                },
                "questions": questions
            }
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Äänestys suoritettu! {len(voted_questions)} kysymystä äänestetty")
    except Exception as e:
        print(f"⚠️  Tallennus epäonnistui: {e}")

if __name__ == "__main__":
   
