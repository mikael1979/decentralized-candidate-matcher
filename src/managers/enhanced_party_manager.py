# src/managers/enhanced_party_manager.py
#!/usr/bin/env python3
"""
Erikoistoiminnallisuus Jumaltenvaaleille - Täysi PKI-toteutus
"""
from datetime import datetime, timedelta
from typing import Dict, List
import json
from .crypto_manager import CryptoManager

class EnhancedPartyManager:
    def __init__(self, election_id: str):
        self.election_id = election_id
        self.crypto = CryptoManager()
    
    def propose_party_with_keys(self, party_data: Dict) -> Dict:
        """Ehdotta uutta puoluetta täydellä PKI-tuella"""
        
        # 1. Luo avainpari
        key_pair = self.crypto.generate_key_pair()
        
        # 2. Luo perustamisdokumentti
        foundation_doc = {
            "party_name": party_data["name"]["fi"],
            "founding_date": datetime.now().isoformat(),
            "election_id": self.election_id,
            "principles": party_data.get("principles", ""),
            "domain": party_data.get("domain", "general")
        }
        
        # 3. Allekirjoita dokumentti
        signature = self.crypto.sign_data(
            key_pair["private_key"], 
            foundation_doc
        )
        
        # 4. Luo puolue
        party_id = f"party_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        enhanced_party = {
            "party_id": party_id,
            "name": party_data["name"],
            "description": party_data["description"],
            "crypto_identity": {
                "public_key": key_pair["public_key"],
                "key_fingerprint": key_pair["key_fingerprint"],
                "foundation_document": foundation_doc,
                "foundation_signature": signature,
                "key_algorithm": "RSA-2048",
                "signature_algorithm": "RSA-PSS-SHA256"
            },
            "media_publications": [],
            "registration": {
                "proposed_by": "system",
                "proposed_at": datetime.now().isoformat(),
                "verification_status": "pending",
                "verification_phase": "key_publication",
                "verified_by_nodes": [],
                "media_verifications": [],
                "quorum_votes": [],
                "rejection_reason": None
            },
            "candidates": [],
            "metadata": party_data.get("metadata", {})
        }
        
        return enhanced_party
    
    def verify_party_signature(self, party_data: Dict) -> bool:
        """Varmista puolueen perustamisdokumentin allekirjoitus"""
        try:
            crypto_id = party_data["crypto_identity"]
            return self.crypto.verify_signature(
                crypto_id["public_key"],
                crypto_id["foundation_document"],
                crypto_id["foundation_signature"]
            )
        except Exception as e:
            print(f"Puolueen allekirjoituksen varmistusvirhe: {e}")
            return False

    def publish_party_key_to_media(self, party_data: Dict, media_url: str) -> Dict:
        """Julkaise puolueen julkinen avain mediaan"""
        from .media_registry import MediaRegistry
        
        media_registry = MediaRegistry(self.election_id)
        
        publication = media_registry.register_media_publication(
            party_id=party_data["party_id"],
            party_name=party_data["name"]["fi"],
            public_key_fingerprint=party_data["crypto_identity"]["key_fingerprint"],
            media_url=media_url,
            publication_data={
                "party_name": party_data["name"]["fi"],
                "election": self.election_id,
                "public_key_fingerprint": party_data["crypto_identity"]["key_fingerprint"],
                "publication_date": datetime.now().strftime("%Y-%m-%d"),
                "verification_challenge": f"verify-{party_data['party_id']}"
            }
        )
        
        # Lisää julkaisu puolueen tietoihin
        if "media_publications" not in party_data:
            party_data["media_publications"] = []
        
        party_data["media_publications"].append(publication)
        
        return publication

    def complete_party_registration(self, party_data: Dict) -> Dict:
        """Suorita täydellinen puoluerekisteröinti PKI:llä"""
        from .quorum_manager import QuorumManager
        
        quorum_manager = QuorumManager(self.election_id)
        
        # 1. Alusta kvoorumivahvistus
        verification = quorum_manager.initialize_party_verification(party_data)
        
        # 2. Lisää puolueen tiedot
        party_data["registration"] = {
            "verification_process": verification,
            "status": "pending_quorum",
            "registration_timestamp": datetime.now().isoformat()
        }
        
        return party_data

    def get_party_verification_status(self, party_data: Dict) -> Dict:
        """Hae puolueen vahvistustila"""
        if "registration" not in party_data or "verification_process" not in party_data["registration"]:
            return {"status": "not_started"}
        
        from .quorum_manager import QuorumManager
        quorum_manager = QuorumManager(self.election_id)
        
        verification = party_data["registration"]["verification_process"]
        return quorum_manager.get_verification_status(verification)

    def add_media_verification_to_party(self, party_data: Dict, publication_record: Dict, node_id: str) -> bool:
        """Lisää mediavahvistus puolueelle"""
        if "registration" not in party_data or "verification_process" not in party_data["registration"]:
            return False
        
        from .quorum_manager import QuorumManager
        quorum_manager = QuorumManager(self.election_id)
        
        verification = party_data["registration"]["verification_process"]
        return quorum_manager.add_media_verification(verification, publication_record, node_id)

    def cast_vote_for_party(self, party_data: Dict, node_id: str, vote: str, 
                           node_public_key: str, justification: str = "") -> bool:
        """Äänestä puolueen hyväksymisestä"""
        if "registration" not in party_data or "verification_process" not in party_data["registration"]:
            return False
        
        from .quorum_manager import QuorumManager
        quorum_manager = QuorumManager(self.election_id)
        
        verification = party_data["registration"]["verification_process"]
        return quorum_manager.cast_vote(verification, node_id, vote, node_public_key, justification)
