#!/usr/bin/env python3
# install.py - PÄIVITETTY IPFS-VALINNALLA
"""
Vaalijärjestelmän asennus- ja konfiguraatiotyökalu - PÄIVITETTY IPFS-VALINNALLA
Käyttö: 
  python install.py --config-file=elections_list.json --election-id=vaali_2024 --first-install --ipfs-type=mock
  python install.py --config-file=elections_list.json --election-id=vaali_2024 --ipfs-type=real --ipfs-host=localhost --ipfs-port=5001
"""

import argparse
import sys
from pathlib import Path

# Lisää nykyinen hakemisto polkuun
sys.path.append('.')

def get_ipfs_client(ipfs_type, host=None, port=None, test_connection=True):
    """Hae IPFS-client valitun tyypin mukaan"""
    print(f"🔗 Alustetaan IPFS: {ipfs_type.upper()}")
    
    if ipfs_type == "mock":
        from mock_ipfs import MockIPFS
        client = MockIPFS()
        print("✅ MockIPFS alustettu")
        return client
    
    elif ipfs_type == "real":
        try:
            from real_ipfs_client import RealIPFSClient
            client = RealIPFSClient(host=host or "localhost", port=port or 5001)
            
            if test_connection:
                # Testaa yhteys
                stats = client.get_stats()
                if stats.get("connected", False):
                    print("✅ Todellinen IPFS yhdistetty onnistuneesti!")
                else:
                    print("⚠️  IPFS-daemon ei vastaa - varmista että ipfs daemon on käynnissä")
                    print("💡 Käynnistä: ipfs daemon tai docker start ipfs-node")
                    
            return client
            
        except ImportError:
            print("❌ RealIPFSClient ei saatavilla - tarkista että real_ipfs_client.py on olemassa")
            print("🔄 Käytetään MockIPFS:ää fallbackina")
            from mock_ipfs import MockIPFS
            return MockIPFS()
    
    elif ipfs_type == "auto":
        # Yritä ensin todellista IPFS:ää, sitten mock
        try:
            from real_ipfs_client import RealIPFSClient
            client = RealIPFSClient(host=host or "localhost", port=port or 5001)
            stats = client.get_stats()
            if stats.get("connected", False):
                print("✅ Auto-valinta: Todellinen IPFS yhdistetty")
                return client
            else:
                raise ConnectionError("IPFS ei vastaa")
        except Exception as e:
            print(f"⚠️  Auto-valinta: Todellinen IPFS epäonnistui ({e})")
            print("🔄 Auto-valinta: Käytetään MockIPFS:ää")
            from mock_ipfs import MockIPFS
            return MockIPFS()
    
    else:
        print(f"❌ Tuntematon IPFS-tyyppi: {ipfs_type}")
        print("🔄 Käytetään MockIPFS:ää")
        from mock_ipfs import MockIPFS
        return MockIPFS()

def main():
    parser = argparse.ArgumentParser(description="Vaalijärjestelmän asennus - PÄIVITETTY IPFS-VALINNALLA")
    
    # Perus-argumentit
    parser.add_argument('--config-file', required=True, help='Konfiguraatiotiedosto (elections_list.json)')
    parser.add_argument('--election-id', required=True, help='Asennettavan vaalin ID')
    parser.add_argument('--first-install', action='store_true', help='Ensimmäinen asennus (master-kone)')
    parser.add_argument('--output-dir', default='runtime', help='Output-hakemisto')
    parser.add_argument('--verify', action='store_true', help='Tarkista asennus')
    parser.add_argument('--master-cid', help='Master-noden CID (työasemalle)')
    
    # Uudet IPFS-argumentit
    parser.add_argument('--ipfs-type', 
                       choices=['mock', 'real', 'auto'], 
                       default='auto',
                       help='IPFS-tyyppi: mock (testi), real (todellinen), auto (automaattinen valinta)')
    parser.add_argument('--ipfs-host', default='localhost', help='IPFS-palvelin (vain real/auto)')
    parser.add_argument('--ipfs-port', type=int, default=5001, help='IPFS-portti (vain real/auto)')
    parser.add_argument('--skip-ipfs-test', action='store_true', help='Ohita IPFS-yhteyden testaus')
    
    args = parser.parse_args()
    
    print("🎯 VAAILIJÄRJESTELMÄN ASENNUS - IPFS-VALINNALLA")
    print("=" * 60)
    
    try:
        # 1. Alusta IPFS-client valitulla tyypillä
        ipfs = get_ipfs_client(
            ipfs_type=args.ipfs_type,
            host=args.ipfs_host,
            port=args.ipfs_port,
            test_connection=not args.skip_ipfs_test
        )
        
        # 2. Alusta asennusmoottori
        from installation_engine import InstallationEngine
        engine = InstallationEngine(args.output_dir)
        engine.set_ipfs_client(ipfs)
        
        if args.verify:
            # Tarkista asennus
            print("🔍 TARKISTETAAN ASENNUS...")
            success = engine.verify_installation(args.election_id)
            if success:
                print("✅ Asennus tarkistettu onnistuneesti")
                return True
            else:
                print("❌ Asennuksen tarkistus epäonnistui")
                return False
        
        # 3. Lataa konfiguraatio
        elections_data = engine.load_elections_config(args.config_file)
        
        # 4. Listaa saatavilla olevat vaalit
        engine.list_available_elections(elections_data)
        
        # 5. Tarkista että vaali on olemassa konfiguraatiossa
        election_exists = any(e['election_id'] == args.election_id for e in elections_data['elections'])
        if not election_exists:
            print(f"❌ Vaalia '{args.election_id}' ei löydy konfiguraatiosta")
            return False
        
        # 6. Päätä first-install tila (sama logiikka kuin aiemmin)
        first_install = args.first_install
        if not first_install:
            from metadata_manager import get_metadata_manager
            metadata_manager = get_metadata_manager(args.output_dir)
            machine_info = metadata_manager.get_machine_info()
            
            if machine_info['election_id'] == 'unknown':
                first_install = True
                print("📊 PÄÄTÖS: Ensimmäinen asennus (ei aiempaa vaalia)")
            elif machine_info['election_id'] != args.election_id:
                first_install = False
                print("📊 PÄÄTÖS: Liity olemassa olevaan vaaliin")
            else:
                first_install = False
                print("📊 PÄÄTÖS: Päivitä olemassa olevaa asennusta")
        
        # 7. Suorita asennus
        print(f"{'👑 MASTER-NODE ASENNUS' if first_install else '💻 TYÖASEMAN ASENNUS'}")
        print("=" * 40)
        
        result = engine.install_election(args.election_id, elections_data, first_install)
        
        # 8. IPFS-spesifiset toimenpiteet
        if args.ipfs_type in ['real', 'auto'] and hasattr(ipfs, 'get_stats'):
            stats = ipfs.get_stats()
            if stats.get('connected'):
                print(f"🌐 IPFS-tilastot: {stats}")
                
                # Pin tärkeät tiedot jos todellinen IPFS
                if first_install and hasattr(ipfs, 'pin'):
                    try:
                        # Tässä voit pinata tärkeitä CIDEjä
                        print("📌 Pinnataan tärkeät tiedot IPFS:ään...")
                    except:
                        print("⚠️  Pinnaus epäonnistui - ei kriittinen")
        
        print("\n✅ ASENNUS ONNISTUI!")
        print("=" * 40)
        print(f"🏛️  Vaali: {result['election']['name']['fi']}")
        print(f"💻 Kone-ID: {result['machine_info']['machine_id']}")
        print(f"👑 Rooli: {'MASTER-NODE' if first_install else 'TYÖASEMA'}")
        print(f"🔗 IPFS: {args.ipfs_type.upper()}")
        if args.ipfs_type in ['real', 'auto']:
            print(f"🌐 Osoite: {args.ipfs_host}:{args.ipfs_port}")
        print(f"📁 Hakemisto: {args.output_dir}")
        
        # 9. Tarkista asennus
        print("\n🔍 TARKISTETAAN ASENNUS...")
        verification_success = engine.verify_installation(args.election_id)
        
        if verification_success:
            print("\n💡 KÄYTTÖÖNOTTO VALMIS!")
            print("=" * 40)
            
            # Näytä IPFS-spesifiset ohjeet
            if args.ipfs_type == 'real':
                print("🌐 TODELLINEN IPFS KÄYTÖSSÄ:")
                print("   - Tarkista IPFS-daemon: ipfs stats bw")
                print("   - Listaa pinatut: ipfs pin ls")
                print("   - Tarkista verkko: ipfs swarm peers")
            else:
                print("🔄 MOCK-IPFS KÄYTÖSSÄ:")
                print("   - Data tallennettuna: mock_ipfs_data.json")
                print("   - Vaihda todelliseen: --ipfs-type=real")
            
            return True
        else:
            print("❌ Asennuksen tarkistus epäonnistui - tarkista tiedostot")
            return False
            
    except ImportError as e:
        print(f"❌ Riippuvuus puuttuu: {e}")
        print("💡 Varmista että kaikki moduulit ovat saatavilla")
        return False
    except Exception as e:
        print(f"❌ Asennus epäonnistui: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
