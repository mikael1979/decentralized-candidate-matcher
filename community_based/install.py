#!/usr/bin/env python3
"""
Vaalijärjestelmän modulaarinen asennusskripti - KORJATTU VERSIO
Käyttö: 
  python install.py --config-file=CID/TIEDOSTO --election-id=ID [--first-install] [--output-dir=DIR]
"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime

# Lisää moduulit polkuun
sys.path.append('.')

try:
    from metadata_manager import get_metadata_manager
    from installation_engine import InstallationEngine
except ImportError as e:
    print(f"Moduulien latausvirhe: {e}")
    sys.exit(1)

# Yksinkertainen MockIPFS korvaaja jos ei saatavilla
class SimpleMockIPFS:
    """Yksinkertainen Mock-IPFS paikallisille tiedostoille"""
    
    def download(self, cid_or_path):
        """Lataa dataa - tukea paikallisille tiedostoille"""
        if cid_or_path.endswith('.json') and Path(cid_or_path).exists():
            # Lataa paikallisesta tiedostosta
            try:
                with open(cid_or_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ Virhe ladattaessa tiedostoa {cid_or_path}: {e}")
                return None
        else:
            print(f"⚠️  IPFS-toiminto ei saatavilla, käytetään paikallisia tiedostoja")
            return None
    
    def upload(self, data):
        """Mock-upload - palauttaa mock-CID:n"""
        import hashlib
        content_string = json.dumps(data, sort_keys=True, ensure_ascii=False)
        content_hash = hashlib.sha256(content_string.encode('utf-8')).hexdigest()
        return f"QmMock{content_hash[:40]}"

def load_elections_config_direct(file_path: str) -> dict:
    """Lataa vaalikonfiguraatio suoraan tiedostosta"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Tarkista tiedoston rakenne
        if 'elections' in data:
            # elections_list.json rakenne
            return data
        elif 'election_data' in data:
            # install_config.base.json rakenne - muunna elections_list muotoon
            return convert_install_config_to_elections_list(data)
        else:
            raise ValueError("Tuntematon konfiguraatiotiedoston rakenne")
            
    except Exception as e:
        raise ValueError(f"Virhe ladattaessa tiedostoa {file_path}: {e}")

def convert_install_config_to_elections_list(install_config: dict) -> dict:
    """Muuntaa install_config.base.json muotoon elections_list.json"""
    election_data = install_config['election_data']
    
    return {
        "metadata": {
            "version": "1.0.0",
            "created": datetime.now().isoformat(),
            "source": "converted_from_install_config"
        },
        "elections": [
            {
                "election_id": election_data["id"],
                "name": election_data["name"],
                "description": election_data["name"],  # Käytä nimeä kuvauksena
                "dates": [
                    {
                        "phase": 1,
                        "date": election_data["date"],
                        "description": {
                            "fi": "Vaalipäivä",
                            "en": "Election day",
                            "sv": "Valdag"
                        }
                    }
                ],
                "type": election_data["type"],
                "timelock_enabled": election_data["timelock_enabled"],
                "edit_deadline": election_data["edit_deadline"],
                "grace_period_hours": election_data["grace_period_hours"],
                "community_managed": election_data["community_managed"],
                "phases": 1,
                "districts": election_data.get("districts", ["koko_maa"]),
                "status": "upcoming",
                "config_cid": election_data.get("ipfs_cid", "")
            }
        ]
    }

def main():
    parser = argparse.ArgumentParser(
        description="Vaalijärjestelmän modulaarinen asennus",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esimerkkejä:
  # Käytä paikallista elections_list.json tiedostoa
  python install.py --config-file=config_output/elections_list.json --election-id=Testivaalit_2027 --first-install
  
  # Käytä paikallista install_config.base.json tiedostoa
  python install.py --config-file=config_output/install_config.base.json --election-id=Testivaalit_2027 --first-install
        """
    )
    
    parser.add_argument(
        "--config-file", 
        required=True,
        help="Polku paikalliseen JSON-tiedostoon"
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
    
    # Tarkista että config-file on olemassa
    if not Path(args.config_file).exists():
        print(f"❌ Tiedostoa ei löydy: {args.config_file}")
        sys.exit(1)
    
    # Alusta komponentit
    engine = InstallationEngine(args.output_dir)
    engine.set_ipfs_client(SimpleMockIPFS())  # Yksinkertainen mock-IPFS
    
    try:
        # Lataa vaalikonfiguraatio SUORAAN tiedostosta
        print(f"📁 Ladataan konfiguraatiota tiedostosta: {args.config_file}")
        elections_data = load_elections_config_direct(args.config_file)
        
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
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

