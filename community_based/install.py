#!/usr/bin/env python3
# install.py - KORJATTU VERSIO
"""
Vaalijärjestelmän asennus- ja konfiguraatiotyökalu
Käyttö: 
  python install.py --config-file=elections_list.json --election-id=vaali_2024 --first-install
  python install.py --config-file=elections_list.json --election-id=vaali_2024 (työasema)
  python install.py --verify --election-id=vaali_2024
"""

import argparse
import sys
from pathlib import Path

# Lisää nykyinen hakemisto polkuun
sys.path.append('.')

def main():
    parser = argparse.ArgumentParser(description="Vaalijärjestelmän asennus")
    parser.add_argument('--config-file', required=True, help='Konfiguraatiotiedosto (elections_list.json)')
    parser.add_argument('--election-id', required=True, help='Asennettavan vaalin ID')
    parser.add_argument('--first-install', action='store_true', help='Ensimmäinen asennus (master-kone)')
    parser.add_argument('--output-dir', default='runtime', help='Output-hakemisto')
    parser.add_argument('--verify', action='store_true', help='Tarkista asennus')
    
    args = parser.parse_args()
    
    print("🎯 VAAILIJÄRJESTELMÄN ASENNUS")
    print("=" * 50)
    
    try:
        # Tuo riippuvuudet
        from mock_ipfs import MockIPFS
        from installation_engine import InstallationEngine
        from metadata_manager import get_metadata_manager
        
        # Alusta IPFS (mock)
        ipfs = MockIPFS()
        
        # Alusta asennusmoottori
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
        
        # Lataa konfiguraatio
        elections_data = engine.load_elections_config(args.config_file)
        
        # Listaa saatavilla olevat vaalit
        engine.list_available_elections(elections_data)
        
        # Päätä first-install tila
        first_install = args.first_install
        if not first_install:
            # Automaattinen first-install päätös
            metadata_manager = get_metadata_manager(args.output_dir)
            machine_info = metadata_manager.get_machine_info()
            
            print("🔍 FIRST-INSTALL PÄÄTÖSLOGIIKKA:")
            print(f"   Vaali '{args.election_id}' elections_list.json:ssa: {any(e['election_id'] == args.election_id for e in elections_data['elections'])}")
            print(f"   Vaali asennettuna nykyiseen koneeseen: {machine_info['election_id'] == args.election_id}")
            
            # Päätä first-install tila
            if machine_info['election_id'] == 'unknown':
                first_install = True
                print("   📊 PÄÄTÖS: Ensimmäinen asennus (ei aiempaa vaalia)")
            elif machine_info['election_id'] != args.election_id:
                first_install = False
                print("   📊 PÄÄTÖS: Liity olemassa olevaan vaaliin (eri vaali asennettuna)")
            else:
                first_install = False
                print("   📊 PÄÄTÖS: Päivitä olemassa olevaa asennusta")
        
        # Asenna vaali
        result = engine.install_election(args.election_id, elections_data, first_install)
        
        if first_install:
            # Rekisteröi master-kone
            metadata_manager = get_metadata_manager(args.output_dir)
            registry = metadata_manager.create_election_registry(result['election'])
            print("✅ Master-kone rekisteröity")
        
        print("\n✅ ASENNUS ONNISTUI!")
        print("=" * 40)
        print(f"🏛️  Vaali: {result['election']['name']['fi']}")
        print(f"💻 Kone-ID: {result['machine_info']['machine_id']}")
        print(f"👑 Rooli: {'MASTER-KONE' if first_install else 'TYÖASEMA'}")
        print(f"📁 Hakemisto: {args.output_dir}")
        print(f"⏰ Aikaleima: {result['installation_time']}")
        
        # Tarkista asennus
        print("\n🔍 TARKISTETAAN ASENNUS...")
        verification_success = engine.verify_installation(args.election_id)
        
        if verification_success:
            print("\n💡 KÄYTTÖÖNOTTO VALMIS!")
            print("=" * 40)
            
            if first_install:
                print("🎯 MASTER-KONEEN TOIMINNOT:")
                print("   - Luo uusia työasemia komennolla:")
                print(f"     python install.py --config-file={args.config_file} --election-id={args.election_id}")
                print("   - Hallinnoi kysymysten synkronointia")
                print("   - Aktivoi tuotantotila")
            else:
                print("🎯 TYÖASEMAN TOIMINNOT:")
                print("   - Osallistu vertailuihin: python demo_comparisons.py")
                print("   - Tarkista tila: python system_bootstrap.py")
                print("   - Synkronoi data master-koneen kanssa")
            
            print("\n📊 TESTAA JÄRJESTELMÄÄ:")
            print("   python system_bootstrap.py          # Tarkista käynnistys")
            print("   python manage_questions.py status   # Kysymysten tila")
            print("   python demo_comparisons.py --user testi --count 3  # Testaa vertailut")
            
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
