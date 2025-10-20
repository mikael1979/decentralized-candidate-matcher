# candidate_registration.py
import json
import hashlib
from datetime import datetime
from typing import Dict, Any
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

class CandidateRegistration:
    def __init__(self, ipfs, election_manager):
        self.ipfs = ipfs
        self.election_manager = election_manager
    
    def generate_key_pair(self):
        """Luo uuden avainparin ehdokkaalle"""
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        # Serialisoi avaimet
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH
        )
        
        return {
            "private_key": private_bytes.decode(),
            "public_key": public_bytes.decode(),
            "key_fingerprint": self._calculate_fingerprint(public_bytes)
        }
    
    def register_candidate(self, candidate_data: Dict[str, Any], private_key: str) -> str:
        """Rekisteröi uuden ehdokkaan allekirjoituksella"""
        # Varmista pakolliset kentät
        required_fields = ["name", "party", "district"]
        for field in required_fields:
            if field not in candidate_data:
                raise ValueError(f"Pakollinen kenttä puuttuu: {field}")
        
        # Luo allekirjoitus
        signature = self._sign_data(candidate_data, private_key)
        
        # Lisää metadata
        candidate_data.update({
            "id": self._generate_candidate_id(),
            "public_key": self._extract_public_key(private_key),
            "key_fingerprint": self._calculate_fingerprint(self._extract_public_key(private_key).encode()),
            "registration_date": datetime.now().isoformat(),
            "verified": False,  # Yhteisö voi vahvistaa myöhemmin
            "signature": signature,
            "signed_data": json.dumps(candidate_data, sort_keys=True)
        })
        
        # Tallenna ehdokas
        cid = self.election_manager.add_candidate(candidate_data)
        print(f"✅ Ehdokas {candidate_data['name']} rekisteröity onnistuneesti!")
        print(f"📝 Ehdokas ID: {candidate_data['id']}")
        print(f"🔑 Julkinen avain: {candidate_data['public_key'][:50]}...")
        print(f"🆔 Avaintunniste: {candidate_data['key_fingerprint']}")
        
        return cid
    
    def verify_candidate_signature(self, candidate_data: Dict[str, Any]) -> bool:
        """Tarkistaa ehdokkaan allekirjoituksen"""
        try:
            public_key = serialization.load_ssh_public_key(
                candidate_data["public_key"].encode()
            )
            
            # Tarkista allekirjoitus
            public_key.verify(
                bytes.fromhex(candidate_data["signature"]),
                candidate_data["signed_data"].encode()
            )
            return True
        except Exception as e:
            print(f"Allekirjoituksen tarkistus epäonnistui: {e}")
            return False
    
    def _sign_data(self, data: Dict[str, Any], private_key_pem: str) -> str:
        """Allekirjoittaa datan yksityisellä avaimella"""
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None
        )
        
        data_to_sign = json.dumps(data, sort_keys=True).encode()
        signature = private_key.sign(data_to_sign)
        
        return signature.hex()
    
    def _extract_public_key(self, private_key_pem: str) -> str:
        """Poimia julkinen avain yksityisestä avaimesta"""
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None
        )
        public_key = private_key.public_key()
        
        return public_key.public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH
        ).decode()
    
    def _generate_candidate_id(self) -> int:
        """Generoi uniikin ehdokas-ID:n"""
        candidates_data = self.election_manager.get_election_data("candidates.json")
        existing_ids = [c["id"] for c in candidates_data.get("candidates", [])]
        
        return max(existing_ids) + 1 if existing_ids else 1
    
    def _calculate_fingerprint(self, public_key_bytes: bytes) -> str:
        """Laskee julkisen avaimen tunnisteen"""
        return hashlib.sha256(public_key_bytes).hexdigest()[:16]
