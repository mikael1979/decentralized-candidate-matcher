#!/usr/bin/env python3
"""
Integraatiotesti kysymysten lisäämiselle
"""
import sys
import os
import json
from datetime import datetime

# Korjattu import-polku
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def add_test_questions():
    """Testaa kysymysten lisäämistä"""
    print("🧪 Testataan kysymysten lisäämistä...")
    
    try:
        questions_file = "data/runtime/questions.json"
        
        test_questions = [
            {
                "local_id": "q_001",
                "content": {
                    "category": "sky_thunder",
                    "question": {
                        "fi": "Pitääkö ukkosen jumalan osata hallita säätä?",
                        "en": "Should a thunder god be able to control weather?",
                        "sv": "Bör en åskgud kunna kontrollera vädret?"
                    },
                    "scale": {"min": -5, "max": 5}
                },
                "elo_rating": {
                    "base_rating": 1000,
                    "current_rating": 1000,
                    "comparison_delta": 0,
                    "vote_delta": 0
                },
                "timestamps": {
                    "created_local": datetime.now().isoformat(),
                    "modified_local": datetime.now().isoformat()
                }
            },
            {
                "local_id": "q_002", 
                "content": {
                    "category": "wisdom_warfare",
                    "question": {
                        "fi": "Onko viisauden jumalan tehtävä opettaa ihmiskuntaa?",
                        "en": "Should a wisdom god be responsible for teaching humanity?",
                        "sv": "Bör en vishetsgud vara ansvarig för att undervisa mänskligheten?"
                    },
                    "scale": {"min": -5, "max": 5}
                },
                "elo_rating": {
                    "base_rating": 1000,
                    "current_rating": 1000,
                    "comparison_delta": 0,
                    "vote_delta": 0
                },
                "timestamps": {
                    "created_local": datetime.now().isoformat(),
                    "modified_local": datetime.now().isoformat()
                }
            }
        ]
        
        # Lataa nykyiset kysymykset
        with open(questions_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Lisää testikysymykset
        data['questions'].extend(test_questions)
        data['metadata']['last_updated'] = datetime.now().isoformat()
        
        # Tallenna
        with open(questions_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print("✅ Kysymykset lisätty onnistuneesti!")
        for q in test_questions:
            print(f"   - {q['content']['question']['fi']}")
            
        return True
        
    except Exception as e:
        print(f"❌ Kysymysten lisäys epäonnistui: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = add_test_questions()
    sys.exit(0 if success else 1)
