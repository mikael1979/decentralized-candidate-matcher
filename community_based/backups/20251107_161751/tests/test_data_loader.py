# tests/test_data_loader.py - UUSI MODUULI
"""
Testidatan lataus erillisistä JSON-tiedostoista
"""

import json
from pathlib import Path

def load_test_questions():
    """Lataa testikysymykset JSON-tiedostosta"""
    test_file = Path("tests/test_questions.json")
    if test_file.exists():
        with open(test_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Luo oletustestidata jos tiedostoa ei ole
        default_data = {
            "test_questions": [
                {
                    "local_id": "test_q_1",
                    "content": {
                        "question": {
                            "fi": "Testikysymys 1 - Pitäisikö kaupunkipyöriä lisätä?",
                            "en": "Test question 1 - Should city bikes be increased?",
                            "sv": "Testfråga 1 - Bör stadscyklar ökas?"
                        },
                        "category": {
                            "fi": "Liikenne",
                            "en": "Transportation", 
                            "sv": "Transport"
                        }
                    },
                    "elo_rating": {
                        "base_rating": 1000,
                        "current_rating": 1000,
                        "comparison_delta": 0,
                        "vote_delta": 0
                    }
                }
            ]
        }
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, indent=2)
        return default_data

def load_test_candidates():
    """Lataa testiehdokkaat JSON-tiedostosta"""
    test_file = Path("tests/test_candidates.json")
    if test_file.exists():
        with open(test_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"test_candidates": []}
