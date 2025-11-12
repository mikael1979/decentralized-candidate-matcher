#!/usr/bin/env python3
"""
Integraatiotesti vastausten lisäämiselle
"""
import sys
import os
import json
from datetime import datetime

# Korjattu import-polku
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def test_answer_submission():
    """Testaa vastausten lisäämistä"""
    print("🧪 Testataan vastausten lisäämistä...")
    
    try:
        candidates_file = "data/runtime/candidates.json"
        questions_file = "data/runtime/questions.json"
        
        # Lataa data
        with open(candidates_file, 'r', encoding='utf-8') as f:
            candidates_data = json.load(f)
        
        with open(questions_file, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
        
        if not candidates_data["candidates"] or not questions_data["questions"]:
            print("❌ Tarvitaan ehdokkaita ja kysymyksiä")
            return False
        
        # Valitse ensimmäinen ehdokas ja kysymys
        candidate = candidates_data["candidates"][0]
        question = questions_data["questions"][0]
        
        # Lisää vastaus
        new_answer = {
            "question_id": question["local_id"],
            "answer_value": 5,
            "confidence": 5,
            "explanation": {
                "fi": "Totta kai ukkosen jumalan täytyy hallita säätä!",
                "en": "Of course a thunder god must control weather!",
                "sv": "Naturligtvis måste en åskgud kontrollera vädret!"
            },
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        if "answers" not in candidate:
            candidate["answers"] = []
        
        candidate["answers"].append(new_answer)
        
        # Tallenna
        with open(candidates_file, 'w', encoding='utf-8') as f:
            json.dump(candidates_data, f, indent=2, ensure_ascii=False)
        
        print("✅ Vastaus lisätty onnistuneesti!")
        print(f"👤 Ehdokas: {candidate['basic_info']['name']['fi']}")
        print(f"❓ Kysymys: {question['content']['question']['fi']}")
        print(f"📊 Vastaus: {new_answer['answer_value']}/5")
        print(f"💬 Perustelu: {new_answer['explanation']['fi']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Vastausten lisäys epäonnistui: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_answer_submission()
    sys.exit(0 if success else 1)
