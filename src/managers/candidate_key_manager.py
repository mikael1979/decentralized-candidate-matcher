#!/usr/bin/env python3
"""
Ehdokkaiden PKI-valtuutusten hallinta
"""
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict
from .crypto_manager import CryptoManager

class CandidateKeyManager:
    def __init__(self, election_id: str):
        self.election_id = election_id
        self.crypto = CryptoManager()
    
    def issue_candidate_credentials(self, party_id: str, candidate_id: str, 
                                  party_private_key: str, validity_days: int = 180) -> Dict:
        """Luo ehdokkaalle PKI-valtuutus"""
        
        # 1. Luo ehdokkaalle avainpari
        candidate_keys = self.crypto.generate_key_pair()
        
        # 2. Luo valtuutusasiakirja
        delegation_document = {
            "election_id": self.election_id,
            "party_id": party_id,
            "candidate_id": candidate_id,
            "delegated_powers": [
                "submit_answers", 
                "modify_answers", 
                "view_own_data",
                "update_profile"
            ],
            "valid_from": datetime.now().isoformat(),
            "valid_until": (datetime.now() + timedelta(days=validity_days)).isoformat(),
            "candidate_public_key": candidate_keys["public_key"],
            "candidate_key_fingerprint": candidate_keys["key_fingerprint"],
            "document_version": "1.0"
        }
        
        # 3. Allekirjoita valtuutus puolueen avaimella
        delegation_signature = self.crypto.sign_data(
            party_private_key,
            delegation_document
        )
        
        credentials = {
            "candidate_keys": candidate_keys,
            "delegation_document": delegation_document,
            "delegation_signature": delegation_signature,
            "party_verification": {
                "party_id": party_id,
                "verification_timestamp": datetime.now().isoformat(),
                "validity_days": validity_days
            }
        }
        
        return credentials
    
    def verify_candidate_authorization(self, candidate_id: str, 
                                    delegation_document: Dict, 
                                    delegation_signature: str,
                                    party_public_key: str) -> bool:
        """Varmista ehdokkaan valtuutus"""
        
        try:
            # 1. Tarkista puolueen allekirjoitus
            if not self.crypto.verify_signature(
                party_public_key, delegation_document, delegation_signature
            ):
                print("❌ Puolueen allekirjoitus epävalidi")
                return False
            
            # 2. Tarkista voimassaolo
            valid_until = datetime.fromisoformat(delegation_document["valid_until"])
            if datetime.now() > valid_until:
                print("❌ Valitus vanhentunut")
                return False
            
            # 3. Tarkista ehdokas-id
            if delegation_document["candidate_id"] != candidate_id:
                print("❌ Ehdokas-id ei täsmää")
                return False
            
            print("✅ Valituus validi")
            return True
            
        except Exception as e:
            print(f"❌ Valituuden tarkistusvirhe: {e}")
            return False
