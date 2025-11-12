# src/managers/crypto_manager.py
import hashlib
import json
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from typing import Dict

class CryptoManager:
    def __init__(self):
        self.key_size = 2048
    
    def generate_key_pair(self) -> Dict:
        """Luo RSA-avainparin"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.key_size
        )
        
        public_key = private_key.public_key()
        
        # Serialisoi avaimet PEM-muotoon
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        return {
            "private_key": private_pem,
            "public_key": public_pem,
            "key_fingerprint": self.calculate_fingerprint(public_pem)
        }
    
    def calculate_fingerprint(self, public_key_pem: str) -> str:
        """Laske julkisen avaimen tunniste"""
        return hashlib.sha256(public_key_pem.encode()).hexdigest()[:16]
    
    def sign_data(self, private_key_pem: str, data: Dict) -> str:
        """Allekirjoita data yksityisellä avaimella"""
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None
        )
        
        signature = private_key.sign(
            json.dumps(data, sort_keys=True, ensure_ascii=False).encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return base64.b64encode(signature).decode('utf-8')
    
    def verify_signature(self, public_key_pem: str, data: Dict, signature: str) -> bool:
        """Varmista allekirjoitus"""
        try:
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode()
            )
            
            public_key.verify(
                base64.b64decode(signature),
                json.dumps(data, sort_keys=True, ensure_ascii=False).encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            print(f"Allekirjoituksen varmistusvirhe: {e}")
            return False
