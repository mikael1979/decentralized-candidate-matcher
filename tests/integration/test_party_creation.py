#!/usr/bin/env python3
"""
Integraatiotesti puolueen luomiselle PKI:llä
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import os
import json

# Korjattu import-polku
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
    from src.managers.enhanced_party_manager import EnhancedPartyManager
    from src.managers.crypto_manager import CryptoManager
except ImportError as e:
    print(f"❌ Import-virhe: {e}")
    sys.exit(1)

def test_party_creation():
    """Testaa puolueen luomista julkisella avaimella"""
    print("🧪 Testataan puolueen luomista PKI:llä...")
    
    try:
        manager = EnhancedPartyManager("Jumaltenvaalit2026")
        
        party_data = {
            "name": {
                "fi": "Ukosen Jumalat",
                "en": "Thunder Gods",
                "sv": "Åskgudar"
            },
            "description": {
                "fi": "Perinteiset ukkosen ja salaman jumalat",
                "en": "Traditional thunder and lightning gods", 
                "sv": "Traditionella åska- och blixtgudar"
            },
            "metadata": {
                "contact_email": "ukonen@olympus.fi",
                "website": "https://ukosenjumalat.olympus.fi",
                "founding_year": "2025"
            },
            "principles": "Ukkosen ja salaman hallinta vastuullisesti"
        }
        
        new_party = manager.propose_party_with_keys(party_data)
        
        print("✅ Puolue luotu onnistuneesti!")
        print(f"   Puolue ID: {new_party['party_id']}")
        print(f"   Julkisen avaimen tunniste: {new_party['crypto_identity']['key_fingerprint']}")
        
        # Tallenna testidata
        parties_file = 'data/runtime/parties.json'
        with open(parties_file, 'r', encoding='utf-8') as f:
            parties_data = json.load(f)
        
        parties_data['parties'].append(new_party)
        parties_data['metadata']['last_updated'] = new_party['crypto_identity']['foundation_document']['founding_date']
        
        with open(parties_file, 'w', encoding='utf-8') as f:
            json.dump(parties_data, f, indent=2, ensure_ascii=False)
        
        return True
        
    except Exception as e:
        print(f"❌ Puolueen luonti epäonnistui: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_party_creation()
    sys.exit(0 if success else 1)
