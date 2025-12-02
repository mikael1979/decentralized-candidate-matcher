#!/usr/bin/env python3
"""
Täysi PKI-testi puolueen luomiselle
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.abspath('.'))

# Suora import ilman src/__init__.py:n kautta
try:
    from src.managers.enhanced_party_manager import EnhancedPartyManager
except ImportError:
    # Vaihtoehtoinen tapa
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "enhanced_party_manager", 
        "src/managers/enhanced_party_manager.py"
    )
    party_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(party_module)
    EnhancedPartyManager = party_module.EnhancedPartyManager

def test_party_creation_pki():
    """Testaa puolueen luomista täydellä PKI:llä"""
    print("🧪 Testataan puolueen luomista täydellä PKI:llä...")
    
    try:
        manager = EnhancedPartyManager("Jumaltenvaalit2026")
        
        party_data = {
            "name": {
                "fi": "Olympos-jumalat",
                "en": "Olympian Gods", 
                "sv": "Olympiska gudar"
            },
            "description": {
                "fi": "Kreikkalaisten olympolaisten jumalten liitto",
                "en": "Alliance of Greek Olympian gods",
                "sv": "Allians av grekiska olympiska gudar"
            },
            "metadata": {
                "contact_email": "olympos@divine.fi",
                "website": "https://olympos.divine.fi",
                "founding_year": "2025"
            },
            "principles": "Jumalallisen vallan käyttö viisaasti ja vastuullisesti",
            "domain": "divine_power"
        }
        
        # Luo puolue PKI:llä
        new_party = manager.propose_party_with_keys(party_data)
        
        print("✅ Puolue luotu PKI:llä onnistuneesti!")
        print(f"   Puolue ID: {new_party['party_id']}")
        print(f"   Julkisen avaimen tunniste: {new_party['crypto_identity']['key_fingerprint']}")
        
        # Tarkista allekirjoitus
        is_signature_valid = manager.verify_party_signature(new_party)
        print(f"   Allekirjoituksen tila: {'✅ VALIDI' if is_signature_valid else '❌ EPÄVALIDI'}")
        
        # Tallenna testidata
        parties_file = 'data/runtime/parties.json'
        with open(parties_file, 'r', encoding='utf-8') as f:
            parties_data = json.load(f)
        
        parties_data['parties'].append(new_party)
        parties_data['metadata']['last_updated'] = datetime.now().isoformat()
        
        with open(parties_file, 'w', encoding='utf-8') as f:
            json.dump(parties_data, f, indent=2, ensure_ascii=False)
        
        return is_signature_valid
        
    except Exception as e:
        print(f"❌ PKI-puolueen luonti epäonnistui: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_party_creation_pki()
    sys.exit(0 if success else 1)
