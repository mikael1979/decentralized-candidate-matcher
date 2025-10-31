#!/usr/bin/env python3
"""
Demo: Kysymysvertailut - KORJATTU VERSIO
Käyttö: python demo_comparisons.py --user testi --count 5
"""

import argparse
import json
import sys
from pathlib import Path

# Lisää polku jotta moduulit löytyvät
sys.path.append('.')

def initialize_question_comparisons(questions_data, min_comparisons=5):
    """Alusta kysymykset vaaditulla määrällä vertailuja"""
    for question in questions_data['questions']:
        if question['elo_rating']['total_comparisons'] < min_comparisons:
            question['elo_rating']['total_comparisons'] = min_comparisons
    
    # Tallenna päivitetty questions.json
    with open('runtime/questions.json', 'w', encoding='utf-8') as f:
        json.dump(questions_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Alustettu {len(questions_data['questions'])} kysymystä vertailuihin")

def make_demo_comparisons(count: int, user_id: str = "demo_user"):
    """Tee demovertailuja"""
    
    print("🎯 DEMO: KYSYMYSVERTAILUT")
    print("=" * 50)
    print(f"Käyttäjä: {user_id}")
    print(f"Vertailuja: {count}")
    print()
    
    try:
        # Lataa kysymykset
        with open('runtime/questions.json', 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
        
        print(f"✅ Ladattu {len(questions_data['questions'])} kysymystä")
        print()
        
        # Alusta vertailut jos tarpeen
        initialize_question_comparisons(questions_data)
        
        # Tuo ELO-laskenta
        from complete_elo_calculator import (
            CompleteELOCalculator, 
            ComparisonResult, 
            UserTrustLevel
        )
        
        calculator = CompleteELOCalculator()
        results = []
        
        print("🔀 DEMO: VERTAILUTESTIT")
        print("=" * 40)
        
        for i in range(count):
            if len(questions_data['questions']) < 2:
                print("❌ Liian vähän kysymyksiä vertailuihin")
                break
            
            # Valitse kaksi satunnaista kysymystä
            import random
            question_a = random.choice(questions_data['questions'])
            question_b = random.choice(questions_data['questions'])
            
            # Varmista että eivät ole samoja
            while question_a['local_id'] == question_b['local_id']:
                question_b = random.choice(questions_data['questions'])
            
            print(f"\n🔄 Vertailu {i+1}:")
            text_a = question_a['content']['question']['fi'][:40] + '...' if len(question_a['content']['question']['fi']) > 40 else question_a['content']['question']['fi']
            text_b = question_b['content']['question']['fi'][:40] + '...' if len(question_b['content']['question']['fi']) > 40 else question_b['content']['question']['fi']
            print(f"   A: {text_a}")
            print(f"   B: {text_b}")
            
            # Satunnainen tulos
            import random
            result_type = random.choice([
                ComparisonResult.A_WINS, 
                ComparisonResult.B_WINS, 
                ComparisonResult.TIE
            ])
            
            result_text = {
                ComparisonResult.A_WINS: "A voittaa",
                ComparisonResult.B_WINS: "B voittaa", 
                ComparisonResult.TIE: "Tasapeli"
            }[result_type]
            
            print(f"   📊 Tulos: {result_text}")
            
            # Käsittele vertailu
            comparison_result = calculator.process_comparison(
                question_a, question_b, result_type, UserTrustLevel.REGULAR_USER
            )
            
            if comparison_result["success"]:
                # Päivitä kysymysten ratingit
                changes = comparison_result["changes"]
                
                # Etsi kysymykset datasta ja päivitä
                for q in questions_data['questions']:
                    if q['local_id'] == question_a['local_id']:
                        q['elo_rating']['current_rating'] = changes['question_a']['new_rating']
                        q['elo_rating']['comparison_delta'] += changes['question_a']['change']
                        q['elo_rating']['total_comparisons'] += 1
                    elif q['local_id'] == question_b['local_id']:
                        q['elo_rating']['current_rating'] = changes['question_b']['new_rating']
                        q['elo_rating']['comparison_delta'] += changes['question_b']['change']
                        q['elo_rating']['total_comparisons'] += 1
                
                results.append({
                    'question_a': question_a['local_id'],
                    'question_b': question_b['local_id'], 
                    'result': result_type.value,
                    'rating_changes': changes
                })
                
                print(f"   ✅ Rating-muutokset: A {changes['question_a']['change']:+.1f}, B {changes['question_b']['change']:+.1f}")
            else:
                print(f"   ⚠️  Estetty: {comparison_result['error']}")
                if 'details' in comparison_result:
                    for check in comparison_result['details'].get('checks', []):
                        print(f"      - {check}")
        
        # Tallenna päivitetty data
        with open('runtime/questions.json', 'w', encoding='utf-8') as f:
            json.dump(questions_data, f, indent=2, ensure_ascii=False)
        
        # Näytä tilanne
        print(f"\n📊 LOPPUTILA - TESTIKYSYMYKSET:")
        print("-" * 40)
        
        # Lajittele ratingin mukaan
        sorted_questions = sorted(
            questions_data['questions'][:4],  # Näytä 4 ensimmäistä
            key=lambda x: x['elo_rating']['current_rating'], 
            reverse=True
        )
        
        for i, q in enumerate(sorted_questions, 1):
            text = q['content']['question']['fi'][:40] + '...' if len(q['content']['question']['fi']) > 40 else q['content']['question']['fi']
            print(f"{i}. {q['elo_rating']['current_rating']:.1f} pts (vertailut: {q['elo_rating']['total_comparisons']}) - {text}")
        
        # Kirjaa system_chainiin
        try:
            from system_chain_manager import log_action
            log_action(
                "demo_comparisons",
                f"Demovertailut: {len(results)} kpl, käyttäjä: {user_id}",
                question_ids=[r['question_a'] for r in results] + [r['question_b'] for r in results],
                user_id=user_id,
                metadata={"comparison_count": len(results)}
            )
        except ImportError:
            print("⚠️  System chain ei saatavilla - skipataan kirjaus")
        
        return results
        
    except Exception as e:
        print(f"❌ Virhe demovertailuissa: {e}")
        import traceback
        traceback.print_exc()
        return []

def main():
    """Pääohjelma"""
    parser = argparse.ArgumentParser(description="Demo: Kysymysvertailut")
    parser.add_argument('--user', default='demo_user', help='Käyttäjän ID')
    parser.add_argument('--count', type=int, default=3, help='Vertailujen määrä')
    
    args = parser.parse_args()
    
    # Suorita vertailut
    results = make_demo_comparisons(args.count, args.user)
    
    # Näytä yhteenveto
    print(f"\n🎉 DEMO VALMIS!")
    print(f"Suoritettu {len(results)} vertailua")
    
    # Tarkista system_chain
    try:
        with open('runtime/system_chain.json', 'r', encoding='utf-8') as f:
            chain_data = json.load(f)
        print(f"🔗 System chain lohkoja: {len(chain_data.get('blocks', []))}")
    except:
        print("🔗 System chain: Ei saatavilla")

if __name__ == "__main__":
    main()
