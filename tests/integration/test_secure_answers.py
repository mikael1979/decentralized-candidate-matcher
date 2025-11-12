# tests/integration/test_secure_answers.py
#!/usr/bin/env python3
"""
Testaa turvallista vastausjärjestelmää
"""
import sys
import os
import json

sys.path.insert(0, os.path.abspath('.'))

try:
    from src.managers.secure_answer_manager import SecureAnswerManager
    from src.managers.candidate_key_manager import CandidateKeyManager
    from src.managers.crypto_manager import CryptoManager
except ImportError as e:
    print(f"Import-virhe: {e}")
    sys.exit(1)

def test_secure_answers():
    """Testaa allekirjoitettujen vastausten luontia ja varmistusta"""
    print("🧪 Testataan turvallista vastausjärjestelmää...")
    
    try:
        # 1. Luo testiavaimet
        crypto = CryptoManager()
        party_keys = crypto.generate_key_pair()
        candidate_manager = CandidateKeyManager("Jumaltenvaalit2026")
        
        # 2. Luo ehdokasvaltuutus
        credentials = candidate_manager.issue_candidate_credentials(
            party_id="party_secure_test",
            candidate_id="cand_secure_001", 
            party_private_key=party_keys["private_key"],
            validity_days=90
        )
        
        candidate_keys = credentials["candidate_keys"]
        
        # 3. Luo turvallinen vastaus
        answer_manager = SecureAnswerManager("Jumaltenvaalit2026")
        
        answer_data = {
            "answer_value": 4,
            "confidence": 5,
            "explanation": {
                "fi": "Täysin samaa mieltä - tämä on tärkeä kysymys",
                "en": "Completely agree - this is an important question",
                "sv": "Helt överens - detta är en viktig fråga"
            }
        }
        
        secure_answer = answer_manager.submit_signed_answer(
            candidate_id="cand_secure_001",
            question_id="q_test_001",
            answer_data=answer_data,
            candidate_private_key=candidate_keys["private_key"],
            delegation_document=credentials["delegation_document"],
            delegation_signature=credentials["delegation_signature"],
            party_public_key=party_keys["public_key"]
        )
        
        print("✅ Turvallinen vastaus luotu!")
        print(f"   Vastaus-ID: {secure_answer['metadata']['submission_id']}")
        print(f"   Arvo: {secure_answer['answer_document']['answer_value']}/5")
        print(f"   Varmuus: {secure_answer['answer_document']['confidence']}/5")
        
        # 4. Varmista vastauksen eheys
        is_valid = answer_manager.verify_answer_integrity(secure_answer)
        print(f"   Vastauksen eheys: {'✅ VALIDI' if is_valid else '❌ EPÄVALIDI'}")
        
        # 5. Testaa väärä vastaus
        print("\n🧪 Testataan väärää vastausta...")
        tampered_answer = secure_answer.copy()
        tampered_answer["answer_document"]["answer_value"] = 5  # Muuta arvoa
        
        is_tampered_valid = answer_manager.verify_answer_integrity(tampered_answer)
        print(f"   Väärän vastauksen eheys: {'❌ HYVÄKSYTTY (VIRHE!)' if is_tampered_valid else '✅ HYLÄTTY'}")
        
        # 6. Tallenna testitulokset
        secure_file = "test_secure_answer.json"
        with open(secure_file, 'w') as f:
            json.dump({
                "secure_answer": secure_answer,
                "test_info": {
                    "candidate_id": "cand_secure_001",
                    "question_id": "q_test_001", 
                    "generated_at": secure_answer['answer_document']['submission_timestamp']
                }
            }, f, indent=2)
        
        print(f"📁 Turvallinen vastaus tallennettu: {secure_file}")
        
        success = is_valid and not is_tampered_valid
        return success
        
    except Exception as e:
        print(f"❌ Turvallisen vastauksen testi epäonnistui: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_secure_answers()
    sys.exit(0 if success else 1)
