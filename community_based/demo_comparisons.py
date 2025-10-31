# demo_comparisons.py
#!/usr/bin/env python3
"""
Demo: Kysymysvertailut - KORJATTU VERSIO
"""

import argparse
import sys
from pathlib import Path

# 🔒 LISÄTTY: Järjestelmän käynnistystarkistus
try:
    from system_bootstrap import verify_system_startup
    if not verify_system_startup():
        print("❌ Järjestelmän käynnistystarkistus epäonnistui")
        sys.exit(1)
except ImportError:
    print("⚠️  System bootstrap ei saatavilla - jatketaan ilman tarkistusta")

from complete_elo_calculator import CompleteELOCalculator, ComparisonResult, UserTrustLevel
from elo_manager import ELOManager
import json
from datetime import datetime

def make_demo_comparisons(count=5, user_id="demo_user"):
    """Tee demovertailuja"""
    
    print(f"🔀 DEMO: VERTAILUTESTIT")
    print("=" * 40)
    
    # Lataa kysymykset
    try:
        with open("runtime/questions.json", "r", encoding="utf-8") as f:
            questions_data = json.load(f)
        
        questions = questions_data["questions"]
        print(f"✅ Ladattu {len(questions)} kysymystä")
        
    except Exception as e:
        print(f"❌ Virhe kysymysten lataamisessa: {e}")
        return []
    
    # Alusta ELO-manageri
    try:
        elo_manager = ELOManager()
    except Exception as e:
        print(f"❌ ELO-managerin alustus epäonnistui: {e}")
        return []
    
    results = []
    
    for i in range(min(count, len(questions) - 1)):
        question_a = questions[i]
        question_b = questions[i + 1]
        
        print(f"\n🔄 Vertailu {i+1}:")
        print(f"   A: {question_a['content']['question']['fi'][:30]}...")
        print(f"   B: {question_b['content']['question']['fi'][:30]}...")
        
        # Valitse satunnainen tulos
        import random
        result_type = random.choice([ComparisonResult.A_WINS, ComparisonResult.B_WINS, ComparisonResult.TIE])
        result_text = "A voittaa" if result_type == ComparisonResult.A_WINS else "B voittaa" if result_type == ComparisonResult.B_WINS else "Tasapeli"
        print(f"   📊 Tulos: {result_text}")
        
        try:
            # Käsittele vertailu
            result = elo_manager.handle_comparison(
                user_id=user_id,
                question_a_id=question_a["local_id"],
                question_b_id=question_b["local_id"], 
                result=result_type,
                user_trust=UserTrustLevel.REGULAR_USER
            )
            
            if result["success"]:
                changes = result["rating_changes"]
                print(f"   ✅ Muutokset:")
                print(f"      A: {changes['question_a']['old_rating']:.1f} → {changes['question_a']['new_rating']:.1f} ({changes['question_a']['change']:+.1f})")
                print(f"      B: {changes['question_b']['old_rating']:.1f} → {changes['question_b']['new_rating']:.1f} ({changes['question_b']['change']:+.1f})")
                results.append(result)
            else:
                print(f"   ⚠️  Estetty: {result['error']}")
                if 'details' in result:
                    for check in result['details'].get('checks', []):
                        print(f"      - {check}")
                
        except Exception as e:
            print(f"   ❌ Virhe vertailussa: {e}")
    
    # Näytä lopputila
    print(f"\n📊 LOPPUTILA - TESTIKYSYMYKSET:")
    print("-" * 40)
    
    for i, q in enumerate(questions[:4]):
        rating = q["elo_rating"]["current_rating"]
        comparisons = q["elo_rating"].get("total_comparisons", 0)
        text = q['content']['question']['fi'][:30] + '...' if len(q['content']['question']['fi']) > 30 else q['content']['question']['fi']
        print(f"{i+1}. {rating:.1f} pts (vertailut: {comparisons}) - {text}")
    
    return results

def main():
    """Pääohjelma"""
    parser = argparse.ArgumentParser(description="Demo: Kysymysvertailut")
    parser.add_argument("--count", type=int, default=5, help="Vertailujen määrä")
    parser.add_argument("--user", default="demo_user", help="Käyttäjän ID")
    
    args = parser.parse_args()
    
    print("🎯 DEMO: KYSYMYSVERTAILUT")
    print("=" * 50)
    print(f"Käyttäjä: {args.user}")
    print(f"Vertailuja: {args.count}")
    print()
    
    results = make_demo_comparisons(args.count, args.user)
    
    print(f"\n🎉 DEMO VALMIS!")
    print(f"Suoritettu {len(results)} vertailua")
    
    # Tarkista system_chain
    try:
        chain_file = Path("runtime/system_chain.json")
        if chain_file.exists():
            with open(chain_file, "r", encoding="utf-8") as f:
                chain_data = json.load(f)
            print(f"🔗 System chain lohkoja: {len(chain_data.get('blocks', []))}")
    except:
        pass

if __name__ == "__main__":
    main()
