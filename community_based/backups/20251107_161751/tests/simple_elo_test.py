#!/usr/bin/env python3
"""
Yksinkertainen ELO-testi joka varmistaa että kaikki moduulit toimivat
"""

import json
import sys
import os

# Lisää nykyinen hakemisto polkuun
sys.path.append('.')

def simple_elo_test():
    """Yksinkertainen testi joka varmistaa perustoiminnallisuuden"""
    
    print("🧪 YKSINKERTAINEN ELO-TESTI")
    print("="*40)
    
    try:
        # 1. Testaa että tiedostot löytyvät
        print("1. 📁 Tarkistetaan tiedostot...")
        required_files = [
            "runtime/questions.json",
            "runtime/parties.json", 
            "runtime/candidates.json"
        ]
        
        for file in required_files:
            if os.path.exists(file):
                print(f"   ✅ {file} löytyy")
            else:
                print(f"   ❌ {file} puuttuu")
                return False
        
        # 2. Testaa että kysymystiedosto on validi JSON
        print("2. 📊 Tarkistetaan kysymysdata...")
        with open("runtime/questions.json", 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
        
        question_count = len(questions_data.get("questions", []))
        print(f"   ✅ {question_count} kysymystä ladattu")
        
        # 3. Näytä ensimmäiset 3 kysymystä
        print("3. ❓ Näytetään esimerkkikysymyksiä:")
        for i, question in enumerate(questions_data["questions"][:3]):
            print(f"   {i+1}. {question['content']['question']['fi']}")
        
        # 4. Testaa ELO-calculatorin lataus
        print("4. ⚡ Testataan ELO-calculator...")
        try:
            from complete_elo_calculator import CompleteELOCalculator, ComparisonResult, VoteType, UserTrustLevel
            calculator = CompleteELOCalculator()
            print("   ✅ ELO-calculator ladattu onnistuneesti")
        except ImportError as e:
            print(f"   ❌ ELO-calculatorin lataus epäonnistui: {e}")
            return False
        
        # 5. Testaa ELO-managerin lataus
        print("5. 🔄 Testataan ELO-manager...")
        try:
            from elo_manager import ELOManager
            manager = ELOManager("runtime/questions.json")
            print("   ✅ ELO-manager ladattu onnistuneesti")
        except ImportError as e:
            print(f"   ❌ ELO-managerin lataus epäonnistui: {e}")
            return False
        
        print("\n🎉 PERUSTESTIT ONNISTUIVAT!")
        print("\n💡 Nyt voit suorittaa täydellisen testin:")
        print("   python test_elo_with_greek_gods.py")
        
        return True
        
    except Exception as e:
        print(f"❌ TESTI EPÄONNISTUI: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = simple_elo_test()
    sys.exit(0 if success else 1)
