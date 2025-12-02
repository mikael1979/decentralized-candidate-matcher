#!/usr/bin/env python3
"""
Yksinkertainen testi puolueen luomiselle ilman monimutkaisia importteja
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import os
import json
from datetime import datetime

def create_simple_party():
    """Luo yksinkertaisen testipuolueen"""
    print("🧪 Testataan puolueen luomista (yksinkertainen versio)...")
    
    try:
        parties_file = "data/runtime/parties.json"
        
        # Lataa nykyiset puolueet
        with open(parties_file, 'r', encoding='utf-8') as f:
            parties_data = json.load(f)
        
        # Luo testipuolue
        test_party = {
            "party_id": "party_test_001",
            "name": {
                "fi": "Testi Ukosen Jumalat",
                "en": "Test Thunder Gods", 
                "sv": "Test Åskgudar"
            },
            "description": {
                "fi": "Testi: Perinteiset ukkosen jumalat",
                "en": "Test: Traditional thunder gods",
                "sv": "Test: Traditionella åskgudar"
            },
            "crypto_identity": {
                "public_key": "test_public_key_12345",
                "key_fingerprint": "test_fingerprint_001",
                "foundation_document": {
                    "party_name": "Testi Ukosen Jumalat",
                    "founding_date": datetime.now().isoformat(),
                    "election_id": "Jumaltenvaalit2026",
                    "principles": "Testiperiaatteet"
                },
                "foundation_signature": "test_signature_12345"
            },
            "media_publications": [],
            "registration": {
                "proposed_by": "test_system",
                "proposed_at": datetime.now().isoformat(),
                "verification_status": "pending",
                "verification_phase": "key_publication",
                "verified_by_nodes": [],
                "media_verifications": [],
                "quorum_votes": [],
                "rejection_reason": None
            },
            "candidates": [],
            "metadata": {
                "contact_email": "test@olympus.fi",
                "website": "https://test.olympus.fi",
                "founding_year": "2025"
            }
        }
        
        # Lisää puolue
        parties_data['parties'].append(test_party)
        parties_data['metadata']['last_updated'] = datetime.now().isoformat()
        
        # Tallenna
        with open(parties_file, 'w', encoding='utf-8') as f:
            json.dump(parties_data, f, indent=2, ensure_ascii=False)
        
        print("✅ Testipuolue luotu onnistuneesti!")
        print(f"   Puolue ID: {test_party['party_id']}")
        print(f"   Nimi: {test_party['name']['fi']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Testipuolueen luonti epäonnistui: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_simple_party()
    sys.exit(0 if success else 1)
