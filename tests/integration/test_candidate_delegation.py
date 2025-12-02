#!/usr/bin/env python3
"""
Testaa ehdokasvaltuutusjärjestelmää - KORJATTU VERSIO
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import os
import json

sys.path.insert(0, os.path.abspath('.'))

try:
    from src.managers.candidate_key_manager import CandidateKeyManager
    from src.managers.crypto_manager import CryptoManager
except ImportError as e:
    print(f"Import-virhe: {e}")
    sys.exit(1)

def test_candidate_delegation():
    """Testaa ehdokkaan valtuutuksen luontia ja varmistusta"""
    print("🧪 Testataan ehdokasvaltuutusjärjestelmää...")
    
    try:
        # 1. Luo PUOLUEEN avainpari testiä varten
        crypto = CryptoManager()
        party_key_pair = crypto.generate_key_pair()
        
        party_id = "party_test_delegation"
        candidate_id = "cand_test_001"
        
        # 2. Luo ehdokasvaltuutus
        candidate_manager = CandidateKeyManager("Jumaltenvaalit2026")
        credentials = candidate_manager.issue_candidate_credentials(
            party_id=party_id,
            candidate_id=candidate_id,
            party_private_key=party_key_pair["private_key"],  # OIKEA YKSITYINEN AVAIN
            validity_days=90
        )
        
        print("✅ Ehdokasvaltuutus luotu!")
        print(f"   Ehdokas: {credentials['delegation_document']['candidate_id']}")
        print(f"   Puolue: {credentials['delegation_document']['party_id']}")
        print(f"   Voimassa: {credentials['delegation_document']['valid_until'][:10]}")
        
        # 3. Varmista valtuutus
        is_valid = candidate_manager.verify_candidate_authorization(
            candidate_id=candidate_id,
            delegation_document=credentials["delegation_document"],
            delegation_signature=credentials["delegation_signature"],
            party_public_key=party_key_pair["public_key"]  # OIKEA JULKINEN AVAIN
        )
        
        print(f"   Valituuden tila: {'✅ VALIDI' if is_valid else '❌ EPÄVALIDI'}")
        
        # 4. Tallenna testitulokset
        delegation_file = "test_delegation.json"
        with open(delegation_file, 'w') as f:
            json.dump({
                "credentials": credentials,
                "party_public_key": party_key_pair["public_key"],  # Säilytetään varmistusta varten
                "test_info": {
                    "party_id": party_id,
                    "candidate_id": candidate_id,
                    "generated_at": credentials['delegation_document']['valid_from']
                }
            }, f, indent=2)
        
        print(f"📁 Valituudet tallennettu: {delegation_file}")
        
        return is_valid
        
    except Exception as e:
        print(f"❌ Ehdokasvaltuutuksen testi epäonnistui: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_candidate_delegation()
    sys.exit(0 if success else 1)
