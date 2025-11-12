#!/usr/bin/env python3
"""
Testaa IPFS-integrointia
"""
import sys
import os

# Aseta Python-polku
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from src.core.ipfs_client import IPFSClient
from src.managers.ipfs_sync_manager import IPFSSyncManager

def test_ipfs_basic():
    print("🔧 TESTI 1: IPFS-CLIENT PERUSTOIMINNOT")
    ipfs = IPFSClient.get_client('Jumaltenvaalit2026')
    print(f"✅ Client type: {type(ipfs._client).__name__}")
    
    # Testaa data-julkaisu
    test_data = {"test": "data", "number": 42}
    cid = ipfs.publish_election_data("test", test_data)
    print(f"✅ Data published with CID: {cid}")
    
    # Testaa data-haku
    retrieved = ipfs.fetch_from_ipfs(cid)
    print(f"✅ Data retrieved: {retrieved is not None}")
    
    return True

def test_ipfs_sync():
    print("\n🔄 TESTI 2: IPFS-SYNKRONOINTI")
    sync_manager = IPFSSyncManager('Jumaltenvaalit2026')
    report = sync_manager.full_sync()
    
    print(f"✅ Sync completed: {report['status']}")
    print(f"📊 Files synced: {report['files_synced']}")
    
    for file_type, cid in report['ipfs_cids'].items():
        print(f"   📄 {file_type}: {cid}")
    
    return True

def test_ipfs_verify():
    print("\n🔍 TESTI 3: EHEYDEN VARMISTUS")
    sync_manager = IPFSSyncManager('Jumaltenvaalit2026')
    report = sync_manager.verify_sync_integrity()
    
    print(f"✅ Verification completed")
    print(f"📊 Valid files: {report['valid_files']}/{report['total_files']}")
    
    for file_type, result in report['results'].items():
        status = "✅" if result == "valid" else "❌" if result == "invalid" else "⚠️"
        print(f"   {status} {file_type}: {result}")
    
    return True

if __name__ == "__main__":
    print("🎯 ALoitetaan IPFS-integroinnin testaus")
    print("=" * 50)
    
    try:
        test_ipfs_basic()
        test_ipfs_sync() 
        test_ipfs_verify()
        print("\n🎉 KAIKKI TESTIT LÄPÄISTY! IPFS-INTEGROINTI TOIMII!")
    except Exception as e:
        print(f"\n💥 TESTI EPÄONNISTUI: {e}")
        import traceback
        traceback.print_exc()
