# test_wrong_key.py
#!/usr/bin/env python3
"""
Testaa että väärä avain hylätään
"""
import sys
import os
import json

sys.path.insert(0, os.path.abspath('.'))

from src.managers.candidate_key_manager import CandidateKeyManager
from src.managers.crypto_manager import CryptoManager

def test_wrong_key_rejection():
    """Testaa että väärä puolueen avain hylätään"""
    print("🧪 Testataan väärän avaimen hylkäämistä...")
    
    crypto = CryptoManager()
    
    # 1. Luo oikea puolueavain
    correct_party_keys = crypto.generate_key_pair()
    
    # 2. Luo väärä puolueavain
    wrong_party_keys = crypto.generate_key_pair()
    
    candidate_manager = CandidateKeyManager("Jumaltenvaalit2026")
    
    # 3. Luo valtuutus oikealla avaimella
    credentials = candidate_manager.issue_candidate_credentials(
        party_id="party_test",
        candidate_id="cand_test",
        party_private_key=correct_party_keys["private_key"],
        validity_days=90
    )
    
    # 4. Yritä varmistaa VÄÄRÄLLÄ avaimella
    is_valid_wrong = candidate_manager.verify_candidate_authorization(
        candidate_id="cand_test",
        delegation_document=credentials["delegation_document"],
        delegation_signature=credentials["delegation_signature"],
        party_public_key=wrong_party_keys["public_key"]  # VÄÄRÄ AVAIN!
    )
    
    # 5. Varmista OIKEALLA avaimella
    is_valid_correct = candidate_manager.verify_candidate_authorization(
        candidate_id="cand_test",
        delegation_document=credentials["delegation_document"],
        delegation_signature=credentials["delegation_signature"],
        party_public_key=correct_party_keys["public_key"]  # OIKEA AVAIN
    )
    
    print(f"✅ Väärällä avaimella: {'HYLÄTTY' if not is_valid_wrong else 'HYVÄKSYTTY'}")
    print(f"✅ Oikealla avaimella: {'HYVÄKSYTTY' if is_valid_correct else 'HYLÄTTY'}")
    
    success = (not is_valid_wrong) and is_valid_correct
    print(f"🎯 Testin tulos: {'✅ ONNISTUI' if success else '❌ EPÄONNISTUI'}")
    
    return success

if __name__ == "__main__":
    success = test_wrong_key_rejection()
    sys.exit(0 if success else 1)
