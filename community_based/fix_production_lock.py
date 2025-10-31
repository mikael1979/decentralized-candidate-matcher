# fix_production_lock.py
#!/usr/bin/env python3
"""
Korjaa tuotantolukituksen ongelma
"""

import json
from datetime import datetime
from pathlib import Path

def fix_production_lock():
    print("🔧 KORJATAAN TUOTANTOLUKITUS...")
    
    # 1. Tarkista onko lohkometadata olemassa
    from mock_ipfs import MockIPFS
    from ipfs_block_manager import IPFSBlockManager
    
    ipfs = MockIPFS()
    block_manager = IPFSBlockManager(ipfs, 'Jumaltenvaalit_2026', 'main_node')
    
    try:
        metadata = block_manager._load_blocks_metadata()
        print(f"✅ Lohkometadata löytyy: {metadata.get('blocks_metadata_cid', 'unknown')}")
        return True
    except Exception as e:
        print(f"❌ Lohkometadataa ei löydy: {e}")
        print("🌐 Alustetaan lohkot uudelleen...")
        
        # Alusta lohkot
        metadata_cid = block_manager.initialize_blocks()
        print(f"✅ Lohkot alustettu uudelleen: {metadata_cid}")
        
        # Varmista että metadata latautuu
        try:
            metadata = block_manager._load_blocks_metadata()
            print(f"✅ Lohkometadata varmistettu: {metadata.get('blocks_metadata_cid', 'unknown')}")
            return True
        except Exception as e2:
            print(f"❌ Edelleen ongelma: {e2}")
            return False

def create_simple_lock():
    """Luo yksinkertainen tuotantolukitus ilman IPFS:ää"""
    print("🔒 LUODAAN YKSINKERTAINEN TUOTANTOLUKITUS...")
    
    lock_file = Path("runtime/production.lock")
    fingerprint_file = Path("runtime/file_fingerprints.json")
    
    # Lataa nykyinen fingerprint-rekisteri
    from enhanced_integrity_manager import EnhancedIntegrityManager
    integrity = EnhancedIntegrityManager("development")
    registry = integrity.generate_fingerprint_registry()
    registry["metadata"]["locked_for_production"] = datetime.now().isoformat()
    registry["metadata"]["mode"] = "production"
    
    # Tallenna fingerprintit
    with open(fingerprint_file, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    print(f"✅ Fingerprint-rekisteri tallennettu: {len(registry['modules'])} moduulia")
    
    # Luo lukkotiedosto
    lock_data = {
        "production_locked": True,
        "locked_at": datetime.now().isoformat(),
        "fingerprint_cid": "local_only",
        "total_modules": len(registry['modules']),
        "election_id": "Jumaltenvaalit_2026",
        "method": "simple_lock"
    }
    
    with open(lock_file, 'w', encoding='utf-8') as f:
        json.dump(lock_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Tuotantolukitus luotu: {lock_file}")
    print("🎯 Järjestelmä on nyt tuotantotilassa!")
    
    return True

if __name__ == "__main__":
    print("🚀 TUOTANTOLUKITUKSEN KORJAUS")
    print("=" * 50)
    
    # Yritä ensin korjata IPFS-lohkot
    if not fix_production_lock():
        print("\n🔄 Käytetään yksinkertaista lukitusta...")
        create_simple_lock()
    
    print("\n💡 Testaa tuotantotila:")
    print("python system_bootstrap.py")
    print("python security_test.py")
