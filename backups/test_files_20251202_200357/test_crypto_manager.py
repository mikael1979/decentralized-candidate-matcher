#!/usr/bin/env python3
"""
Testaa täysi CryptoManager-toteutus
"""
import sys
import os

# Lisää src hakemisto Python-polkuun
sys.path.insert(0, os.path.abspath('.'))

# Käytetään suoraa importtia ilman src/__init__.py:n kautta kulkemista
try:
    from src.managers.crypto_manager import CryptoManager
except ImportError:
    # Vaihtoehtoinen tapa jos edelleen ongelmia
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "crypto_manager", 
        "src/managers/crypto_manager.py"
    )
    crypto_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(crypto_module)
    CryptoManager = crypto_module.CryptoManager

def test_crypto_manager():
    print("🧪 Testataan CryptoManager PKI-toimintoja...")
    
    crypto = CryptoManager()
    
    # 1. Testaa avaimen generointi
    print("1. 🔑 Testataan avaimen generointia...")
    key_pair = crypto.generate_key_pair()
    assert "private_key" in key_pair
    assert "public_key" in key_pair
    assert "key_fingerprint" in key_pair
    assert len(key_pair["key_fingerprint"]) == 16
    print("   ✅ Avaimen generointi toimii")
    
    # 2. Testaa allekirjoitus ja varmistus
    print("2. 📝 Testataan allekirjoitusta...")
    test_data = {"test": "data", "number": 42, "nested": {"field": "value"}}
    signature = crypto.sign_data(key_pair["private_key"], test_data)
    
    # Varmista että allekirjoitus on validi
    is_valid = crypto.verify_signature(key_pair["public_key"], test_data, signature)
    assert is_valid == True
    print("   ✅ Allekirjoitus ja varmistus toimii")
    
    # 3. Testaa että väärä data ei mene läpi
    print("3. ❌ Testataan väärää dataa...")
    wrong_data = {"test": "wrong_data", "number": 42}
    is_valid_wrong = crypto.verify_signature(key_pair["public_key"], wrong_data, signature)
    assert is_valid_wrong == False
    print("   ✅ Väärän datan tunnistus toimii")
    
    # 4. Testaa että väärä allekirjoitus ei mene läpi
    print("4. ❌ Testataan väärää allekirjoitusta...")
    fake_signature = "fake" + signature[4:]
    is_valid_fake = crypto.verify_signature(key_pair["public_key"], test_data, fake_signature)
    assert is_valid_fake == False
    print("   ✅ Väärän allekirjoituksen tunnistus toimii")
    
    print("🎉 Kaikki CryptoManager-testit läpäisty!")
    return True

if __name__ == "__main__":
    success = test_crypto_manager()
    sys.exit(0 if success else 1)
