#!/usr/bin/env python3
"""
Testaa ELO-järjestelmää kreikkalaisten jumalien datalla - KORJATTU VERSIO
"""

import json
import sys
import os
from datetime import datetime
from datetime import timezone

# 🔒 LISÄTTY: Järjestelmän käynnistystarkistus
try:
    from system_bootstrap import verify_system_startup
    if not verify_system_startup():
        print("❌ Järjestelmän käynnistystarkistus epäonnistui")
        sys.exit(1)
except ImportError:
    print("⚠️  System bootstrap ei saatavilla - jatketaan ilman tarkistusta")

# Lisää nykyinen hakemisto polkuun jotta moduulit löytyvät
sys.path.append('.')

try:
    from complete_elo_calculator import CompleteELOCalculator, ComparisonResult, VoteType, UserTrustLevel
    from elo_manager import ELOManager
except ImportError as e:
    print(f"❌ Moduulien latausvirhe: {e}")
    print("💡 Varmista että complete_elo_calculator.py ja elo_manager.py ovat hakemistossa")
    sys.exit(1)

def test_elo_with_greek_gods():
    """Testaa ELO-järjestelmää kreikkalaisten jumalien datalla"""
    
    print("🏛️  TESTATAAN ELO-JÄRJESTELMÄÄ KREIKKALAISTEN JUMALIEN DATALLA")
    print("="*60)
    
    try:
        # Alusta ELO manager
        elo_manager = ELOManager("runtime/questions.json")
        
        # Lataa testikysymykset
        with open("runtime/questions.json", 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
        
        questions = questions_data["questions"]
        print(f"✅ Ladattu {len(questions)} kysymystä")
        
        # Testaa vertailut
        print("\n🔀 VERTAILUTESTIT:")
        print("-" * 30)
        
        # Valitse ensimmäiset 5 kysymystä testaamiseen
        test_questions = questions[:5]
        
        for i in range(3):
            question_a = test_questions[i]
            question_b = test_questions[(i + 1) % len(test_questions)]
            
            print(f"\nVertailu {i+1}:")
            print(f"  A: {question_a['content']['question']['fi'][:50]}...")
            print(f"  B: {question_b['content']['question']['fi'][:50]}...")
            
            result = elo_manager.handle_comparison(
                user_id=f"test_user_{i}",
                question_a_id=question_a["local_id"],
                question_b_id=question_b["local_id"],
                result=ComparisonResult.A_WINS,
                user_trust=UserTrustLevel.REGULAR_USER
            )
            
            if result["success"]:
                changes = result["rating_changes"]
                print(f"✅ Muutokset:")
                print(f"   A: {changes['question_a']['old_rating']:.1f} → {changes['question_a']['new_rating']:.1f} ({changes['question_a']['change']:+.1f})")
                print(f"   B: {changes['question_b']['old_rating']:.1f} → {changes['question_b']['new_rating']:.1f} ({changes['question_b']['change']:+.1f})")
            else:
                print(f"⚠️  Estetty: {result['error']}")
                if 'details' in result:
                    print(f"   Syy: {result['details']['checks']}")
        
        # Testaa äänestykset
        print("\n🗳️  ÄÄNESTYSTESTIT:")
        print("-" * 30)
        
        for i, question in enumerate(test_questions[:3]):
            print(f"\nÄänestys {i+1}: {question['content']['question']['fi'][:50]}...")
            
            # Upvote
            result = elo_manager.handle_vote(
                user_id=f"test_voter_{i}",
                question_id=question["local_id"],
                vote_type=VoteType.UPVOTE,
                confidence=4,
                user_trust=UserTrustLevel.REGULAR_USER
            )
            
            if result["success"]:
                change = result["vote_result"]["change"]
                print(f"✅ Upvote: {change['old_rating']:.1f} → {change['new_rating']:.1f} ({change['change']:+.1f})")
            else:
                print(f"⚠️  Estetty: {result['error']}")
        
        # Näytä lopulliset ratingit
        print("\n📊 LOPPUTILA - TOP 5 KYSYMYSTÄ:")
        print("-" * 40)
        
        with open("runtime/questions.json", 'r', encoding='utf-8') as f:
            updated_questions = json.load(f)
        
        # Lajittele ratingin mukaan
        sorted_questions = sorted(
            updated_questions["questions"], 
            key=lambda x: x["elo_rating"]["current_rating"], 
            reverse=True
        )
        
        for i, question in enumerate(sorted_questions[:5]):
            rating = question["elo_rating"]["current_rating"]
            comparisons = question["elo_rating"].get("total_comparisons", 0)
            votes = question["elo_rating"].get("total_votes", 0)
            print(f"{i+1}. {rating:.1f} pts (C:{comparisons}, V:{votes}) - {question['content']['question']['fi'][:40]}...")
        
        print(f"\n🎉 ELO-testit valmiit! Järjestelmä toimii odotetusti.")
        
        return True
        
    except Exception as e:
        print(f"❌ TESTI EPÄONNISTUI: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rate_limiting():
    """Testaa rate limiting -toimintaa"""
    print("\n🛡️  TESTATAAN RATE LIMITINGIÄ:")
    print("-" * 30)
    
    try:
        elo_manager = ELOManager("runtime/questions.json")
        
        with open("runtime/questions.json", 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
        
        test_question = questions_data["questions"][0]
        
        print(f"Testataan kysymystä: {test_question['content']['question']['fi'][:40]}...")
        
        # Tee useita äänestyksiä nopeasti testataksemme rate limitingiä
        blocked_count = 0
        successful_count = 0
        
        for i in range(15):  # Yritä 15 ääntä (yli päivärajan)
            result = elo_manager.handle_vote(
                user_id="rate_limit_tester",
                question_id=test_question["local_id"],
                vote_type=VoteType.UPVOTE,
                confidence=3,
                user_trust=UserTrustLevel.REGULAR_USER
            )
            
            if result["success"]:
                successful_count += 1
                print(f"  Ääni {i+1}: ✅ Hyväksytty")
            else:
                blocked_count += 1
                print(f"  Ääni {i+1}: ❌ Estetty - {result['error']}")
                break  # Lopeta kun tulee ensimmäinen esto
        
        print(f"\n📈 Rate limiting -tulokset:")
        print(f"   Onnistuneet äänet: {successful_count}")
        print(f"   Estetyt äänet: {blocked_count}")
        
        return successful_count > 0 and blocked_count > 0
        
    except Exception as e:
        print(f"❌ Rate limiting -testi epäonnistui: {e}")
        return False

def main():
    """Pääohjelma"""
    print("🚀 KREIKKALAISTEN JUMALIEN ELO-TESTIT")
    print("="*50)
    
    # Testaa perustoiminnot
    success1 = test_elo_with_greek_gods()
    
    # Testaa rate limiting
    success2 = test_rate_limiting()
    
    # Yhteenveto
    print("\n" + "="*50)
    print("🎯 TESTITULOKSET:")
    print(f"   Perustoiminnot: {'✅ ONNISTUI' if success1 else '❌ EPÄONNISTUI'}")
    print(f"   Rate limiting:  {'✅ ONNISTUI' if success2 else '❌ EPÄONNISTUI'}")
    
    if success1 and success2:
        print("\n🎉 KAIKKI TESTIT ONNISTUIVAT! ELO-järjestelmä on valmis.")
        print("\n💡 SEURAAVA VAIHE:")
        print("   - Testaa järjestelmää enemmän vertailuilla")
        print("   - Kokeile eri käyttäjärooleja (new_user, trusted_user, validator)")
        print("   - Testaa konfliktien hallintaa")
    else:
        print("\n⚠️  JOITKIN TESTIT EPÄONNISTUIVAT. Tarkista virheilmoitukset.")

if __name__ == "__main__":
    main()
