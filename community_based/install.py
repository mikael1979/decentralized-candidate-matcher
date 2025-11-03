#!/usr/bin/env python3
"""
Vaalijärjestelmän asennus- ja konfiguraatiotyökalu - KORJATTU VERSIO
Käyttö:
  python install.py --config-file=CID/TIEDOSTO --election-id=ID [--first-install] [--output-dir=DIR]
  
Esimerkkejä:
  # Liity olemassa olevaan vaaliin
  python install.py --config-file=config_output/elections_list.json --election-id=Testivaalit_2027
  
  # Luo uusi vaali (master-kone)
  python install.py --config-file=config_output/elections_list.json --election-id=Testivaalit_2027 --first-install
  
  # Käytä suoraa install_configia
  python install.py --config-file=config_output/install_config.base.json --election-id=Testivaalit_2027 --first-install
"""

import argparse
import json
import sys
from pathlib import Path

# Lisää nykyinen hakemisto polkuun
sys.path.append('.')

try:
    from metadata_manager import get_metadata_manager
    from installation_engine import InstallationEngine
    from mock_ipfs import MockIPFS
except ImportError as e:
    print(f"❌ Tarvittavia moduuleja puuttuu: {e}")
    print("💡 Varmista että olet oikeassa hakemistossa ja riippuvuudet on asennettu")
    sys.exit(1)

def should_use_first_install(election_id, elections_data, metadata_manager):
    """
    Päätä älykkäästi pitäisikö käyttää --first-install lippua
    KORJATTU: Tarkistaa sekä elections_list.json että nykyisen koneen tilan
    """
    
    # 1. Tarkista onko vaali elections_list.json:ssa
    vaali_loytyy_listasta = any(
        e['election_id'] == election_id 
        for e in elections_data.get('elections', [])
    )
    
    # 2. Tarkista onko vaali asennettuna nykyiseen koneeseen
    on_nykyisessa_koneessa = not metadata_manager.is_first_installation(election_id)
    
    print(f"🔍 FIRST-INSTALL PÄÄTÖSLOGIIKKA:")
    print(f"   Vaali '{election_id}' elections_list.json:ssa: {vaali_loytyy_listasta}")
    print(f"   Vaali asennettuna nykyiseen koneeseen: {on_nykyisessa_koneessa}")
    
    if vaali_loytyy_listasta and on_nykyisessa_koneessa:
        # Vaali on olemassa ja asennettuna tähän koneeseen → normaali asennus
        print("   📊 PÄÄTÖS: Normaali asennus (vaali löytyy ja on asennettuna)")
        return False
    elif vaali_loytyy_listasta and not on_nykyisessa_koneessa:
        # Vaali on olemassa, mutta EI asennettuna tähän koneeseen → liity olemassa olevaan
        print("   📊 PÄÄTÖS: Liity olemassa olevaan vaaliin (vaali löytyy listasta)")
        return False  
    elif not vaali_loytyy_listasta and not on_nykyisessa_koneessa:
        # Vaali EI ole olemassa eikä asennettuna → ensimmäinen asennus
        print("   📊 PÄÄTÖS: Ensimmäinen asennus (vaali ei löydy listasta)")
        return True
    else:
        # Epäjohdonmukainen tila: vaali ei löydy listasta, mutta on asennettuna koneeseen
        print("   ⚠️  PÄÄTÖS: Epäjohdonmukainen tila, käytetään normaalia asennusta")
        return False

def main():
    """Pääohjelma"""
    
    parser = argparse.ArgumentParser(description="Vaalijärjestelmän asennus- ja konfiguraatiotyökalu")
    
    parser.add_argument("--config-file", required=True,
                       help="Konfiguraatiotiedosto (IPFS CID tai paikallinen tiedosto)")
    parser.add_argument("--election-id", required=True,
                       help="Asennettavan vaalin ID")
    parser.add_argument("--first-install", action="store_true",
                       help="Ensimmäinen asennus (luo master-kone)")
    parser.add_argument("--output-dir", default="runtime",
                       help="Output-hakemisto (default: runtime)")
    
    args = parser.parse_args()
    
    print("🎯 VAAILIJÄRJESTELMÄN ASENNUS")
    print("=" * 50)
    
    try:
        # Alusta komponentit
        metadata_manager = get_metadata_manager(args.output_dir)
        engine = InstallationEngine(args.output_dir)
        
        # Aseta Mock-IPFS (voi korvata oikealla IPFS-asiakkaalla)
        ipfs_client = MockIPFS()
        engine.set_ipfs_client(ipfs_client)
        
        # Lataa vaalikonfiguraatio
        print(f"📁 Ladataan konfiguraatiota tiedostosta: {args.config_file}")
        elections_data = engine.load_elections_config(args.config_file)
        
        # Tarkista että vaali löytyy konfiguraatiosta
        vaali_loytyy = any(
            e['election_id'] == args.election_id 
            for e in elections_data.get('elections', [])
        )
        
        if not vaali_loytyy:
            print(f"❌ Vaalia '{args.election_id}' ei löydy konfiguraatiotiedostosta")
            print("💡 Saatavilla olevat vaalit:")
            for election in elections_data.get('elections', []):
                print(f"   - {election['election_id']}: {election['name']['fi']}")
            return False
        
        # KORJATTU: Älykäs first-install päätöslogiikka
        use_first_install = should_use_first_install(
            args.election_id, 
            elections_data, 
            metadata_manager
        )
        
        # Käsittele käyttäjän antama --first-install lippu
        if args.first_install and not use_first_install:
            print("⚠️  VAROITUS: --first-install asetettu, mutta vaali on jo olemassa")
            print("   Käytetään normaalia asennusta (liity olemassa olevaan)")
            use_first_install = False
        elif not args.first_install and use_first_install:
            print("💡 INFO: Ensimmäinen asennus tälle vaalille")
            print("   Käytetään --first-install lippua luodaksesi master-kone")
            use_first_install = True
        else:
            # Käyttäjän antama lippu ja automaattinen päätös täsmäävät
            use_first_install = args.first_install
        
        # Listaa saatavilla olevat vaalit
        engine.list_available_elections(elections_data)
        
        # Asenna vaali
        print(f"\n🚀 ASENNETAAN VAALI: {args.election_id}")
        result = engine.install_election(
            args.election_id,
            elections_data,
            first_install=use_first_install
        )
        
        # Näytä asennustiedot
        election = result["election"]
        machine_info = result["machine_info"]
        
        print(f"\n✅ ASENNUS ONNISTUI!")
        print("=" * 40)
        print(f"🏛️  Vaali: {election['name']['fi']}")
        print(f"💻 Kone-ID: {machine_info['machine_id']}")
        print(f"👑 Rooli: {'MASTER-KONE' if use_first_install else 'TYÖASEMA'}")
        print(f"📁 Hakemisto: {args.output_dir}")
        print(f"⏰ Aikaleima: {result['installation_time']}")
        
        # Tarkista asennus
        print(f"\n🔍 TARKISTETAAN ASENNUS...")
        if engine.verify_installation(args.election_id):
            print("✅ Asennus tarkistettu onnistuneesti")
        else:
            print("❌ Asennuksen tarkistus epäonnistui")
            return False
        
        # Näytä käyttöohjeet
        print(f"\n💡 KÄYTTÖÖNOTTO VALMIS!")
        print("=" * 40)
        
        if use_first_install:
            print("🎯 MASTER-KONEEN TOIMINNOT:")
            print("   - Hallinnoi kysymysten synkronointia")
            print("   - Luo uusia työasemia komennolla:")
            print(f"     python install.py --config-file={args.config_file} --election-id={args.election_id}")
            print("   - Aktivoi tuotantotila: python enable_production.py")
        else:
            print("🎯 TYÖASEMAN TOIMINNOT:")
            print("   - Osallistu vertailuihin: python demo_comparisons.py")
            print("   - Tarkista tila: python system_bootstrap.py")
            print("   - Synkronoi data master-koneen kanssa")
        
        print(f"\n📊 TESTAA JÄRJESTELMÄÄ:")
        print("   python system_bootstrap.py          # Tarkista käynnistys")
        print("   python manage_questions.py status   # Kysymysten tila")
        print("   python demo_comparisons.py --user testi --count 3  # Testaa vertailut")
        
        return True
        
    except Exception as e:
        print(f"❌ ASENNUS EPÄONNISTUI: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
