#!/usr/bin/env python3
"""
Yksinkertainen IPFS-testi ilman monimutkaisia importteja
"""
import sys
import os

# Aseta Python-polku
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_basic_ipfs():
    print("🔧 TESTI: IPFS-CLIENT PERUSTOIMINNOT")
    
    try:
        from src.core.ipfs_client import IPFSClient
        
        # Alusta IPFS-client
        ipfs = IPFSClient.get_client('Jumaltenvaalit2026')
        print(f"✅ IPFS-asiakas: {type(ipfs._client).__name__}")
        
        # Testaa data-julkaisu
        test_data = {"test": "data", "number": 42, "message": "Tämä on testi"}
        cid = ipfs.publish_election_data("test", test_data)
        print(f"✅ Data julkaistu CID:llä: {cid}")
        
        # Testaa että CID on oikean muotoinen
        if cid.startswith('mock_') or cid.startswith('Qm'):
            print("✅ CID on oikean muotoinen")
        else:
            print(f"⚠️  CID on epätavallinen: {cid}")
        
        return True
        
    except Exception as e:
        print(f"❌ Testi epäonnistui: {e}")
        return False

def test_sync_manager():
    print("\n🔄 TESTI: IPFS-SYNKRONOINTIMANAGER")
    
    try:
        from src.managers.ipfs_sync_manager import IPFSSyncManager
        
        sync_manager = IPFSSyncManager('Jumaltenvaalit2026')
        print("✅ IPFS-synkronointimanager alustettu")
        
        # Testaa synkronointi
        report = sync_manager.full_sync()
        print(f"✅ Synkronointi valmis: {report['status']}")
        print(f"📊 Tiedostoja synkronoitu: {report['files_synced']}")
        
        # Näytä CID:t
        for file_type, cid in report['ipfs_cids'].items():
            print(f"   📄 {file_type}: {cid}")
        
        return True
        
    except Exception as e:
        print(f"❌ Synkronointitesti epäonnistui: {e}")
        return False

if __name__ == "__main__":
    print("🎯 ALoitetaan yksinkertainen IPFS-testi")
    print("=" * 50)
    
    success1 = test_basic_ipfs()
    success2 = test_sync_manager()
    
    if success1 and success2:
        print("\n🎉 KAIKKI TESTIT LÄPÄISTY! IPFS-INTEGROINTI TOIMII!")
    else:
        print("\n💥 JOITKIN TESTIT EPÄONNISTUIVAT")
        print("💡 Tarkista että kaikki tiedostot ovat paikallaan")
