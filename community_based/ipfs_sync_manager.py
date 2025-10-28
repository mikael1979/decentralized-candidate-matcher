[file name]: ipfs_sync_manager.py
[file content begin]
#!/usr/bin/env python3
"""
IPFS synkronointien hallintaskripti
Hallitsee mock-IPFS:n ja oikean IPFS:n välistä synkronointia
"""

import argparse
import sys
from pathlib import Path

sys.path.append('.')

try:
    from mock_ipfs_sync_ready import MockIPFSSyncReady
    from ipfs_sync_engine import get_ipfs_sync_engine, RealIPFS
except ImportError as e:
    print(f"Moduulien latausvirhe: {e}")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="IPFS synkronointien hallinta")
    
    subparsers = parser.add_subparsers(dest='command', help='Komennot')
    
    # Status-komento
    status_parser = subparsers.add_parser('status', help='Näytä synkronointitila')
    
    # Enable-komento
    enable_parser = subparsers.add_parser('enable', help='Ota synkronointi käyttöön')
    enable_parser.add_argument('--mode', choices=['hybrid', 'real_only'], 
                              default='hybrid', help='Synkronointitila')
    
    # Disable-komento
    disable_parser = subparsers.add_parser('disable', help='Poista synkronointi käytöstä')
    
    # Sync-all komento
    sync_all_parser = subparsers.add_parser('sync-all', help='Synkronoi kaikki mock -> real')
    
    # Migrate komento
    migrate_parser = subparsers.add_parser('migrate', help='Siirrä oikeaan IPFS:ään')
    
    # Test-komento
    test_parser = subparsers.add_parser('test', help='Testaa IPFS-yhteyksiä')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Alusta mock-IPFS ja synkronointimoottori
    mock_ipfs = MockIPFSSyncReady()
    
    try:
        sync_engine = get_ipfs_sync_engine(mock_ipfs)
        
        if args.command == 'status':
            show_sync_status(sync_engine)
            
        elif args.command == 'enable':
            enable_sync(sync_engine, args.mode)
            
        elif args.command == 'disable':
            disable_sync(sync_engine)
            
        elif args.command == 'sync-all':
            sync_all_data(sync_engine)
            
        elif args.command == 'migrate':
            migrate_to_real(sync_engine)
            
        elif args.command == 'test':
            test_connections(sync_engine)
            
    except Exception as e:
        print(f"❌ Virhe: {e}")
        sys.exit(1)

def show_sync_status(sync_engine):
    """Näytä synkronointitila"""
    status = sync_engine.get_sync_status()
    
    print("📊 IPFS SYNKRONOINTITILA")
    print("=" * 50)
    
    print(f"🔧 Synkronointi käytössä: {'✅' if status['sync_enabled'] else '❌'}")
    print(f"🏷️  Tila: {status['sync_mode']}")
    print(f"🔗 Oikea IPFS saatavilla: {'✅' if status['real_ipfs_available'] else '❌'}")
    
    if status['last_sync']:
        print(f"🕒 Viimeisin synkronointi: {status['last_sync']}")
    
    # Mock-tilastot
    mock_stats = status['mock_stats']
    print(f"\n🔄 MOCK-IPFS:")
    print(f"   CID:itä: {mock_stats['total_cids']}")
    print(f"   Koko: {mock_stats['total_size_bytes']} tavua")
    print(f"   Latauksia: {mock_stats['total_access_count']}")
    
    # Real-tilastot
    real_stats = status['real_stats']
    print(f"\n🌐 OIKEA IPFS:")
    print(f"   Yhdistetty: {'✅' if real_stats['connected'] else '❌'}")
    if real_stats['connected']:
        print(f"   Peer ID: {real_stats.get('peer_id', 'N/A')}")
        print(f"   Agent: {real_stats.get('agent_version', 'N/A')}")

def enable_sync(sync_engine, mode):
    """Ota synkronointi käyttöön"""
    sync_engine.enable_sync(mode)
    print(f"✅ Synkronointi käytössä tilassa: {mode}")

def disable_sync(sync_engine):
    """Poista synkronointi käytöstä"""
    sync_engine.disable_sync()
    print("✅ Synkronointi pois käytöstä")

def sync_all_data(sync_engine):
    """Synkronoi kaikki data"""
    print("🔄 SYNKRONOIDAAN KAIKKI DATA...")
    results = sync_engine.sync_all_mock_to_real()
    
    if results["success"]:
        print(f"✅ Synkronoitu {results['total_synced']} kohdetta")
        if results["failed"]:
            print(f"⚠️  {len(results['failed'])} epäonnistui")
    else:
        print("❌ Synkronointi epäonnistui")

def migrate_to_real(sync_engine):
    """Siirrä oikeaan IPFS:ään"""
    print("🚀 SIIRRETÄÄN OIKEAAN IPFS:ÄÄN...")
    success = sync_engine.migrate_to_real_only()
    
    if success:
        print("✅ Siirto oikeaan IPFS:ään valmis!")
        print("💡 Muista päivittää konfiguraatiot käyttämään oikeita CID:itä")
    else:
        print("❌ Siirto epäonnistui")

def test_connections(sync_engine):
    """Testaa IPFS-yhteyksiä"""
    print("🧪 TESTATAAN IPFS-YHTEYKSIÄ")
    
    # Testaa mock-IPFS
    print("\n1. 🔄 TESTATAAN MOCK-IPFS:ÄÄ...")
    test_data = {"test": "mock_ipfs_test", "timestamp": datetime.now().isoformat()}
    
    try:
        mock_cid = sync_engine.mock_ipfs.upload(test_data)
        downloaded_data = sync_engine.mock_ipfs.download(mock_cid)
        
        if downloaded_data and downloaded_data["test"] == test_data["test"]:
            print("   ✅ Mock-IPFS toimii")
        else:
            print("   ❌ Mock-IPFS testi epäonnistui")
    except Exception as e:
        print(f"   ❌ Mock-IPFS virhe: {e}")
    
    # Testaa oikea IPFS jos saatavilla
    if sync_engine.real_ipfs:
        print("\n2. 🌐 TESTATAAN OIKEAA IPFS:ÄÄ...")
        test_data = {"test": "real_ipfs_test", "timestamp": datetime.now().isoformat()}
        
        try:
            real_cid = sync_engine.real_ipfs.upload(test_data)
            downloaded_data = sync_engine.real_ipfs.download(real_cid)
            
            if downloaded_data and downloaded_data["test"] == test_data["test"]:
                print("   ✅ Oikea IPFS toimii")
            else:
                print("   ❌ Oikea IPFS testi epäonnistui")
        except Exception as e:
            print(f"   ❌ Oikea IPFS virhe: {e}")
    else:
        print("\n2. 🌐 OIKEA IPFS EI SAATAVILLA")

if __name__ == "__main__":
    main()
[file content end]
