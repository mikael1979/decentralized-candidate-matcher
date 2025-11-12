#!/usr/bin/env python3
"""
Yksikkötestit CryptoManager:lle
"""
import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from src.managers.crypto_manager import CryptoManager

def test_key_generation():
    """Testaa avainparin generointia"""
    print("🔑 Testataan avainparin generointia...")
    
    crypto = CryptoManager()
    key_pair = crypto.generate_key_pair()
    
    assert "private_key" in key_pair
    assert "public_key" in key_pair  
    assert "key_fingerprint" in key_pair
    assert len(key_pair["key_fingerprint"]) == 16
    
    print("✅ Avainparin generointi onnistui!")

def test_signature_verification():
    """Testaa allekirjoituksen varmistusta"""
    print("📝 Testataan allekirjoituksen varmistusta...")
    
    crypto = CryptoManager()
    key_pair = crypto.generate_key_pair()
    
    test_data = {"test": "data", "timestamp": "2025-01-15"}
    signature = crypto.sign_data(key_pair["private_key"], test_data)
    
    # Varmista että allekirjoitus on validi
    is_valid = crypto.verify_signature(key_pair["public_key"], test_data, signature)
    assert is_valid == True
    
    # Varmista että väärä data ei mene läpi
    wrong_data = {"test": "wrong_data", "timestamp": "2025-01-15"}
    is_valid_wrong = crypto.verify_signature(key_pair["public_key"], wrong_data, signature)
    assert is_valid_wrong == False
    
    print("✅ Allekirjoituksen varmistus onnistui!")

if __name__ == "__main__":
    test_key_generation()
    test_signature_verification()
    print("🎉 Kaikki CryptoManager-testit läpäisty!")
