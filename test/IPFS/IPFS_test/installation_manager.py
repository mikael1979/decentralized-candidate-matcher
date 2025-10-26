import os
import sys
import json
from typing import Optional

# Services-importit
from services.console_ui import print_header, get_password
from services.election_collector import collect_election_info
from services.time_lock_collector import collect_time_lock_info
from services.key_manager import generate_keys, save_keys
from services.config_generator import create_all_configs
from services.system_chain_creator import create_system_chain
from services.installation_verifier import verify_installation
from services.install_data_loader import load_install_data
from cryptography.hazmat.primitives import serialization

VERSION = "0.0.6-alpha"
USE_PROD_MODE = '--prod' in sys.argv

class InstallationManager:
    def __init__(self):
        self.install_data = load_install_data()
        self.election_data = {}
        self.admin_data = {}
        self.private_key = None
        self.public_key = None
        self.system_id = None
        self.installation_password = None

    def _collect_admin_info(self):
        print("\n👤 JÄRJESTELMÄN ADMIN-TIEDOT")
        print("-" * 30)
        while True:
            name = input("Adminin nimi: ").strip()
            if name:
                break
            print("❌ Nimi on pakollinen")
        while True:
            username = input("Käyttäjätunnus: ").strip()
            if username:
                break
            print("❌ Käyttäjätunnus on pakollinen")
        email = input("Sähköposti (valinnainen): ").strip()
        self.admin_data = {
            "name": name,
            "username": username,
            "email": email,
            "role": "super_admin",
            "admin_id": f"admin_{username.lower()}"
        }

    def run_first_install(self) -> bool:
        print_header(VERSION, USE_PROD_MODE)
        
        self.election_data = collect_election_info()
        time_lock = collect_time_lock_info()
        self.election_data.update(time_lock)
        self._collect_admin_info()
        self.installation_password = get_password()

        self.private_key, self.public_key, self.system_id = generate_keys()
        save_keys(
            self.private_key, self.public_key, self.installation_password,
            self.system_id, self.election_data['id'], self.admin_data['username']
        )

        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        create_all_configs(
            self.election_data, self.admin_data, self.system_id, public_pem,
            self.install_data, self.private_key
        )

        create_system_chain(self.election_data['id'], self.system_id, VERSION, self.private_key, USE_PROD_MODE)

        return verify_installation()

    def run_config_install(self) -> bool:
        """Suorita asennus olemassa olevalla config-tiedostolla"""
        try:
            print_header(VERSION, USE_PROD_MODE)
            print("🔧 Suoritetaan config-asennus...")
            
            # Tarkista että install_config.json on olemassa
            if not os.path.exists('install_config.json'):
                print("❌ install_config.json tiedostoa ei löydy")
                print("💡 Luo ensin install_config.json tiedosto tai käytä --first-install")
                return False
            
            # Lataa olemassa oleva konfiguraatio
            with open('install_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print(f"📁 Config-tiedoston sisältö: {list(config.keys())}")
            
            # Tarkista pakolliset kentät
            required_fields = ['election_data', 'admin_data']
            missing_fields = []
            for field in required_fields:
                if field not in config:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ Pakollisia kenttiä puuttuu: {', '.join(missing_fields)}")
                print("💡 Tarkista install_config.json tiedoston sisältö")
                print("💡 Esimerkki oikeasta muodosta:")
                print('''
{
  "election_data": {
    "id": "kunnallisvaalit-2025",
    "name": {
      "fi": "Kunnallisvaalit 2025",
      "en": "Municipal Elections 2025", 
      "sv": "Kommunala val 2025"
    },
    "date": "2025-04-13",
    "type": "municipal"
  },
  "admin_data": {
    "name": "Testi Admin",
    "username": "admin",
    "email": "admin@example.com",
    "role": "super_admin"
  }
}''')
                return False
            
            self.election_data = config['election_data']
            self.admin_data = config['admin_data']
            
            # Tarkista että vaalityypin pakolliset kentät ovat olemassa
            if 'id' not in self.election_data:
                print("❌ election_data.id puuttuu")
                return False
            if 'name' not in self.election_data:
                print("❌ election_data.name puuttuu")
                return False
            
            print(f"✅ Ladataan vaali: {self.election_data.get('name', {}).get('fi', 'Nimetön vaali')}")
            
            # Pyydä salasana uudelleen
            self.installation_password = get_password()
            
            # Generoi uudet avaimet
            self.private_key, self.public_key, self.system_id = generate_keys()
            
            # Tallenna avaimet
            save_keys(
                self.private_key, self.public_key, self.installation_password,
                self.system_id, self.election_data['id'], self.admin_data['username']
            )
            
            # Luo konfiguraatiot
            public_pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode('utf-8')
            
            create_all_configs(
                self.election_data, self.admin_data, self.system_id, public_pem,
                self.install_data, self.private_key
            )
            
            # Päivitä järjestelmäketju
            create_system_chain(self.election_data['id'], self.system_id, VERSION, self.private_key, USE_PROD_MODE)
            
            return verify_installation()
            
        except json.JSONDecodeError as e:
            print(f"❌ install_config.json on virheellinen JSON-muodossa: {e}")
            return False
        except Exception as e:
            print(f"❌ Config-asennus epäonnistui: {e}")
            import traceback
            traceback.print_exc()
            return False

    def parse_args(self) -> str:
        if '--first-install' in sys.argv:
            return 'first'
        elif '--verify' in sys.argv:
            return 'verify'
        elif '--config-install' in sys.argv:
            return 'config'
        else:
            if os.path.exists('install_config.json'):
                try:
                    with open('install_config.json', 'r') as f:
                        config = json.load(f)
                    if 'election_data' in config and 'admin_data' in config:
                        return 'config'
                    else:
                        print("⚠️  install_config.json ei sisällä vaadittuja kenttiä, käytetään first-install")
                        return 'first'
                except:
                    print("⚠️  install_config.json on virheellinen, käytetään first-install")
                    return 'first'
            else:
                print("ℹ️  install_config.json ei löydy, käytetään first-install -tilaa...")
                return 'first'

    def run(self) -> bool:
        mode = self.parse_args()
        print(f"🔧 Asennustila: {mode}")
        
        if mode == 'verify':
            return verify_installation()
        elif mode == 'first':
            return self.run_first_install()
        elif mode == 'config':
            return self.run_config_install()
        return False
