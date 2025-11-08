# complete_initialization.py
#!/usr/bin/env python3
"""
Täydellinen järjestelmän alustus tuotantokäyttöön
"""

from mock_ipfs import MockIPFS
from ipfs_block_manager import IPFSBlockManager
from enhanced_recovery_manager import EnhancedRecoveryManager

def initialize_system_for_production():
    print("🏗️ ALUSTETAAN JÄRJESTELMÄ TUOTANTOKÄYTTÖÖN")
    print("=" * 50)
    
    # 1. Alusta IPFS-lohkot
    print("1. 🌐 Alustetaan IPFS-lohkot...")
    ipfs = MockIPFS()
    block_manager = IPFSBlockManager(ipfs, 'Jumaltenvaalit_2026', 'main_node')
    metadata_cid = block_manager.initialize_blocks()
    print(f"   ✅ IPFS-lohkot: {metadata_cid}")
    
    # 2. Alusta palautusjärjestelmä
    print("2. 🔄 Alustetaan palautusjärjestelmä...")
    recovery = EnhancedRecoveryManager(
        runtime_dir="runtime",
        ipfs_client=ipfs,
        election_id="Jumaltenvaalit_2026", 
        node_id="main_node"
    )
    recovery_cid = recovery.initialize_recovery_system()
    print(f"   ✅ Palautusjärjestelmä: {recovery_cid}")
    
    # 3. Tarkista lohkojen tila
    print("3. 📊 Tarkistetaan lohkojen tila...")
    block_status = block_manager.get_block_status()
    for block_name, status in block_status.items():
        print(f"   📦 {block_name}: {status['entries']}/{status['max_size']} entries")
    
    print("\n🎯 JÄRJESTELMÄ ON NYT VALMIS TUOTANTOLUKITUKSEEN!")
    print("💡 Seuraava vaihe: python enable_production.py")

if __name__ == "__main__":
    initialize_system_for_production()
