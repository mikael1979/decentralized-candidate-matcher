#!/usr/bin/env python3
# test_ipfs_blocks.py
"""
Testaa IPFS-lohkojen toimintaa
Käyttö: python test_ipfs_blocks.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Lisää polku jotta moduulit löytyvät
sys.path.append('.')

def test_ipfs_blocks():
    """Testaa IPFS-lohkojen perustoimintoja"""
    
    print("🧪 IPFS LOHKOJEN TESTI")
    print("=" * 50)
    
    try:
        # Testaa että tarvittavat moduulit löytyvät
        from mock_ipfs import MockIPFS
        from ipfs_block_manager import IPFSBlockManager
        
        print("✅ Moduulit ladattu onnistuneesti")
        
        # Alusta testiympäristö
        ipfs = MockIPFS()
        manager = IPFSBlockManager(ipfs, "test_election_2024", "test_node_1")
        
        # Testaa 1: Lohkojen alustus
        print("\n1. 🔄 TESTATAAN LOHKOJEN ALUSTUSTA...")
        metadata_cid = manager.initialize_blocks()
        print(f"   ✅ Lohkot alustettu: {metadata_cid}")
        
        # Testaa 2: Kirjoitus aktiiviseen lohkoon
        print("\n2. 📝 TESTATAAN KIRJOITUSTA...")
        test_data = {"action": "test_write", "value": 42, "timestamp": datetime.now().isoformat()}
        entry_id = manager.write_to_block("active", test_data, "test_entry")
        print(f"   ✅ Kirjoitettu: {entry_id}")
        
        # Testaa 3: Lukeminen lohkosta
        print("\n3. 📖 TESTATAAN LUKEMISTA...")
        entries = manager.read_from_block("active")
        print(f"   ✅ Luettu {len(entries)} merkintää")
        
        # Testaa 4: Lohkon status
        print("\n4. 📊 TESTATAAN STATUSTA...")
        status = manager.get_block_status("active")
        print(f"   ✅ Status: {status['current_entries']}/{status['max_size']} merkintää")
        
        # Testaa 5: Useita kirjoituksia
        print("\n5. 🔄 TESTATAAN USEITA KIRJOITUKSIA...")
        for i in range(3):
            data = {"action": f"multi_write_{i}", "value": i}
            entry_id = manager.write_to_block("active", data, f"multi_test_{i}")
            print(f"   ✅ Kirjoitettu {i+1}/3")
        
        # Testaa 6: Uuden noden rekisteröinti
        print("\n6. 🔗 TESTATAAN NODEN REKISTERÖINTIÄ...")
        success = manager.register_new_node("test_node_2")
        print(f"   ✅ Uusi node rekisteröity: {success}")
        
        # Lopetustilasto
        final_status = manager.get_block_status()
        print(f"\n🎯 LOPPUTILA:")
        for block, info in final_status.items():
            print(f"   {block}: {info['entries']}/{info['max_size']} ({info['purpose']})")
        
        print("\n✅ KAIKKI IPFS-LOHKOTESTIT ONNISTUIVAT!")
        return True
        
    except Exception as e:
        print(f"❌ TESTI EPÄONNISTUI: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ipfs_blocks()
    sys.exit(0 if success else 1)
