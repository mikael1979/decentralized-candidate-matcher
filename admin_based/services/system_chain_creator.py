"""
System Chain Creator - Luo järjestelmäketjun asennuksen yhteydessä
"""
import json
import os
import hashlib
from datetime import datetime

def create_system_chain(election_id: str, system_id: str, version: str, private_key, use_prod_mode: bool = False) -> bool:
    """
    Luo system_chain.json tiedoston asennuksen yhteydessä
    """
    print("🔗 Luodaan järjestelmäketju...")
    
    # Kerää perustiedostojen fingerprintit
    fingerprints = {}
    files_to_check = ['questions.json', 'candidates.json', 'meta.json']
    
    for filename in files_to_check:
        filepath = os.path.join('data', filename)
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                fingerprints[filename] = hashlib.sha256(f.read()).hexdigest()
        else:
            # Jos tiedostoa ei ole, käytä tyhjän tiedoston hashia
            fingerprints[filename] = hashlib.sha256(b'').hexdigest()
    
    # Luo genesis-lohko
    genesis_block = {
        "block_id": 0,
        "timestamp": datetime.now().isoformat(),
        "description": "Alkutila asennuksen jälkeen",
        "files": fingerprints,
        "previous_hash": None
    }
    
    # Laske lohkon hash
    block_hash = hashlib.sha256(json.dumps(genesis_block, sort_keys=True).encode()).hexdigest()
    genesis_block["block_hash"] = f"sha256:{block_hash}"
    
    # Luo ketju
    chain = {
        "chain_id": election_id,
        "created_at": datetime.now().isoformat(),
        "description": "Fingerprint-ketju kaikille järjestelmän tiedostoille",
        "version": version,
        "blocks": [genesis_block],
        "current_state": fingerprints,
        "metadata": {
            "algorithm": "sha256",
            "system_id": system_id,
            "election_id": election_id
        }
    }
    
    # Tallenna
    os.makedirs('data', exist_ok=True)
    with open('data/system_chain.json', 'w', encoding='utf-8') as f:
        json.dump(chain, f, indent=2, ensure_ascii=False)
    
    print("✅ Järjestelmäketju luotu onnistuneesti")
    return True
