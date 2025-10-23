#!/usr/bin/env python3
"""
Vaalikoneen asennus- ja alustusskripti
Luo turvallisen pohjan järjestelmälle salausavaimilla ja eheystarkistuksilla
"""

import os
import json
import hashlib
import base64
from datetime import datetime
from getpass import getpass
import secrets
import string
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import sys
import re


class InstallationManager:
    def __init__(self):
        self.required_dirs = ['data', 'config', 'static', 'templates', 'keys']
        self.election_data = {}
        self.admin_data = {}
        self.test_mode = os.environ.get('VAALIKONE_TEST_MODE') == '1'
        
    def print_header(self):
        """Näyttää asennuksen otsikon"""
        print("=" * 60)
        print("🗳️  HAJAUTETUN VAALIKONEEN ASENNUSOHJELMA")
        print("=" * 60)
        print()

    def validate_environment(self):
        """Tarkistaa ympäristön ja riippuvuudet"""
        print("🔍 Tarkistetaan ympäristöä...")
        
        if sys.version_info < (3, 7):
            print("❌ Python 3.7 tai uudempi vaaditaan")
            return False
        
        try:
            import cryptography
            print("✅ cryptography-kirjasto saatavilla")
        except ImportError:
            print("❌ cryptography-kirjastoa ei löydy. Asenna: pip install cryptography")
            return False
        
        print("✅ Ympäristö tarkistettu onnistuneesti")
        return True

    def get_election_info(self):
        """Kysyy vaalien tiedot interaktiivisesti"""
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
        """Kysyy admin-tiedot interaktiivisesti"""
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
        """Kysyy asennussalasanaa interaktiivisesti"""
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
        self.installation_password = password  # Tallenna alkuperäinen salasana avainten salaamista varten
        self.password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
        self.password_salt = salt
        
        print("✅ Salasana asetettu onnistuneesti")
        return True

    def generate_crypto_keys(self):
        """Generoi julkisen ja yksityisen salausavaimen"""
        print("\n🔑 SALAUSAVAIMIEN LUONTI")
        print("-" * 30)
        
        try:
            self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
            self.public_key = self.private_key.public_key()
            public_bytes = self.public_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)
            self.system_id = hashlib.sha256(public_bytes).hexdigest()[:16]
            print(f"✅ Julkinen avain generoitu (System ID: {self.system_id})")
            print("✅ Yksityinen avain generoitu")
            return True
        except Exception as e:
            print(f"❌ Avainten generoinnissa virhe: {e}")
            return False

    def save_crypto_keys(self):
        """Tallentaa salausavaimet turvallisesti"""
        print("\n💾 SALAUSAVAIMIEN TALLENTAMINEN")
        print("-" * 30)
        
        try:
            os.makedirs('keys', exist_ok=True)
            
            # Salaa yksityinen avain asennussalasanalla
            private_pem = self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.BestAvailableEncryption(
                    self.installation_password.encode()
                )
            )
            with open('keys/private_key.pem', 'wb') as f:
                f.write(private_pem)
            
            # Julkinen avain tallennetaan salaamattomana
            public_pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            with open('keys/public_key.pem', 'wb') as f:
                f.write(public_pem)
            
            # Tallenna järjestelmätiedot
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
            print("📁 Hakemisto: keys/")
            print("   - private_key.pem (salattu)")
            print("   - public_key.pem")
            print("   - system_info.json")
            return True
        except Exception as e:
            print(f"❌ Avainten tallentamisessa virhe: {e}")
            return False

    def load_public_key(self):
        """Lataa julkisen avaimen keys/public_key.pem -tiedostosta"""
        try:
            with open('keys/public_key.pem', 'rb') as f:
                self.public_key = serialization.load_pem_public_key(
                    f.read(),
                    backend=default_backend()
                )
            return True
        except Exception as e:
            print(f"❌ Julkisen avaimen lataus epäonnistui: {e}")
            return False

    def load_private_key(self):
        """Lataa yksityisen avaimen salasanalla"""
        try:
            if not hasattr(self, 'installation_password'):
                print("🔐 Salasana tarvitaan yksityisen avaimen lataamiseen")
                password = getpass("Syötä asennussalasana: ")
                self.installation_password = password
            
            with open('keys/private_key.pem', 'rb') as f:
                self.private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=self.installation_password.encode(),
                    backend=default_backend()
                )
            print("✅ Yksityinen avain ladattu onnistuneesti")
            return True
        except Exception as e:
            print(f"❌ Yksityisen avaimen lataus epäonnistui: {e}")
            return False

    def create_directories(self):
        """Luo tarvittavat hakemistot"""
        print("\n📁 HAKEMISTORAKENTEEN LUONTI")
        print("-" * 30)
        
        for directory in self.required_dirs:
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"✅ Hakemisto luotu: {directory}/")
            except Exception as e:
                print(f"❌ Hakemiston luonti epäonnistui ({directory}): {e}")
                return False
        
        print("✅ Hakemistorakenne luotu onnistuneesti")
        return True

    def sign_clean_data(self, clean_data):
        """Allekirjoittaa vain puhdasta dataa (ei metadataa!)"""
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

    def create_config_files(self):
        """Luo konfiguraatiotiedostot ilman metatietojen sisällyttämistä allekirjoitukseen"""
        print("\n📄 KONFIGURAATIOTIEDOSTOJEN LUONTI")
        print("-" * 30)
        
        current_time = datetime.now().isoformat()
        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

        # --- QUESTIONS ---
        clean_questions = [
            {
                "id": 1,
                "category": {"fi": "Ympäristö", "en": "Environment", "sv": "Miljö"},
                "question": {
                    "fi": "Pitäisikö kaupungin vähentää hiilidioksidipäästöjä 50% vuoteen 2030 mennessä?",
                    "en": "Should the city reduce carbon dioxide emissions by 50% by 2030?",
                    "sv": "Bör staden minska koldioxidutsläppen med 50 % till 2030?"
                },
                "tags": ["ympäristö", "hiilidioksidi", "ilmasto"],
                "scale": {"min": -5, "max": 5},
                "justification": {
                    "fi": "Ilmastonmuutos vaatii kiireellisiä toimia kaupunkitasolla.",
                    "en": "Climate change requires urgent action at the municipal level.",
                    "sv": "Klimatförändringar kräver brådskande åtgärder på kommunal nivå."
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
                    "blocked_reason": None,
                    "created_at": current_time,
                    "created_by": self.admin_data["admin_id"],
                    "votes_for": 0,
                    "votes_against": 0,
                    "community_approved": True
                },
                "elo": {
                    "base_rating": 1500,
                    "deltas": [],
                    "current_rating": 1500
                }
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
                "scale": {"min": -5, "max": 5},
                "justification": {
                    "fi": "Kaupunkipyörät vähentävät liikenne ruuhkia ja saastumista.",
                    "en": "City bikes reduce traffic congestion and pollution.",
                    "sv": "Stadscyklar minskar trafikstockningar och föroreningar."
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
                    "blocked_reason": None,
                    "created_at": current_time,
                    "created_by": self.admin_data["admin_id"],
                    "votes_for": 0,
                    "votes_against": 0,
                    "community_approved": True
                },
                "elo": {
                    "base_rating": 1500,
                    "deltas": [],
                    "current_rating": 1500
                }
            }
        ]
        q_fingerprint = hashlib.sha256(json.dumps(clean_questions, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        q_signature = self.sign_clean_data(clean_questions)
        if q_signature is None:
            print("❌ Kysymysten allekirjoitus epäonnistui")
            return False
        questions_config = {
            "default_questions": clean_questions,
            "metadata": {
                "version": "1.0",
                "created": current_time,
                "fingerprint": q_fingerprint,
                "question_count": len(clean_questions),
                "system_id": self.system_id,
                "election_id": self.election_data["id"],
                "signature": q_signature
            }
        }

        # --- CANDIDATES ---
        district = self.election_data.get("district", "Helsinki")
        clean_candidates = [
            {
                "id": 1,
                "name": "Matti Meikäläinen",
                "party": "Test Puolue",
                "district": district,
                "public_key": None,
                "party_signature": None,
                "answers": [
                    {
                        "question_id": 1,
                        "answer": 4,
                        "confidence": 0.8,
                        "justification": {
                            "fi": "Ilmastonmuutos on kiireellisin uhka, ja 50 % vähennys on välttämätön tavoite.",
                            "en": "Climate change is the most urgent threat, and a 50% reduction is essential.",
                            "sv": "Klimatförändringen är det största hotet, och en 50 % minskning är nödvändig."
                        },
                        "justification_metadata": {
                            "created_at": current_time,
                            "version": 1,
                            "blocked": False,
                            "signature": None
                        }
                    },
                    {
                        "question_id": 2,
                        "answer": 3,
                        "confidence": 0.6,
                        "justification": {
                            "fi": "Kaupunkipyörät ovat tärkeä osa kestävää liikkumista.",
                            "en": "City bikes are an important part of sustainable mobility.",
                            "sv": "Stadscyklar är en viktig del av hållbar mobilitet."
                        },
                        "justification_metadata": {
                            "created_at": current_time,
                            "version": 1,
                            "blocked": False,
                            "signature": None
                        }
                    }
                ]
            },
            {
                "id": 2,
                "name": "Liisa Esimerkki",
                "party": "Toinen Puolue",
                "district": district,
                "public_key": None,
                "party_signature": None,
                "answers": [
                    {
                        "question_id": 1,
                        "answer": 2,
                        "confidence": 0.5,
                        "justification": {
                            "fi": "Tavoite on liian kunnianhimoinen nykyisellä teknologialla.",
                            "en": "The target is too ambitious with current technology.",
                            "sv": "Målet är för ambitiöst med nuvarande teknik."
                        },
                        "justification_metadata": {
                            "created_at": current_time,
                            "version": 1,
                            "blocked": False,
                            "signature": None
                        }
                    },
                    {
                        "question_id": 2,
                        "answer": 5,
                        "confidence": 0.8,
                        "justification": {
                            "fi": "Kaupunkipyörät parantavat kaupunkikuva ja terveyttä.",
                            "en": "City bikes improve urban aesthetics and public health.",
                            "sv": "Stadscyklar förbättrar stadsbilden och folkhälsan."
                        },
                        "justification_metadata": {
                            "created_at": current_time,
                            "version": 1,
                            "blocked": False,
                            "signature": None
                        }
                    }
                ]
            }
        ]
        parties = ["Test Puolue", "Toinen Puolue"]
        c_fingerprint = hashlib.sha256(json.dumps(clean_candidates, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        c_signature = self.sign_clean_data(clean_candidates)
        if c_signature is None:
            print("❌ Ehdokkaiden allekirjoitus epäonnistui")
            return False
        candidates_config = {
            "default_candidates": clean_candidates,
            "party_keys": {p: None for p in parties},
            "metadata": {
                "version": "1.0",
                "created": current_time,
                "fingerprint": c_fingerprint,
                "candidate_count": len(clean_candidates),
                "parties": parties,
                "system_id": self.system_id,
                "election_id": self.election_data["id"],
                "signature": c_signature
            }
        }

        # --- ADMINS ---
        admins_config = {
            "super_admins": [
                {
                    "admin_id": self.admin_data["admin_id"],
                    "username": self.admin_data["username"],
                    "name": self.admin_data["name"],
                    "email": self.admin_data.get("email"),
                    "public_key": public_pem,
                    "created_at": current_time,
                    "role": "super_admin"
                }
            ],
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

        # Tallenna tiedostot
        configs = {
            'config/questions.json': questions_config,
            'config/candidates.json': candidates_config,
            'config/meta.json': self._create_meta_config(current_time, public_pem),
            'config/admins.json': admins_config
        }

        for filepath, data in configs.items():
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ Tiedosto luotu: {filepath}")
            if 'fingerprint' in data.get('metadata', {}):
                print(f"   📊 Fingerprint: {data['metadata']['fingerprint'][:16]}...")

        print("✅ Konfiguraatiotiedostot luotu onnistuneesti")
        return True

    def _create_meta_config(self, current_time, public_pem):
        """Luo meta-konfiguraation"""
        clean_meta = {
            "system": "Decentralized Candidate Matcher",
            "version": "0.0.1",
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
        m_fingerprint = hashlib.sha256(json.dumps(clean_meta, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        m_signature = self.sign_clean_data(clean_meta)
        return {
            "default_meta": clean_meta,
            "metadata": {
                "version": "1.0",
                "created": current_time,
                "fingerprint": m_fingerprint,
                "system_id": self.system_id,
                "admin_user": self.admin_data["username"],
                "signature": m_signature
            }
        }

    def initialize_data_files(self):
        """Alustaa data-tiedostot"""
        print("\n🗃️  DATA-TIEDOSTOJEN ALUSTUS")
        print("-" * 30)
        
        try:
            district = self.election_data.get("district", "Helsinki")
            current_time = datetime.now().isoformat()
            
            # Questions
            clean_questions = [
                {
                    "id": 1,
                    "category": {"fi": "Ympäristö", "en": "Environment", "sv": "Miljö"},
                    "question": {
                        "fi": "Pitäisikö kaupungin vähentää hiilidioksidipäästöjä 50% vuoteen 2030 mennessä?",
                        "en": "Should the city reduce carbon dioxide emissions by 50% by 2030?",
                        "sv": "Bör staden minska koldioxidutsläppen med 50 % till 2030?"
                    },
                    "tags": ["ympäristö", "hiilidioksidi", "ilmasto"],
                    "scale": {"min": -5, "max": 5},
                    "metadata": {
                        "elo_rating": 1500,
                        "blocked": False,
                        "blocked_reason": None,
                        "created_at": current_time,
                        "created_by": self.admin_data["admin_id"],
                        "votes_for": 0,
                        "votes_against": 0,
                        "community_approved": True
                    },
                    "elo": {
                        "base_rating": 1500,
                        "deltas": [],
                        "current_rating": 1500
                    }
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
                    "scale": {"min": -5, "max": 5},
                    "metadata": {
                        "elo_rating": 1500,
                        "blocked": False,
                        "blocked_reason": None,
                        "created_at": current_time,
                        "created_by": self.admin_data["admin_id"],
                        "votes_for": 0,
                        "votes_against": 0,
                        "community_approved": True
                    },
                    "elo": {
                        "base_rating": 1500,
                        "deltas": [],
                        "current_rating": 1500
                    }
                }
            ]
            q_fingerprint = hashlib.sha256(json.dumps(clean_questions, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
            q_signature = self.sign_clean_data(clean_questions)
            questions_data = {
                "election_id": self.election_data["id"],
                "language": "fi",
                "questions": clean_questions,
                "metadata": {
                    "created": current_time,
                    "system_id": self.system_id,
                    "election_id": self.election_data["id"],
                    "fingerprint": q_fingerprint,
                    "signature": q_signature
                }
            }

            # Candidates
            clean_candidates = [
                {
                    "id": 1,
                    "name": "Matti Meikäläinen",
                    "party": "Test Puolue",
                    "district": district,
                    "public_key": None,
                    "party_signature": None,
                    "answers": [
                        {
                            "question_id": 1,
                            "answer": 4,
                            "confidence": 0.8,
                            "justification": {
                                "fi": "Ilmastonmuutos on kiireellisin uhka, ja 50 % vähennys on välttämätön tavoite.",
                                "en": "Climate change is the most urgent threat, and a 50% reduction is essential.",
                                "sv": "Klimatförändringen är det största hotet, och en 50 % minskning är nödvändig."
                            },
                            "justification_metadata": {
                                "created_at": current_time,
                                "version": 1,
                                "blocked": False,
                                "signature": None
                            }
                        },
                        {
                            "question_id": 2,
                            "answer": 3,
                            "confidence": 0.6,
                            "justification": {
                                "fi": "Kaupunkipyörät ovat tärkeä osa kestävää liikkumista.",
                                "en": "City bikes are an important part of sustainable mobility.",
                                "sv": "Stadscyklar är en viktig del av hållbar mobilitet."
                            },
                            "justification_metadata": {
                                "created_at": current_time,
                                "version": 1,
                                "blocked": False,
                                "signature": None
                            }
                        }
                    ]
                },
                {
                    "id": 2,
                    "name": "Liisa Esimerkki",
                    "party": "Toinen Puolue",
                    "district": district,
                    "public_key": None,
                    "party_signature": None,
                    "answers": [
                        {
                            "question_id": 1,
                            "answer": 2,
                            "confidence": 0.5,
                            "justification": {
                                "fi": "Tavoite on liian kunnianhimoinen nykyisellä teknologialla.",
                                "en": "The target is too ambitious with current technology.",
                                "sv": "Målet är för ambitiöst med nuvarande teknik."
                            },
                            "justification_metadata": {
                                "created_at": current_time,
                                "version": 1,
                                "blocked": False,
                                "signature": None
                            }
                        },
                        {
                            "question_id": 2,
                            "answer": 5,
                            "confidence": 0.8,
                            "justification": {
                                "fi": "Kaupunkipyörät parantavat kaupunkikuva ja terveyttä.",
                                "en": "City bikes improve urban aesthetics and public health.",
                                "sv": "Stadscyklar förbättrar stadsbilden och folkhälsan."
                            },
                            "justification_metadata": {
                                "created_at": current_time,
                                "version": 1,
                                "blocked": False,
                                "signature": None
                            }
                        }
                    ]
                }
            ]
            parties = ["Test Puolue", "Toinen Puolue"]
            c_fingerprint = hashlib.sha256(json.dumps(clean_candidates, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
            c_signature = self.sign_clean_data(clean_candidates)
            candidates_data = {
                "election_id": self.election_data["id"],
                "language": "fi",
                "candidates": clean_candidates,
                "party_keys": {p: None for p in parties},
                "metadata": {
                    "created": current_time,
                    "system_id": self.system_id,
                    "election_id": self.election_data["id"],
                    "fingerprint": c_fingerprint,
                    "signature": c_signature
                }
            }

            # New questions (empty)
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

            # Comments (empty)
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

            # === META DATA (KORJATTU) ===
            public_pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode('utf-8')
            
            base_meta = {
                "system": "Decentralized Candidate Matcher",
                "version": "0.0.1",
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
                    "questions_count": 2,
                    "candidates_count": 2,
                    "parties_count": 2
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

            print("✅ Data-tiedostot alustettu onnistuneesti")
            return True

        except Exception as e:
            print(f"❌ Data-tiedostojen alustus epäonnistui: {e}")
            import traceback
            print(f"❌ Ylimääräiset tiedot: {traceback.format_exc()}")
            return False

    def verify_installation(self):
        """Tarkistaa asennuksen onnistumisen"""
        print("\n🔍 ASENNUKSEN TARKISTUS")
        print("-" * 30)
        
        checks = [
            ("Hakemistorakenne", self.check_directories()),
            ("Salausavaimet", self.check_keys()),
            ("Konfiguraatiotiedostot", self.check_config_files()),
            ("Data-tiedostot", self.check_data_files()),
        ]
        
        if not self.test_mode:
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
        
        if all_checks_passed:
            print("\n🎉 ASENNUS ONNISTUI TÄYDELLISESTI!")
            return True
        else:
            print("\n⚠️  Asennuksessa havaittiin ongelmia")
            return False

    def check_directories(self):
        for directory in self.required_dirs:
            if not os.path.exists(directory):
                return False
        return True

    def check_keys(self):
        key_files = ['private_key.pem', 'public_key.pem', 'system_info.json']
        for key_file in key_files:
            if not os.path.exists(f'keys/{key_file}'):
                return False
        return True

    def check_config_files(self):
        for filepath in ['config/questions.json', 'config/candidates.json', 'config/meta.json', 'config/admins.json']:
            if not os.path.exists(filepath):
                return False
        return True

    def check_data_files(self):
        data_files = ['questions.json', 'candidates.json', 'newquestions.json', 'comments.json', 'meta.json']
        for data_file in data_files:
            if not os.path.exists(f'data/{data_file}'):
                return False
        return True

    def verify_signatures(self):
        """Tarkistaa allekirjoitukset vain puhdasta dataa käyttäen"""
        files_to_verify = [
            ('config/questions.json', 'default_questions'),
            ('config/candidates.json', 'default_candidates'),
            ('config/meta.json', 'default_meta'),
            ('config/admins.json', 'super_admins'),
            ('data/questions.json', 'questions'),
            ('data/candidates.json', 'candidates'),
            ('data/newquestions.json', 'questions'),
            ('data/comments.json', 'comments'),
            ('data/meta.json', None)  # erikoiskäsittely
        ]
        
        for filepath, data_key in files_to_verify:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    full_data = json.load(f)
                
                signature = full_data['metadata'].get('signature')
                if not signature:
                    print(f"   ❌ Allekirjoitus puuttuu: {filepath}")
                    return False

                if filepath == 'data/meta.json':
                    clean_data = full_data.copy()
                    clean_data.pop('metadata', None)
                    clean_data.pop('integrity', None)
                elif filepath == 'config/admins.json':
                    clean_data = full_data['super_admins']
                else:
                    if data_key not in full_data:
                        print(f"   ❌ Odottamaton rakenne: {filepath}")
                        return False
                    clean_data = full_data[data_key]

                data_str = json.dumps(clean_data, sort_keys=True, separators=(',', ':'))
                self.public_key.verify(
                    base64.b64decode(signature),
                    data_str.encode('utf-8'),
                    padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                    hashes.SHA256()
                )
            except Exception as e:
                print(f"   ❌ Allekirjoituksen varmistus epäonnistui: {filepath}")
                print(f"   ❌ Virhe: {e}")
                return False
        
        return True

    def display_success_info(self):
        print("\n" + "=" * 60)
        print("🎊 ASENNUS VALMIS!")
        print("=" * 60)
        print("\n📋 JÄRJESTELMÄN TIEDOT:")
        print(f"   • Vaalit: {self.election_data['name']['fi']}")
        print(f"   • Päivämäärä: {self.election_data['date']}")
        print(f"   • System ID: {self.system_id}")
        print(f"   • Admin: {self.admin_data['name']} ({self.admin_data['username']})")
        print(f"   • Asennettu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n🚀 KÄYNNISTYSOHJEET:")
        print("   1. Tarkista asennus:")
        print("      python install.py --verify")
        print("   2. Käynnistä sovellus:")
        print("      python web_app.py")
        print("   3. Avaa selaimessa: http://localhost:5000")
        print("\n🔐 SEURAAVAT VAIHEET:")
        print("   • Puolueet voivat lisätä julkiset avaimensa candidates.json:in")
        print("   • Ehdokkaat voivat lisätä julkiset avaimensa (valinnainen)")
        print("   • Käytä admin-paneelia lisätäksesi oikeat kysymykset ja ehdokkaat")
        print("\n📞 TUKI:")
        print("   • Tarkista että kaikki riippuvuudet on asennettu")
        print("   • Käytä --verify-lippua vianetsintään")

    def run_installation(self):
        self.print_header()
        steps = [
            self.validate_environment,
            self.get_election_info,
            self.get_admin_info,
            self.get_installation_password,
            self.create_directories,
            self.generate_crypto_keys,
            self.save_crypto_keys,
            self.create_config_files,
            self.initialize_data_files,
            self.verify_installation
        ]
        for step in steps:
            if not step():
                return False
        self.display_success_info()
        return True


def main():
    test_mode = '--test' in sys.argv or os.environ.get('VAALIKONE_TEST_MODE') == '1'
    
    if len(sys.argv) > 1 and sys.argv[1] == '--verify':
        verifier = InstallationManager()
        verifier.test_mode = False
        
        if not verifier.load_public_key():
            print("❌ Ei voida suorittaa tarkistusta: julkista avainta ei löydy.")
            sys.exit(1)
        
        success = verifier.verify_installation()
        sys.exit(0 if success else 1)
    else:
        installer = InstallationManager()
        success = installer.run_installation()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
