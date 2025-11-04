try:
    import base58
    import aiohttp
    import asyncio
    import json
    import hashlib
    from datetime import datetime
    
    print("✅ Kaikki kirjastot ladattu onnistuneesti!")
    print(f"base58 versio: {base58.__version__}")
    
    # Testaa base58-toimintoa
    test_bytes = b"test data for ipfs"
    encoded = base58.b58encode(test_bytes)
    decoded = base58.b58decode(encoded)
    
    print(f"✅ Base58 encoding toimii: {test_bytes == decoded}")
    
    # Testaa SHA256-toimintoa
    test_data = b"test content for hash"
    hash_result = hashlib.sha256(test_data).hexdigest()
    print(f"✅ SHA256 hash toimii: {hash_result[:16]}...")
    
    # Testaa JSON-toimintoa
    test_json = {"name": "test", "value": 123}
    json_str = json.dumps(test_json)
    parsed_back = json.loads(json_str)
    print(f"✅ JSON käsittely toimii: {test_json == parsed_back}")
    
    print("🎉 Kaikki testit läpäisty! MockIPFS voi nyt käyttää base58:aa.")
    
except ImportError as e:
    print(f"❌ Virhe: {e}")
    print("Tarkista että virtuaaliympäristö on aktivoitu ja kirjastot asennettu")
