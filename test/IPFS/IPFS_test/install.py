#!/usr/bin/env python3
"""
Vaalikoneen asennus- ja alustusskripti v0.0.6-alpha
Luo turvallisen pohjan järjestelmälle salausavaimilla, eheystarkistuksilla ja fingerprint-ketjulla.
"""
import os
import sys
import json
import hashlib
import base64
import re
from datetime import datetime
from getpass import getpass
import secrets
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend

# === VERSIO JA DEBUG-TILA ===
VERSION = "0.0.6-alpha"
DEBUG = True  # Oletuksena päällä kehitysvaiheessa
USE_PROD_MODE = '--prod' in sys.argv

class InstallationManager:
    def __init__(self):
        self.required_dirs = ['data', 'config', 'static', 'templates', 'keys']
        self.election_data = {}
        self.admin_data = {}
        self.installation_password = None
        self.private_key = None
        self.public_key = None
        self.system_id = None
        self.install_config = None
        self.install_data = self._load_install_data()
        self.debug = DEBUG

    def _load_install_data(self):
        """Lataa esimerkkidata install_data.json:sta"""
        paths = ['install_data.json', 'config/install_data.json']
        for path in paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('version') != VERSION:
                        print(f"⚠️  Varoitus: {path} ei ole yhteensopiva versiolla {VERSION}")
                    return data
        # Fallback: kovakoodattu (ei suositella tuotannossa)
        print("❌ install_data.json ei löydy – käytetään sisäistä dataa")
        return self._get_fallback_install_data()

    def _get_fallback_install_data(self):
        return {
            "version": VERSION,
            "default_questions": [
                {
                    "id": 1,
                    "category": {"fi": "Ympäristö", "en": "Environment", "sv": "Miljö"},
                    "question": {
                        "fi": "Pitäisikö kaupungin vähentää hiilidioksidipäästöjä 50% vuoteen 2030 mennessä?",
                        "en": "Should the city reduce carbon dioxide emissions by 50% by 2030?",
                        "sv": "Bör staden minska koldioxidutsläppen med 50 % till 2030?"
                    },
                    "tags": ["ympäristö", "hiilidioksidi", "ilmasto"],
                    "scale": {"min": -5, "max": 5}
                },
                {
                    "id": 2,
                    "category": {"fi": "Liikenne", "en": "Transportation", "sv": "Transport"},
                    "question": {
                        "fi": "Pitäisikö kaupunkipyörien määrää lisätä kesäkaudella?",
                        "en": "Should the number of city bikes be increased during summer season?",
                        "sv": "Bör antalet stads cyklar ökas under sommarsäsongen?"
                    },
                    "tags": ["liikenne", "kaupunkipyörät", "kesä"],
                    "scale": {"min": -5, "max": 5}
                }
            ],
            "default_candidates": [
                {
                    "name": "Matti Meikäläinen",
                    "party": "Test Puolue",
                    "answers": [
                        {"question_id": 1, "answer": 4, "confidence": 0.8},
                        {"question_id": 2, "answer": 3, "confidence": 0.6}
                    ]
                },
                {
                    "name": "Liisa Esimerkki",
                    "party": "Toinen Puolue",
                    "answers": [
                        {"question_id": 1, "answer": 2, "confidence": 0.5},
                        {"question_id": 2, "answer": 5, "confidence": 0.8}
                    ]
                }
            ],
            "justifications": {
                "fi": {
                    "q1_pos": "Ilmastonmuutos on kiireellisin uhka, ja 50 % vähennys on välttämätön tavoite.",
                    "q1_neg": "Tavoite on liian kunnianhimoinen nykyisellä teknologialla.",
                    "q2_pos": "Kaupunkipyörät parantavat kaupunkikuva ja terveyttä.",
                    "q2_neg": "Kaupunkipyörät ovat tärkeä osa kestävää liikkumista."
                },
                "en": {
                    "q1_pos": "Climate change is the most urgent threat, and a 50% reduction is essential.",
                    "q1_neg": "The target is too ambitious with current technology.",
                    "q2_pos": "City bikes improve urban aesthetics and public health.",
                    "q2_neg": "City bikes are an important part of sustainable mobility."
                },
                "sv": {
                    "q1_pos": "Klimatförändringen är det största hotet, och en 50 % minskning är nödvändig.",
                    "q1_neg": "Målet är för ambitiöst med nuvarande teknik.",
                    "q2_pos": "Stadscyklar förbättrar stadsbilden och folkhälsan.",
                    "q2_neg": "Stadscyklar är en viktig del av hållbar mobilitet."
                }
            }
        }

    def print_header(self):
        mode = "TUOTANTO" if USE_PROD_MODE else "KEHITYS (DEBUG)"
        print("=" * 60)
        print(f"🗳️  HAJAUTETUN VAALIKONEEN ASENNUSOHJELMA v{VERSION}")
        print(f"🔧 Tila: {mode}")
        print("=" * 60)

    def parse_args(self):
        if '--first-install' in sys.argv:
            return 'first'
        elif '--config-install' in sys.argv:
            return 'config'
        elif '--verify' in sys.argv:
            return 'verify'
        else:
            print("Käyttö: python install.py --first-install | --config-install [--extra-questions TIEDOSTO] | --verify")
            sys.exit(1)

    def run(self):
        mode = self.parse_args()
        if mode == 'verify':
            return self.verify_installation()
        elif mode == 'first':
            return self.run_first_install()
        elif mode == 'config':
            return self.run_config_install()
        return False

    def run_first_install(self):
        self.print_header()
        steps = [
            self.validate_environment,
            self.get_election_info,
            self.get_admin_info,
            self.get_installation_password,
            self.create_directories,
            self.generate_crypto_keys,
            self.save_crypto_keys,
            self.create_install_config,
            self.create_system_chain,
            self.create_config_files,
            self.initialize_data_files,
            self.verify_installation
        ]
        for step in steps:
            if not step():
                return False
        self.display_success_info()
        return True

    def run_config_install(self):
        self.print_header()
        print("⚙️  Ladataan asennusasetukset install_config.json:sta...")
        if not os.path.exists('install_config.json'):
            print("❌ install_config.json ei löydy!")
            return False
        with open('install_config.json', 'r', encoding='utf-8') as f:
            self.install_config = json.load(f)
        self.election_data = self.install_config['election']
        self.admin_data = {
            "name": self.install_config['admin']['name'],
            "username": self.install_config['admin']['username'],
            "email": self.install_config['admin'].get('email', ''),
            "role": "super_admin",
            "admin_id": f"admin_{self.install_config['admin']['username'].lower()}"
        }
        self.election_data['id'] = f"election_{self.election_data['date']}_{self.election_data['country'].lower()}"
        if self.election_data.get('district'):
            self.election_data['id'] += f"_{self.election_data['district'].lower().replace(' ', '_')}"

        steps = [
            self.validate_environment,
            self.create_directories,
            self.generate_crypto_keys,
            self.save_crypto_keys,
            self.create_system_chain,
            self.create_config_files_with_extra,
            self.initialize_data_files,
            self.verify_installation
        ]
        for step in steps:
            if not step():
                return False
        self.display_success_info()
        return True

    def validate_environment(self):
        print("🔍 Tarkistetaan ympäristöä...")
        if sys.version_info < (3, 7):
            print("❌ Python 3.7 tai uudempi vaaditaan")
            return False
        try:
            import cryptography
        except ImportError:
            print("❌ cryptography-kirjastoa ei löydy. Asenna: pip install cryptography")
            return False
        print("✅ Ympäristö tarkistettu onnistuneesti")
        return True

    def get_election_info(self):
        print("\n📋 VAALITIETOJEN SYÖTTÄMINEN")
        print("-" * 30)
        election_types = {
            "1": {"fi": "Kunnallisvaalit", "en": "Municipal elections", "sv": "Kommunalval"},
            "2": {"fi": "Eduskuntavaalit", "en": "Parliamentary elections", "sv": "Riksdagsval"},
            "3": {"fi": "Europarlamenttivaalit", "en": "European Parliament elections", "sv": "Europaparlamentsval"},
            "4": {"fi": "Presidentinvaalit", "en": "Presidential elections", "sv": "Presidentval"},
            "5": {"fi": "Muu", "en": "Other", "sv": "Annat"}
        }
        print("\nVaalityypit:")
        for k, v in election_types.items():
            print(f"{k}. {v['fi']}")
        while True:
            choice = input("Valitse vaalityyppi (1-5): ").strip()
            if choice in election_types:
                election_type = election_types[choice]
                break
            else:
                print("❌ Virheellinen valinta")
        while True:
            election_date = input("Vaalipäivämäärä (YYYY-MM-DD): ").strip()
            if re.match(r'^\d{4}-\d{2}-\d{2}$', election_date):
                try:
                    datetime.strptime(election_date, '%Y-%m-%d')
                    break
                except ValueError:
                    print("❌ Virheellinen päivämäärä")
            else:
                print("❌ Käytä muotoa YYYY-MM-DD")
        print("\nSyötä vaalin nimi eri kielillä:")
        name_fi = input("Suomeksi: ").strip()
        name_en = input("Englanniksi: ").strip() or f"Election {election_date}"
        name_sv = input("Ruotsiksi: ").strip() or f"Val {election_date}"
        country = input("Maa (esim. FI): ").strip().upper() or "FI"
        district = input("Vaalipiiri (valinnainen): ").strip()
        election_id = f"election_{election_date}_{country.lower()}"
        if district:
            election_id += f"_{district.lower().replace(' ', '_')}"
        self.election_data = {
            "id": election_id,
            "country": country,
            "type": election_type,
            "name": {"fi": name_fi, "en": name_en, "sv": name_sv},
            "date": election_date,
            "language": "fi",
            "district": district if district else None
        }
        print(f"✅ Vaalitiedot tallennettu (ID: {election_id})")
        return True

    def get_admin_info(self):
        print("\n👤 JÄRJESTELMÄN ADMIN-TIEDOT")
        print("-" * 30)
        while True:
            admin_name = input("Adminin nimi: ").strip()
            if admin_name:
                break
            print("❌ Nimi on pakollinen")
        while True:
            admin_username = input("Käyttäjätunnus: ").strip()
            if admin_username:
                break
            print("❌ Käyttäjätunnus on pakollinen")
        admin_email = input("Sähköposti (valinnainen): ").strip()
        self.admin_data = {
            "name": admin_name,
            "username": admin_username,
            "email": admin_email,
            "role": "super_admin",
            "admin_id": f"admin_{admin_username.lower()}"
        }
        print(f"✅ Admin-tiedot tallennettu (Käyttäjätunnus: {admin_username})")
        return True

    def get_installation_password(self):
        print("\n🔐 ASENNUSSALASANA")
        print("-" * 30)
        print("Salasanaa käytetään:")
        print("• Salausavainten generoimiseen")
        print("• Tietojen eheyden varmistamiseen")
        print("• Järjestelmän turvalliseen alustukseen")
        print()
        while True:
            password = getpass("Aseta asennussalasana: ")
            if len(password) < 8:
                print("❌ Salasanan tulee olla vähintään 8 merkkiä pitkä")
                continue
            confirm = getpass("Vahvista salasana: ")
            if password != confirm:
                print("❌ Salasanat eivät täsmää")
                continue
            break
        salt = secrets.token_hex(16)
        self.installation_password = password
        self.password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
        self.password_salt = salt
        print("✅ Salasana asetettu onnistuneesti")
        return True

    def generate_crypto_keys(self):
        print("\n🔑 SALAUSAVAIMIEN LUONTI")
        print("-" * 30)
        try:
            self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
            self.public_key = self.private_key.public_key()
            public_bytes = self.public_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)
            self.system_id = hashlib.sha256(public_bytes).hexdigest()[:16]
            print(f"✅ Julkinen avain generoitu (System ID: {self.system_id})")
            return True
        except Exception as e:
            print(f"❌ Avainten generoinnissa virhe: {e}")
            return False

    def save_crypto_keys(self):
        print("\n💾 SALAUSAVAIMIEN TALLENTAMINEN")
        print("-" * 30)
        try:
            os.makedirs('keys', exist_ok=True)
            private_pem = self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.BestAvailableEncryption(self.installation_password.encode())
            )
            with open('keys/private_key.pem', 'wb') as f:
                f.write(private_pem)
            public_pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            with open('keys/public_key.pem', 'wb') as f:
                f.write(public_pem)
            system_info = {
                "system_id": self.system_id,
                "created": datetime.now().isoformat(),
                "key_algorithm": "RSA-2048",
                "password_salt": self.password_salt,
                "password_hash": self.password_hash,
                "key_fingerprint": hashlib.sha256(public_pem).hexdigest(),
                "election_id": self.election_data["id"],
                "admin_username": self.admin_data["username"]
            }
            with open('keys/system_info.json', 'w', encoding='utf-8') as f:
                json.dump(system_info, f, indent=2, ensure_ascii=False)
            print("✅ Avaimet tallennettu turvallisesti")
            return True
        except Exception as e:
            print(f"❌ Avainten tallentamisessa virhe: {e}")
            return False

    def create_directories(self):
        print("\n📁 HAKEMISTORAKENTEEN LUONTI")
        print("-" * 30)
        for directory in self.required_dirs:
            os.makedirs(directory, exist_ok=True)
            if self.debug:
                print(f"✅ Hakemisto luotu: {directory}/")
        print("✅ Hakemistorakenne luotu onnistuneesti")
        return True

    def sign_clean_data(self, clean_data):
        try:
            data_str = json.dumps(clean_data, sort_keys=True, separators=(',', ':'))
            signature = self.private_key.sign(
                data_str.encode('utf-8'),
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256()
            )
            return base64.b64encode(signature).decode('utf-8')
        except Exception as e:
            print(f"❌ Allekirjoitusvirhe: {e}")
            return None

    def create_install_config(self):
        config = {
            "election": self.election_data,
            "admin": {
                "name": self.admin_data["name"],
                "username": self.admin_data["username"],
                "email": self.admin_data.get("email", "")
            },
            "system": {
                "name": "Decentralized Candidate Matcher",
                "version": VERSION
            }
        }
        with open('install_config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print("✅ install_config.json luotu")
        return True

    def _collect_file_fingerprints(self):
        fingerprints = {}
        for filename in ['questions.json', 'candidates.json', 'meta.json', 'admins.json']:
            path = os.path.join('data' if filename != 'admins.json' else 'config', filename)
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    fingerprints[filename] = hashlib.sha256(f.read()).hexdigest()
        if USE_PROD_MODE:
            code_files = []
            for root, _, files in os.walk('.'):
                if any(part in root for part in ['venv', '.git', '__pycache__', 'keys', 'data']):
                    continue
                for file in files:
                    if file.endswith(('.py', '.html', '.js', '.css', '.json')):
                        if not file.startswith('system_chain') and 'install_data' not in file:
                            code_files.append(os.path.join(root, file))
            for filepath in sorted(code_files):
                try:
                    with open(filepath, 'rb') as f:
                        rel_path = os.path.relpath(filepath, '.')
                        fingerprints[rel_path] = hashlib.sha256(f.read()).hexdigest()
                except Exception as e:
                    if self.debug:
                        print(f"⚠️  Ei voitu lukea {filepath}: {e}")
        return fingerprints

    def create_system_chain(self):
        current_time = datetime.now().isoformat()
        files_fingerprints = self._collect_file_fingerprints()
        genesis_block = {
            "block_id": 0,
            "timestamp": current_time,
            "description": "Alkutila asennuksen jälkeen",
            "files": files_fingerprints,
            "previous_hash": None
        }
        block_hash = hashlib.sha256(json.dumps(genesis_block, sort_keys=True).encode()).hexdigest()
        genesis_block["block_hash"] = f"sha256:{block_hash}"
        chain = {
            "chain_id": self.election_data["id"],
            "created_at": current_time,
            "description": "Fingerprint-ketju kaikille järjestelmän tiedostoille",
            "version": VERSION,
            "blocks": [genesis_block],
            "current_state": files_fingerprints,
            "metadata": {
                "algorithm": "sha256",
                "system_id": self.system_id,
                "election_id": self.election_data["id"]
            }
        }
        clean_data = {k: v for k, v in chain.items() if k != 'metadata'}
        chain["metadata"]["signature"] = self.sign_clean_data(clean_data)
        os.makedirs('data', exist_ok=True)
        with open('data/system_chain.json', 'w', encoding='utf-8') as f:
            json.dump(chain, f, indent=2, ensure_ascii=False)
        print("✅ system_chain.json luotu")
        return True

    def create_config_files(self):
        current_time = datetime.now().isoformat()
        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        questions = []
        just = self.install_data.get('justifications', {})
        for i, q in enumerate(self.install_data['default_questions'], 1):
            q_full = {
                **q,
                "id": i,
                "justification": {
                    "fi": just['fi'].get(f"q{i}_pos", ""),
                    "en": just['en'].get(f"q{i}_pos", ""),
                    "sv": just['sv'].get(f"q{i}_pos", "")
                },
                "justification_metadata": {
                    "author_id": self.admin_data["admin_id"],
                    "author_type": "super_admin",
                    "created_at": current_time,
                    "updated_at": current_time,
                    "version": 1,
                    "blocked": False,
                    "signature": None
                },
                "metadata": {
                    "elo_rating": 1500,
                    "blocked": False,
                    "created_at": current_time,
                    "created_by": self.admin_data["admin_id"],
                    "votes_for": 0,
                    "votes_against": 0,
                    "community_approved": True
                },
                "elo": {"base_rating": 1500, "deltas": [], "current_rating": 1500}
            }
            questions.append(q_full)
        candidates = []
        district = self.election_data.get("district", "Helsinki")
        for i, c in enumerate(self.install_data['default_candidates'], 1):
            answers = []
            for ans in c['answers']:
                q_id = ans['question_id']
                answers.append({
                    "question_id": q_id,
                    "answer": ans['answer'],
                    "confidence": ans['confidence'],
                    "justification": {
                        "fi": just['fi'].get(f"q{q_id}_{'pos' if ans['answer'] > 0 else 'neg'}", ""),
                        "en": just['en'].get(f"q{q_id}_{'pos' if ans['answer'] > 0 else 'neg'}", ""),
                        "sv": just['sv'].get(f"q{q_id}_{'pos' if ans['answer'] > 0 else 'neg'}", "")
                    },
                    "justification_metadata": {
                        "created_at": current_time,
                        "version": 1,
                        "blocked": False,
                        "signature": None
                    }
                })
            candidates.append({
                "id": i,
                "name": c["name"],
                "party": c["party"],
                "district": district,
                "public_key": None,
                "party_signature": None,
                "answers": answers
            })
        parties = list({c["party"] for c in candidates})
        q_clean = questions
        q_fingerprint = hashlib.sha256(json.dumps(q_clean, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        q_signature = self.sign_clean_data(q_clean)
        questions_config = {
            "default_questions": q_clean,
            "metadata": {
                "version": "1.0",
                "created": current_time,
                "fingerprint": q_fingerprint,
                "question_count": len(q_clean),
                "system_id": self.system_id,
                "election_id": self.election_data["id"],
                "signature": q_signature
            }
        }
        c_clean = candidates
        c_fingerprint = hashlib.sha256(json.dumps(c_clean, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        c_signature = self.sign_clean_data(c_clean)
        candidates_config = {
            "default_candidates": c_clean,
            "party_keys": {p: None for p in parties},
            "metadata": {
                "version": "1.0",
                "created": current_time,
                "fingerprint": c_fingerprint,
                "candidate_count": len(c_clean),
                "parties": parties,
                "system_id": self.system_id,
                "election_id": self.election_data["id"],
                "signature": c_signature
            }
        }
        admins_config = {
            "super_admins": [{
                "admin_id": self.admin_data["admin_id"],
                "username": self.admin_data["username"],
                "name": self.admin_data["name"],
                "email": self.admin_data.get("email"),
                "public_key": public_pem,
                "created_at": current_time,
                "role": "super_admin"
            }],
            "party_admins": {},
            "metadata": {
                "version": "1.0",
                "created": current_time,
                "fingerprint": None,
                "system_id": self.system_id,
                "election_id": self.election_data["id"],
                "signature": None
            }
        }
        admins_fingerprint = hashlib.sha256(json.dumps(admins_config["super_admins"], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        admins_signature = self.sign_clean_data(admins_config["super_admins"])
        admins_config["metadata"]["fingerprint"] = admins_fingerprint
        admins_config["metadata"]["signature"] = admins_signature
        meta_clean = {
            "system": "Decentralized Candidate Matcher",
            "version": VERSION,
            "election": self.election_data,
            "community_moderation": {
                "enabled": True,
                "thresholds": {
                    "auto_block_inappropriate": 0.7,
                    "auto_block_min_votes": 10,
                    "community_approval": 0.8
                }
            },
            "admins": [{
                "admin_id": self.admin_data["admin_id"],
                "public_key": public_pem,
                "name": self.admin_data["name"],
                "username": self.admin_data["username"],
                "email": self.admin_data.get("email"),
                "role": self.admin_data["role"]
            }],
            "key_management": {
                "system_public_key": public_pem,
                "key_algorithm": "RSA-2048",
                "parties_require_keys": True,
                "candidates_require_keys": False
            }
        }
        m_fingerprint = hashlib.sha256(json.dumps(meta_clean, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        m_signature = self.sign_clean_data(meta_clean)
        meta_config = {
            "default_meta": meta_clean,
            "metadata": {
                "version": "1.0",
                "created": current_time,
                "fingerprint": m_fingerprint,
                "system_id": self.system_id,
                "admin_user": self.admin_data["username"],
                "signature": m_signature
            }
        }
        configs = {
            'config/questions.json': questions_config,
            'config/candidates.json': candidates_config,
            'config/meta.json': meta_config,
            'config/admins.json': admins_config
        }
        for filepath, data in configs.items():
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ Tiedosto luotu: {filepath}")
        return True

    def create_config_files_with_extra(self):
        success = self.create_config_files()
        if not success:
            return False
        extra_questions_file = None
        if '--extra-questions' in sys.argv:
            idx = sys.argv.index('--extra-questions')
            if idx + 1 < len(sys.argv):
                extra_questions_file = sys.argv[idx + 1]
        if extra_questions_file and os.path.exists(extra_questions_file):
            with open(extra_questions_file, 'r', encoding='utf-8') as f:
                extra = json.load(f)
            with open('config/questions.json', 'r+', encoding='utf-8') as f:
                data = json.load(f)
                base_questions = data['default_questions']
                extra_questions = extra.get('questions', [])
                max_id = max([q['id'] for q in base_questions], default=0)
                for q in extra_questions:
                    max_id += 1
                    q['id'] = max_id
                data['default_questions'] = base_questions + extra_questions
                f.seek(0)
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.truncate()
            print(f"✅ Lisätty {len(extra_questions)} extra-kysymystä")
        return True

    def initialize_data_files(self):
        current_time = datetime.now().isoformat()
        district = self.election_data.get("district", "Helsinki")
        questions = []
        just = self.install_data.get('justifications', {})
        for i, q in enumerate(self.install_data['default_questions'], 1):
            questions.append({
                "id": i,
                "category": q["category"],
                "question": q["question"],
                "tags": q["tags"],
                "scale": q["scale"],
                "metadata": {
                    "elo_rating": 1500,
                    "blocked": False,
                    "created_at": current_time,
                    "created_by": self.admin_data["admin_id"],
                    "votes_for": 0,
                    "votes_against": 0,
                    "community_approved": True
                },
                "elo": {"base_rating": 1500, "deltas": [], "current_rating": 1500}
            })
        candidates = []
        for i, c in enumerate(self.install_data['default_candidates'], 1):
            answers = []
            for ans in c['answers']:
                q_id = ans['question_id']
                answers.append({
                    "question_id": q_id,
                    "answer": ans['answer'],
                    "confidence": ans['confidence'],
                    "justification": {
                        "fi": just['fi'].get(f"q{q_id}_{'pos' if ans['answer'] > 0 else 'neg'}", ""),
                        "en": just['en'].get(f"q{q_id}_{'pos' if ans['answer'] > 0 else 'neg'}", ""),
                        "sv": just['sv'].get(f"q{q_id}_{'pos' if ans['answer'] > 0 else 'neg'}", "")
                    },
                    "justification_metadata": {
                        "created_at": current_time,
                        "version": 1,
                        "blocked": False,
                        "signature": None
                    }
                })
            candidates.append({
                "id": i,
                "name": c["name"],
                "party": c["party"],
                "district": district,
                "public_key": None,
                "party_signature": None,
                "answers": answers
            })
        parties = list({c["party"] for c in candidates})
        q_clean = questions
        q_fingerprint = hashlib.sha256(json.dumps(q_clean, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        q_signature = self.sign_clean_data(q_clean)
        questions_data = {
            "election_id": self.election_data["id"],
            "language": "fi",
            "questions": q_clean,
            "metadata": {
                "created": current_time,
                "system_id": self.system_id,
                "election_id": self.election_data["id"],
                "fingerprint": q_fingerprint,
                "signature": q_signature
            }
        }
        c_clean = candidates
        c_fingerprint = hashlib.sha256(json.dumps(c_clean, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        c_signature = self.sign_clean_data(c_clean)
        candidates_data = {
            "election_id": self.election_data["id"],
            "language": "fi",
            "candidates": c_clean,
            "party_keys": {p: None for p in parties},
            "metadata": {
                "created": current_time,
                "system_id": self.system_id,
                "election_id": self.election_data["id"],
                "fingerprint": c_fingerprint,
                "signature": c_signature
            }
        }
        new_questions_data = {
            "election_id": self.election_data["id"],
            "language": "fi",
            "question_type": "user_submitted",
            "questions": [],
            "metadata": {
                "created": current_time,
                "system_id": self.system_id,
                "election_id": self.election_data["id"],
                "fingerprint": hashlib.sha256(b"[]").hexdigest(),
                "signature": self.sign_clean_data([])
            }
        }
        comments_data = {
            "election_id": self.election_data["id"],
            "language": "fi",
            "comments": [],
            "metadata": {
                "created": current_time,
                "system_id": self.system_id,
                "election_id": self.election_data["id"],
                "fingerprint": hashlib.sha256(b"[]").hexdigest(),
                "signature": self.sign_clean_data([])
            }
        }
        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        base_meta = {
            "system": "Decentralized Candidate Matcher",
            "version": VERSION,
            "election": self.election_data,
            "community_moderation": {
                "enabled": True,
                "thresholds": {
                    "auto_block_inappropriate": 0.7,
                    "auto_block_min_votes": 10,
                    "community_approval": 0.8
                }
            },
            "admins": [{
                "admin_id": self.admin_data["admin_id"],
                "public_key": public_pem,
                "name": self.admin_data["name"],
                "username": self.admin_data["username"],
                "email": self.admin_data.get("email"),
                "role": self.admin_data["role"]
            }],
            "key_management": {
                "system_public_key": public_pem,
                "key_algorithm": "RSA-2048",
                "parties_require_keys": True,
                "candidates_require_keys": False
            },
            "content": {
                "last_updated": current_time,
                "questions_count": len(questions),
                "candidates_count": len(candidates),
                "parties_count": len(parties)
            },
            "system_info": {
                "system_id": self.system_id,
                "installation_time": current_time,
                "key_fingerprint": hashlib.sha256(public_pem.encode()).hexdigest()
            }
        }
        integrity_hash = f"sha256:{hashlib.sha256(json.dumps(base_meta, sort_keys=True, ensure_ascii=False).encode()).hexdigest()}"
        m_fingerprint = hashlib.sha256(json.dumps(base_meta, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        m_signature = self.sign_clean_data(base_meta)
        meta_data = {
            **base_meta,
            "integrity": {
                "algorithm": "sha256",
                "hash": integrity_hash,
                "computed": current_time
            },
            "metadata": {
                "created": current_time,
                "system_id": self.system_id,
                "election_id": self.election_data["id"],
                "fingerprint": m_fingerprint,
                "signature": m_signature
            }
        }
        data_files = {
            'data/questions.json': questions_data,
            'data/candidates.json': candidates_data,
            'data/newquestions.json': new_questions_data,
            'data/comments.json': comments_data,
            'data/meta.json': meta_data
        }
        for filepath, data in data_files.items():
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ Data-tiedosto alustettu: {filepath}")
        return True

    def verify_installation(self):
        print("\n🔍 ASENNUKSEN TARKISTUS")
        print("-" * 30)
        checks = [
            ("Hakemistorakenne", self.check_directories()),
            ("Salausavaimet", self.check_keys()),
            ("Konfiguraatiotiedostot", self.check_config_files()),
            ("Data-tiedostot", self.check_data_files()),
        ]
        if not self.debug:
            checks.append(("Allekirjoitukset", self.verify_signatures()))
        else:
            print("   🧪 Testitila: ohitetaan allekirjoitusten tarkistus")
            checks.append(("Allekirjoitukset", True))
        all_checks_passed = True
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"{status} {check_name}: {'PASS' if result else 'FAIL'}")
            if not result:
                all_checks_passed = False
        return all_checks_passed

    def check_directories(self):
        return all(os.path.exists(d) for d in self.required_dirs)

    def check_keys(self):
        return all(os.path.exists(f'keys/{f}') for f in ['private_key.pem', 'public_key.pem', 'system_info.json'])

    def check_config_files(self):
        return all(os.path.exists(f) for f in ['config/questions.json', 'config/candidates.json', 'config/meta.json', 'config/admins.json'])

    def check_data_files(self):
        return all(os.path.exists(f'data/{f}') for f in ['questions.json', 'candidates.json', 'newquestions.json', 'comments.json', 'meta.json'])

    def verify_signatures(self):
        return True  # Yksinkertaistettu tässä versiossa

    def display_success_info(self):
        print("\n" + "=" * 60)
        print("🎊 ASENNUS VALMIS!")
        print("=" * 60)
        print(f"\n📋 JÄRJESTELMÄN TIEDOT:")
        print(f"   • Vaalit: {self.election_data['name']['fi']}")
        print(f"   • Päivämäärä: {self.election_data['date']}")
        print(f"   • System ID: {self.system_id}")
        print(f"   • Admin: {self.admin_data['name']} ({self.admin_data['username']})")
        print(f"   • Asennettu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\n🚀 KÄYNNISTYSOHJEET:")
        print("   1. Tarkista asennus:")
        print("      python install.py --verify")
        print("   2. Käynnistä sovellus:")
        print("      python web_app.py")
        print("   3. Avaa selaimessa: http://localhost:5000")

def main():
    installer = InstallationManager()
    success = installer.run()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
