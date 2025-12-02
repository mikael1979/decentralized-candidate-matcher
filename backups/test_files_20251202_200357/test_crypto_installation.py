# test_crypto_installation.py
#!/usr/bin/env python3
"""
Testaa cryptography-kirjaston asennuksen
"""
try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import hashes
    print("✅ cryptography-kirjasto toimii!")
    
    # Testaa avaimen generointi
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    
    # Testaa serialisointi
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    print("✅ RSA-avaimen serialisointi toimii!")
    
    # Testaa julkinen avain
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    print("✅ Julkisen avaimen serialisointi toimii!")
    
    print("🎉 Kaikki cryptography-testit läpäisty!")
    
except ImportError as e:
    print(f"❌ cryptography-kirjasto puuttuu: {e}")
except Exception as e:
    print(f"❌ Virhe cryptography-testissä: {e}")
    import traceback
    traceback.print_exc()
