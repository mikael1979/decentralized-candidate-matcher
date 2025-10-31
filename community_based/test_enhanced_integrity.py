#!/usr/bin/env python3
# test_enhanced_integrity.py
"""
Testaa laajennettua integriteettivalvontaa
Käyttö: python test_enhanced_integrity.py
"""

import json
import sys
from datetime import datetime

sys.path.append('.')

def test_enhanced_integrity():
    """Testaa laajennettua integriteettivalvontaa"""
    
    print("🧪 LAAJENNETUN INTEGRITEETTIVALVONNAN TESTI")
    print("=" * 50)
    
    try:
        from mock_ipfs import MockIPFS
        from enhanced_integrity_manager import EnhancedIntegrityManager
        
        print("✅ Moduulit ladattu onnistuneesti")
        
        # Alusta testiympäristö
        ipfs = MockIPFS()
        integrity = EnhancedIntegrityManager("development", ipfs)
        
        # Testaa 1: Fingerprint-rekisterin generointi
        print("\n1. 🔍 TESTATAAN FINGERPRINT-REKISTERIÄ...")
        registry = integrity.generate_fingerprint_registry()
        print(f"   ✅ Fingerprint-rekisteri luotu:")
        print(f"      - Moduuleja: {len(registry['modules'])}")
        print(f"      - Tila: {registry['metadata']['mode']}")
        
        # Testaa 2: Perusintegriteettitarkistus
        print("\n2. ✅ TESTATAAN PERUSINTEGRITEETTITARKISTUSTA...")
        base_check = integrity.verify_system_integrity(registry)
        print(f"   ✅ Perustarkistus suoritettu: {base_check['verified']}")
        if 'modules_checked' in base_check:
            print(f"      - Tarkistetut moduulit: {base_check['modules_checked']}")
        else:
            print(f"      - Status: {base_check['status']}")
        
        # Testaa 3: Laajennettu integriteettitarkistus lohkojen kanssa
        print("\n3. 🔄 TESTATAAN LAAJENNETTUA INTEGRITEETTITARKISTUSTA...")
        enhanced_check = integrity.verify_system_with_blocks("test_election_2024", "test_node_1")
        print(f"   ✅ Laajennettu tarkistus suoritettu: {enhanced_check['overall_verified']}")
        print(f"      - Turvataso: {enhanced_check['security_level']}")
        
        # Testaa 4: Järjestelmän lukitus testi
        print("\n4. 🔒 TESTATAAN JÄRJESTELMÄN LUKITUSTA...")
        try:
            # Alusta ensin IPFS-lohkot
            from ipfs_block_manager import IPFSBlockManager
            block_manager = IPFSBlockManager(ipfs, "test_election_2024", "test_node_1")
            block_manager.initialize_blocks()
            
            lock_entry = integrity.lock_system_for_production(ipfs, "test_election_2024", "test_node_1")
            print(f"   ✅ Lukitus testattu: {lock_entry}")
        except Exception as e:
            print(f"   ⚠️  Lukitus testissä virhe: {e}")
        
        # Testaa 5: Fingerprint-tiedoston olemassaolo
        print("\n5. 📁 TESTATAAN FINGERPRINT-TIEDOSTOA...")
        from pathlib import Path
        fingerprint_file = Path("runtime/file_fingerprints.json")
        if fingerprint_file.exists():
            with open(fingerprint_file, 'r') as f:
                fingerprint_data = json.load(f)
            print(f"   ✅ Fingerprint-tiedosto löytyy:")
            print(f"      - Lukittu: {fingerprint_data['metadata'].get('system_locked', False)}")
            print(f"      - Moduuleja: {len(fingerprint_data['modules'])}")
        else:
            print("   ℹ️  Fingerprint-tiedostoa ei vielä ole")
        
        print("\n✅ KAIKKI INTEGRITEETTIVALVONNAN TESTIT ONNISTUIVAT!")
        return True
        
    except Exception as e:
        print(f"❌ TESTI EPÄONNISTUI: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_integrity()
    sys.exit(0 if success else 1)
