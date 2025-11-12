# src/managers/secure_answer_manager.py
#!/usr/bin/env python3
"""
Turvallinen vastausjärjestelmä PKI-allekirjoituksilla
"""
import json
import hashlib
from datetime import datetime
from typing import Dict, List
from .candidate_key_manager import CandidateKeyManager
from .crypto_manager import CryptoManager

class SecureAnswerManager:
    def __init__(self, election_id: str):
        self.election_id = election_id
        self.crypto = CryptoManager()
        self.key_manager = CandidateKeyManager(election_id)
    
    def submit_signed_answer(self, candidate_id: str, question_id: str,
                           answer_data: Dict, candidate_private_key: str,
                           delegation_document: Dict, delegation_signature: str,
                           party_public_key: str) -> Dict:
        """Lähetä ehdokkaan allekirjoitettu vastaus"""
        
        # 1. Varmista valtuutus
        if not self.key_manager.verify_candidate_authorization(
            candidate_id, delegation_document, delegation_signature, party_public_key
        ):
            raise PermissionError("Ehdokkaalla ei ole voimassa olevaa valtuutusta")
        
        # 2. Validoi vastaus
        if not self._validate_answer_data(answer_data):
            raise ValueError("Virheellinen vastausdata")
        
        # 3. Luo vastausdokumentti
        answer_document = {
            "election_id": self.election_id,
            "candidate_id": candidate_id,
            "question_id": question_id,
            "answer_value": answer_data["answer_value"],
            "confidence": answer_data.get("confidence", 3),
            "explanation": answer_data.get("explanation", {}),
            "submission_timestamp": datetime.now().isoformat(),
            "document_version": "1.0",
            "previous_answer_hash": self._get_previous_answer_hash(candidate_id, question_id)
        }
        
        # 4. Allekirjoita vastaus
        answer_signature = self.crypto.sign_data(
            candidate_private_key,
            answer_document
        )
        
        # 5. Tallenna turvallisesti
        secure_answer = {
            "answer_document": answer_document,
            "answer_signature": answer_signature,
            "delegation_chain": {
                "delegation_document": delegation_document,
                "delegation_signature": delegation_signature,
                "party_public_key": party_public_key
            },
            "metadata": {
                "submission_id": self._generate_submission_id(candidate_id, question_id),
                "integrity_verified": True,
                "verification_timestamp": datetime.now().isoformat(),
                "hash_chain": self._calculate_hash_chain(answer_document, answer_signature)
            }
        }
        
        return secure_answer
    
    def verify_answer_integrity(self, secure_answer: Dict) -> bool:
        """Tarkista vastauksen eheys koko ketjussa"""
        
        try:
            answer_doc = secure_answer["answer_document"]
            delegation = secure_answer["delegation_chain"]
            
            # 1. Tarkista ehdokkaan allekirjoitus
            candidate_public_key = delegation["delegation_document"]["candidate_public_key"]
            if not self.crypto.verify_signature(
                candidate_public_key,
                answer_doc,
                secure_answer["answer_signature"]
            ):
                print("❌ Ehdokkaan allekirjoitus epävalidi")
                return False
            
            # 2. Tarkista puolueen valtuutus
            if not self.key_manager.verify_candidate_authorization(
                answer_doc["candidate_id"],
                delegation["delegation_document"],
                delegation["delegation_signature"],
                delegation["party_public_key"]
            ):
                print("❌ Puolueen valtuutus epävalidi")
                return False
            
            # 3. Tarkista hash-ketju
            expected_hash = self._calculate_hash_chain(
                answer_doc, secure_answer["answer_signature"]
            )
            if secure_answer["metadata"]["hash_chain"] != expected_hash:
                print("❌ Hash-ketju epävalidi")
                return False
            
            print("✅ Vastauksen eheys varmistettu")
            return True
            
        except Exception as e:
            print(f"❌ Vastauksen eheystarkistusvirhe: {e}")
            return False
    
    def _validate_answer_data(self, answer_data: Dict) -> bool:
        """Validoi vastausdata"""
        if "answer_value" not in answer_data:
            return False
        
        if not (-5 <= answer_data["answer_value"] <= 5):
            return False
        
        if "confidence" in answer_data and not (1 <= answer_data["confidence"] <= 5):
            return False
        
        return True
    
    def _generate_submission_id(self, candidate_id: str, question_id: str) -> str:
        """Generoi yksilöllinen vastaus-ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        content = f"{candidate_id}_{question_id}_{timestamp}"
        return f"ans_{hashlib.sha256(content.encode()).hexdigest()[:16]}"
    
    def _calculate_hash_chain(self, answer_document: Dict, signature: str) -> str:
        """Laske vastauksen hash-ketju"""
        content = json.dumps(answer_document, sort_keys=True) + signature
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _get_previous_answer_hash(self, candidate_id: str, question_id: str) -> str:
        """Hae edellisen vastauksen tiiviste (yksinkertaistettu)"""
        # Toteutus riippuu data-tallennuksesta
        return "initial"
