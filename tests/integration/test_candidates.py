#!/usr/bin/env python3
"""
Integraatiotesti ehdokkaiden lisäämiselle
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import os
import json
from datetime import datetime

# Korjattu import-polku
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def add_test_candidates():
    """Testaa ehdokkaiden lisäämistä"""
    print("🧪 Testataan ehdokkaiden lisäämistä...")
    
    try:
        candidates_file = "data/runtime/candidates.json"
        
        test_candidates = [
            {
                "candidate_id": "cand_001",
                "basic_info": {
                    "name": {
                        "fi": "Zeus",
                        "en": "Zeus",
                        "sv": "Zeus"
                    },
                    "party": "party_001",
                    "domain": "sky_thunder"
                },
                "answers": []
            },
            {
                "candidate_id": "cand_002",
                "basic_info": {
                    "name": {
                        "fi": "Athena",
                        "en": "Athena", 
                        "sv": "Athena"
                    },
                    "party": "party_001",
                    "domain": "wisdom_warfare"
                },
                "answers": []
            }
        ]
        
        # Lataa nykyiset ehdokkaat
        with open(candidates_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Lisää testiehdokkaat
        data['candidates'].extend(test_candidates)
        data['metadata']['last_updated'] = datetime.now().isoformat()
        
        # Tallenna
        with open(candidates_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print("✅ Ehdokkaat lisätty onnistuneesti!")
        for c in test_candidates:
            print(f"   - {c['basic_info']['name']['fi']} ({c['candidate_id']})")
            
        return True
        
    except Exception as e:
        print(f"❌ Ehdokkaiden lisäys epäonnistui: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = add_test_candidates()
    sys.exit(0 if success else 1)
