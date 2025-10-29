#!/usr/bin/env python3
# update_base_templates_minimal.py

import json
from datetime import datetime
from pathlib import Path

def update_base_templates():
    """Päivitä kaikki base.json tiedostot minimaaliseen muotoon"""
    
    base_dir = Path("runtime")
    base_dir.mkdir(exist_ok=True)
    
    templates = {
        "candidates.base.json": {
            "metadata": {
                "version": "2.0.0",
                "created": "{{TIMESTAMP}}",
                "last_updated": "{{TIMESTAMP}}",
                "election_id": "{{ELECTION_ID}}",
                "description": {
                    "fi": "Ehdokkaiden perustiedot ja vastaukset",
                    "en": "Candidate information and answers", 
                    "sv": "Kandidatinformation och svar"
                }
            },
            "candidates": [
                {
                    "candidate_id": "{{CANDIDATE_ID}}",
                    "name": {
                        "fi": "{{FI_NAME}}",
                        "en": "{{EN_NAME}}",
                        "sv": "{{SV_NAME}}"
                    },
                    "party": "{{PARTY_ID}}",
                    "description": {
                        "fi": "{{FI_DESCRIPTION}}",
                        "en": "{{EN_DESCRIPTION}}",
                        "sv": "{{SV_DESCRIPTION}}"
                    },
                    "answers": [
                        {
                            "question_id": "{{QUESTION_ID}}",
                            "answer_value": 3,
                            "confidence": 3,
                            "explanations": {
                                "fi": "{{FI_EXPLANATION}}",
                                "en": "{{EN_EXPLANATION}}",
                                "sv": "{{SV_EXPLANATION}}"
                            },
                            "timestamp": "{{TIMESTAMP}}",
                            "version": 1
                        }
                    ],
                    "metadata": {
                        "submission_timestamp": "{{TIMESTAMP}}",
                        "last_updated": "{{TIMESTAMP}}",
                        "answers_hash": "{{ANSWERS_HASH}}",
                        "verification_tx": "{{VERIFICATION_TX}}"
                    }
                }
            ]
        },
        
        "questions.base.json": {
            "metadata": {
                "version": "2.0.0",
                "created": "{{TIMESTAMP}}",
                "last_updated": "{{TIMESTAMP}}", 
                "election_id": "{{ELECTION_ID}}",
                "description": {
                    "fi": "Kysymysten perusrakenteet",
                    "en": "Basic question structures",
                    "sv": "Grundläggande frågestrukturer"
                }
            },
            "questions": [
                {
                    "local_id": "{{QUESTION_ID}}",
                    "ipfs_cid": "{{IPFS_CID}}",
                    "source": "local",
                    "content": {
                        "category": {
                            "fi": "{{FI_CATEGORY}}",
                            "en": "{{EN_CATEGORY}}",
                            "sv": "{{SV_CATEGORY}}"
                        },
                        "question": {
                            "fi": "{{FI_QUESTION}}",
                            "en": "{{EN_QUESTION}}",
                            "sv": "{{SV_QUESTION}}"
                        },
                        "tags": ["{{TAG1}}", "{{TAG2}}"],
                        "scale": {
                            "min": -5,
                            "max": 5,
                            "labels": {
                                "fi": {
                                    "min": "Täysin eri mieltä",
                                    "neutral": "Neutraali",
                                    "max": "Täysin samaa mieltä"
                                },
                                "en": {
                                    "min": "Strongly disagree", 
                                    "neutral": "Neutral",
                                    "max": "Strongly agree"
                                },
                                "sv": {
                                    "min": "Helt avig",
                                    "neutral": "Neutral",
                                    "max": "Helt enig"
                                }
                            }
                        }
                    },
                    "elo_rating": {
                        "base_rating": 1000,
                        "current_rating": 1000,
                        "comparison_delta": 0,
                        "vote_delta": 0,
                        "total_comparisons": 0,
                        "total_votes": 0,
                        "up_votes": 0,
                        "down_votes": 0
                    },
                    "timestamps": {
                        "created_local": "{{TIMESTAMP}}",
                        "modified_local": "{{TIMESTAMP}}"
                    }
                }
            ]
        },
        
        "active_questions.base.json": {
            "metadata": {
                "election_id": "{{ELECTION_ID}}",
                "created": "{{TIMESTAMP}}",
                "last_updated": "{{TIMESTAMP}}",
                "question_limit": 15,
                "min_rating": 800,
                "sync_enabled": True,
                "submission_locked": False
            },
            "sync_rules": {
                "auto_sync": True,
                "sync_interval_hours": 24,
                "max_questions": 15,
                "min_comparisons": 5,
                "min_votes": 3,
                "rating_weight": 0.7,
                "activity_weight": 0.3
            },
            "questions": []
        }
    }
    
    print("🔄 PÄIVITETÄÄN BASE.JSON TIEDOSTOT MINIMAALISEEN MUOTOON...")
    
    for filename, template in templates.items():
        filepath = base_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        print(f"✅ {filename} päivitetty")
    
    print("🎯 KAIKKI BASE.JSON TIEDOSTOT PÄIVITETTY!")

if __name__ == "__main__":
    update_base_templates()
