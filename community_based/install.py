[file name]: install.py
[file content begin]
#!/usr/bin/env python3
"""
Vaalijärjestelmän modulaarinen asennusskripti
Käyttö: 
  python install.py --config-file=CID --election-id=ID [--first-install] [--output-dir=DIR]
"""

import argparse
import sys
from pathlib import Path

# Lisää moduulit polkuun
sys.path.append('.')

try:
    from metadata_manager import get_metadata_manager
    from installation_engine import InstallationEngine
    from mock_ipfs_extended import MockIPFSExtended
except ImportError as e:
    print(f"Moduulien latausvirhe: {e}")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Vaalijärjestelmän modulaarinen asennus",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esimerkkejä:
  python install.py --config-file=QmElectionsList123456789 --list-elections
  python install.py --config-file=QmElectionsList123456789 --election-id=president_2024 --first-install
  python install.py --config-file=QmElectionsList123456789 --election-id=president_2024 --output-dir=./my_election
        """
    )
    
    parser.add_argument(
        "--config-file", 
        required=True,
        help="IPFS CID vaalikonfiguraatiolle"
    )
    parser.add_argument(
        "--election-id", 
        help="Tietyn vaalin ID asennettuna (lista näytetään jos ei anneta)"
    )
    parser.add_argument(
        "--output-dir", 
        default="runtime",
        help="Output-hakemisto (oletus: runtime)"
    )
    parser.add_argument(
        "--first-install", 
        action="store_true",
        help="Merkitse ensimmäiseksi asennukseksi (luo master-kone)"
    )
    parser.add_argument(
        "--list-elections", 
        action="store_true",
        help="Listaa saatavilla olevat vaalit"
    )
    parser.add_argument(
        "--verify", 
        action="store_true",
        help="Tarkista nykyinen asennus"
    )
    
    args = parser.parse_args()
    
    # Alusta komponentit
    engine = InstallationEngine(args.output_dir)
    engine.set_ipfs_client(MockIPFSExtended())  # Mock-IPFS testaukseen
    
    try:
        # Lataa vaalikonfiguraatio
        elections_data = engine.load_elections_config(args.config_file)
        
        if args.list_elections:
            engine.list_available_elections(elections_data)
            return
        
        if args.verify:
            if not args.election_id:
                print("Virhe: --election-id vaaditaan verifiointiin")
                return
            
            if engine.verify_installation(args.election_id):
                machine_info = get_metadata_manager(args.output_dir).get_machine_info()
                print(f"✅ ASENNUS OK")
                print(f"   Vaali: {args.election_id}")
                print(f"   Kone-ID: {machine_info['machine_id']}")
                print(f"   Master-kone: {'✅' if machine_info['is_master'] else '❌'}")
            else:
                print("❌ ASENNUS VIRHEELLINEN TAI KESKEN")
            return
        
        if not args.election_id:
            engine.list_available_elections(elections_data)
            print("\n💡 Käytä --election-id=<id> asentaaksesi tietyn vaalin")
            print("💡 Käytä --first-install ensimmäiselle asennukselle")
            return
        
        # Tarkista first-install logiikka
        metadata_manager = get_metadata_manager(args.output_dir)
        is_first = metadata_manager.is_first_installation(args.election_id)
        
        if args.first_install and not is_first:
            print("⚠️  VAROITUS: --first-install asetettu, mutta vaali on jo asennettu")
            print("   Käytetään olemassa olevaa asennusta")
            args.first_install = False
        elif not args.first_install and is_first:
            print("💡 INFO: Ensimmäinen asennus tälle vaalille")
            print("   Käytetään --first-install lippua luodaksesi master-kone")
            args.first_install = True
        
        # Suorita asennus
        result = engine.install_election(
            args.election_id, 
            elections_data, 
            args.first_install
        )
        
        # Näytä loppuraportti
        election = result["election"]
        machine_info = result["machine_info"]
        
        print("\n🎉 ASENNUS VALMIS!")
        print("=" * 50)
        print(f"Vaali: {election['name']['fi']}")
        print(f"Kone-ID: {machine_info['machine_id']}")
        print(f"Asennustyyppi: {'Master-kone' if machine_info['is_master'] else 'Työasema'}")
        print(f"Hakemisto: {args.output_dir}")
        print(f"Asennettu: {result['installation_time']}")
        
        if machine_info['is_master']:
            print("\n🔑 Olet nyt MASTER-KONE tälle vaalille")
            print("   Muut koneet voivat liittyä tähän vaaliin")
        else:
            print("\n💻 Olet nyt TYÖASEMA tälle vaalille")
            print("   Synkronoi data master-koneen kanssa")
            
    except Exception as e:
        print(f"❌ ASENNUS EPÄONNISTUI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
[file content end]
