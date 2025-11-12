#!/usr/bin/env python3
"""
Integraatiotesti ELO-vertailulle
"""
import sys
import os
import json

# Korjattu import-polku
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
    from src.managers.elo_manager import ELOManager
except ImportError as e:
    print(f"❌ Import-virhe: {e}")
    sys.exit(1)

def test_elo_comparison():
    """Testaa ELO-vertailua"""
    print("🧪 Testataan ELO-vertailua...")
    
    try:
        # Lataa kysymykset
        with open("data/runtime/questions.json", "r", encoding='utf-8') as f:
            questions_data = json.load(f)
        
        if len(questions_data["questions"]) < 2:
            print("❌ Tarvitaan vähintään 2 kysymystä")
            return False
        
        # Näytä kysymykset
        print("\n📝 KYSYMYKSET:")
        for i, q in enumerate(questions_data["questions"][:2], 1):
            print(f"{i}. {q['content']['question']['fi']}")
            print(f"   ELO: {q['elo_rating']['current_rating']}")
        
        # Testaa ELO-päivitys
        elo_manager = ELOManager("Jumaltenvaalit2026")
        
        q1_id = questions_data["questions"][0]["local_id"]
        q2_id = questions_data["questions"][1]["local_id"]
        
        print(f"\n🔄 Vertaillaan: {q1_id} vs {q2_id}")
        print("💡 Valinta: 'a' (ensimmäinen kysymys voittaa)")
        
        result = elo_manager.update_ratings(q1_id, q2_id, "a")
        
        print("✅ ELO-päivitys onnistui!")
        print(f"📊 {q1_id}: {result['question_a']['old']} → {result['question_a']['new']} ({result['question_a']['delta']:+.0f})")
        print(f"📊 {q2_id}: {result['question_b']['old']} → {result['question_b']['new']} ({result['question_b']['delta']:+.0f})")
        
        return True
        
    except Exception as e:
        print(f"❌ ELO-vertailu epäonnistui: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_elo_comparison()
    sys.exit(0 if success else 1)
