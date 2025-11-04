# fix_demos_properly.py
#!/usr/bin/env python3
"""
Korjaa demo-skriptit oikein
"""

def fix_demo_comparisons():
    """Korjaa tests/demo_comparisons.py oikein"""
    with open('tests/demo_comparisons.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Korvaa koko tiedosto yksinkertaisella versiolla
    new_content = '''#!/usr/bin/env python3
"""
Demo: Kysymysvertailut - Korjattu versio
"""

import json
import random
import sys
import os
from datetime import datetime

# Lisää polku jotta importit toimivat
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from complete_elo_calculator import CompleteELOCalculator, ComparisonResult, UserTrustLevel
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
    import argparse
    
    parser = argparse.ArgumentParser(description='Kysymysvertailu demo')
    parser.add_argument('--user', required=True, help='Käyttäjätunnus')
    parser.add_argument('--count', type=int, default=3, help='Vertailujen määrä')
    
    args = parser.parse_args()
    
    print("🎯 DEMO: KYSYMYSVERTAILUT")
    print("=" * 50)
    print(f"Käyttäjä: {args.user}")
    print(f"Vertailuja: {args.count}")
    print()
    
    # Lataa kysymykset
    questions = load_questions()
    print(f"📊 Ladattu {len(questions)} kysymystä")
    
    if len(questions) < 2:
        print("❌ Tarvitaan vähintään 2 kysymystä vertailuun")
        return
    
    calculator = CompleteELOCalculator()
    successful_comparisons = 0
    
    # Tee vertailuja
    for i in range(args.count):
        print(f"\\n🔀 VERTAILU {i+1}/{args.count}:")
        
        # Valitse kaksi satunnaista kysymystä
        q1, q2 = random.sample(questions, 2)
        
        print(f"   A: {q1['content']['question']['fi'][:60]}...")
        print(f"   B: {q2['content']['question']['fi'][:60]}...")
        
        # Satunnainen tulos
        result = random.choice([ComparisonResult.A_WINS, ComparisonResult.B_WINS, ComparisonResult.TIE])
        print(f"   📊 Tulos: {result.value}")
        
        # Käytä ELO-laskinta
        try:
            elo_result = calculator.process_comparison(q1, q2, result, UserTrustLevel.REGULAR_USER)
            
            if elo_result["success"]:
                # Päivitä kysymykset
                changes = elo_result["changes"]
                q1['elo_rating']['current_rating'] = changes["question_a"]["new_rating"]
                q2['elo_rating']['current_rating'] = changes["question_b"]["new_rating"]
                
                # Päivitä vertailumäärä
                q1['elo_rating']['total_comparisons'] = q1['elo_rating'].get('total_comparisons', 0) + 1
                q2['elo_rating']['total_comparisons'] = q2['elo_rating'].get('total_comparisons', 0) + 1
                
                print(f"   📈 Uudet ratingit: A={q1['elo_rating']['current_rating']}, B={q2['elo_rating']['current_rating']}")
                successful_comparisons += 1
            else:
                print("   ❌ ELO-laskenta epäonnistui")
                
        except Exception as e:
            print(f"   ❌ Virhe vertailussa: {e}")
    
    # Tallenna päivitetyt kysymykset
    if successful_comparisons > 0:
        try:
            with open('runtime/questions.json', 'w', encoding='utf-8') as f:
                data = {
                    "metadata": {
                        "version": "2.0.0",
                        "last_updated": datetime.now().isoformat(),
                        "total_questions": len(questions),
                        "comparisons_performed": successful_comparisons
                    },
                    "questions": questions
                }
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\\n✅ {successful_comparisons} vertailua suoritettu ja tallennettu!")
        except Exception as e:
            print(f"\\n⚠️ Tallennus epäonnistui: {e}")
    else:
        print("\\n❌ Ei vertailuja suoritettu")
    
    print("\\n🎉 DEMO VALMIS!")

if __name__ == "__main__":
    main()
'''
    
    with open('tests/demo_comparisons.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("✅ demo_comparisons.py korjattu!")

def fix_demo_voting():
    """Korjaa tests/demo_voting.py oikein"""
    with open('tests/demo_voting.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Korvaa koko tiedosto yksinkertaisella versiolla
    new_content = '''#!/usr/bin/env python3
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
        print(f"\\n📋 KYSYMYS {i}/{votes_to_cast}:")
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
            print(f"\\n✅ Äänestys suoritettu! {successful_votes} ääntä annettu")
        except Exception as e:
            print(f"\\n⚠️ Tallennus epäonnistui: {e}")
    else:
        print("\\n❌ Ei ääniä annettu")
    
    print("\\n🎉 DEMO VALMIS!")

if __name__ == "__main__":
    main()
'''
    
    with open('tests/demo_voting.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("✅ demo_voting.py korjattu!")

if __name__ == "__main__":
    fix_demo_comparisons()
    fix_demo_voting()
    print("🎯 Demo-skriptit korjattu oikein!")
