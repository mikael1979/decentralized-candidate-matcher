import os
import hashlib
import secrets
import json
from datetime import datetime
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

def generate_keys() -> tuple:
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    system_id = hashlib.sha256(public_bytes).hexdigest()[:16]
    return private_key, public_key, system_id

def save_keys(private_key, public_key, password: str, system_id: str, election_id: str, admin_username: str):
    os.makedirs('keys', exist_ok=True)
    
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(password.encode())
    )
    with open('keys/private_key.pem', 'wb') as f:
        f.write(private_pem)

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open('keys/public_key.pem', 'wb') as f:
        f.write(public_pem)

    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    
    system_info = {
        "system_id": system_id,
        "created": datetime.now().isoformat(),
        "key_algorithm": "RSA-2048",
        "password_salt": salt,
        "password_hash": password_hash,
        "key_fingerprint": hashlib.sha256(public_pem).hexdigest(),
        "election_id": election_id,
        "admin_username": admin_username
    }
    with open('keys/system_info.json', 'w', encoding='utf-8') as f:
        json.dump(system_info, f, indent=2, ensure_ascii=False)
    
    print("✅ Avaimet tallennettu")
