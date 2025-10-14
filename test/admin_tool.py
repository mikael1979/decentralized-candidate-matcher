#!/usr/bin/env python3
"""
Admin Tool - Comprehensive administration tool for Decentralized Candidate Matcher
Includes both admin and superadmin functionalities with proper authentication
"""

import json
import os
import sys
import hashlib
import getpass
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import argparse

class AdminTool:
    def __init__(self, data_dir: str = "test_data"):
        self.data_dir = Path(data_dir)
        self.loaded_data = {}
        self.current_admin = None
        self.admin_roles = {}
        
        # Lataa admin-tiedot
        self.load_admin_data()
    
    def load_admin_data(self):
        """Lataa admin-tiedot meta.json:stä"""
        meta_file = self.data_dir / "meta.json"
        if meta_file.exists():
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta_data = json.load(f)
                admins = meta_data.get('admins', [])
                for admin in admins:
                    self.admin_roles[admin['admin_id']] = {
                        'public_key': admin['public_key'],
                        'name': admin['name'],
                        'role': admin['role']
                    }
    
    def authenticate_admin(self) -> bool:
        """Todennä admin-käyttäjä"""
        print("\n🔐 ADMIN KIRJAUTUMINEN")
        print("=" * 30)
        
        admin_id = input("Admin ID: ").strip()
        # Demo: käytetään salasanaa todellisen julkisen avaimen sijaan
        password = getpass.getpass("Salasana: ")
        
        # Tarkista että admin ID on olemassa
        if admin_id not in self.admin_roles:
            print("❌ Virheellinen Admin ID")
            return False
        
        # Demo-todennus: todellisessa käytössä tarkistettaisiin digitaalinen allekirjoitus
        expected_password = f"admin_{admin_id}_demo"
        if password != expected_password:
            print("❌ Virheellinen salasana")
            return False
        
        self.current_admin = {
            'admin_id': admin_id,
            **self.admin_roles[admin_id]
        }
        
        print(f"✅ Kirjauduttu sisään: {self.current_admin['name']} ({self.current_admin['role']})")
        return True
    
    def load_all_data(self):
        """Lataa kaikki JSON-tiedostot"""
        files = ['meta.json', 'questions.json', 'newquestions.json', 
                'candidates.json', 'community_votes.json']
        
        for filename in files:
            filepath = self.data_dir / filename
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.loaded_data[filename] = json.load(f)
            else:
                print(f"⚠️  Tiedostoa {filename} ei löydy")
    
    def save_data(self, filename: str):
        """Tallenna data takaisin tiedostoon"""
        if filename in self.loaded_data:
            filepath = self.data_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.loaded_data[filename], f, indent=2, ensure_ascii=False)
            print(f"✓ Tallennettu: {filename}")
    
    def calculate_hash(self, data: Dict) -> str:
        """Laske SHA256 hash"""
        data_copy = data.copy()
        if 'integrity' in data_copy:
            del data_copy['integrity']
        
        json_str = json.dumps(data_copy, sort_keys=True, separators=(',', ':'))
        return f"sha256:{hashlib.sha256(json_str.encode()).hexdigest()}"
    
    def update_integrity(self, data: Dict) -> Dict:
        """Päivitä integrity-hash"""
        hash_value = self.calculate_hash(data)
        data['integrity'] = {
            'algorithm': 'sha256',
            'hash': hash_value,
            'computed': datetime.now().isoformat(),
            'admin_id': self.current_admin['admin_id']
        }
        return data
    
    # ADMIN TOIMINNOT
    
    def moderate_questions(self):
        """Moderoi käyttäjien kysymyksiä"""
        print("\n📝 KYSYMYSTEN MODERAATIO")
        print("=" * 40)
        
        newquestions = self.loaded_data.get('newquestions.json', {})
        questions = newquestions.get('questions', [])
        
        pending_questions = [q for q in questions if q.get('submission', {}).get('status') == 'pending']
        
        if not pending_questions:
            print("✅ Ei odottavia kysymyksiä moderoitavaksi")
            return
        
        print(f"Löytyi {len(pending_questions)} odottavaa kysymystä:")
        
        for i, question in enumerate(pending_questions, 1):
            print(f"\n--- {i}. KYSYMYS ---")
            print(f"ID: {question['id']}")
            print(f"Kategoria: {question['category']['fi']}")
            print(f"Kysymys: {question['question']['fi']}")
            if question['question'].get('en'):
                print(f"English: {question['question']['en']}")
            print(f"Tagit: {', '.join(question['tags']['fi'])}")
            print(f"Lähettäjän kommentti: {question.get('user_comment', 'Ei kommenttia')}")
            print(f"Yhteisöäänestykset: {question.get('community_moderation', {}).get('votes_received', 0)}")
            print(f"Sopimattomien suhde: {question.get('community_moderation', {}).get('inappropriate_ratio', 0):.2f}")
            
            action = input("\nToiminto (1=Hyväksy, 2=Hylkää, 3=Ohita, 4=Lopeta): ").strip()
            
            if action == '1':
                self.approve_question(question['id'])
                print("✅ Kysymys hyväksytty")
            elif action == '2':
                self.reject_question(question['id'])
                print("❌ Kysymys hylätty")
            elif action == '4':
                print("Moderaatio keskeytetty")
                break
            else:
                print("⏭️  Kysymys ohitettu")
    
    def approve_question(self, question_id: str):
        """Hyväksy kysymys"""
        newquestions = self.loaded_data.get('newquestions.json', {})
        for question in newquestions['questions']:
            if question['id'] == question_id:
                question['submission']['status'] = 'approved'
                question['moderation']['approved'] = True
                question['moderation']['moderated'] = True
                question['moderation']['moderated_by'] = self.current_admin['admin_id']
                question['moderation']['moderated_at'] = datetime.now().isoformat()
                question['community_moderation']['status'] = 'approved'
                break
        
        self.update_integrity(newquestions)
        self.save_data('newquestions.json')
    
    def reject_question(self, question_id: str):
        """Hylkää kysymys"""
        newquestions = self.loaded_data.get('newquestions.json', {})
        for question in newquestions['questions']:
            if question['id'] == question_id:
                question['submission']['status'] = 'rejected'
                question['moderation']['approved'] = False
                question['moderation']['moderated'] = True
                question['moderation']['moderated_by'] = self.current_admin['admin_id']
                question['moderation']['moderated_at'] = datetime.now().isoformat()
                question['community_moderation']['status'] = 'blocked'
                break
        
        self.update_integrity(newquestions)
        self.save_data('newquestions.json')
    
    def manage_candidates(self):
        """Hallinnoi ehdokkaita"""
        print("\n👥 EHDOKKAIDEN HALLINTA")
        print("=" * 40)
        
        candidates_data = self.loaded_data.get('candidates.json', {})
        candidates = candidates_data.get('candidates', [])
        
        if not candidates:
            print("⚠️  Ei ehdokkaita")
            return
        
        print(f"Järjestelmässä {len(candidates)} ehdokasta:")
        
        for i, candidate in enumerate(candidates, 1):
            verified = candidate.get('verified', False)
            status = "✅ Vahvistettu" if verified else "⏳ Odottaa vahvistusta"
            print(f"{i}. {candidate['name']} - {candidate['party']} - {candidate['district']} - {status}")
        
        print("\nValitse toiminto:")
        print("1. Vahvista ehdokas")
        print("2. Poista ehdokas")
        print("3. Näytä ehdokkaan tiedot")
        print("4. Lisää uusi ehdokas")
        
        choice = input("Valinta (1-4): ").strip()
        
        if choice == '1':
            self.verify_candidate()
        elif choice == '2':
            self.remove_candidate()
        elif choice == '3':
            self.show_candidate_details()
        elif choice == '4':
            self.add_candidate()
        else:
            print("❌ Virheellinen valinta")
    
    def verify_candidate(self):
        """Vahvista ehdokas"""
        candidate_id = input("Ehdokkaan ID: ").strip()
        
        candidates_data = self.loaded_data.get('candidates.json', {})
        for candidate in candidates_data['candidates']:
            if str(candidate['id']) == candidate_id:
                candidate['verified'] = True
                candidate['verified_by'] = self.current_admin['admin_id']
                candidate['verified_at'] = datetime.now().isoformat()
                print(f"✅ Ehdokas {candidate['name']} vahvistettu")
                break
        else:
            print("❌ Ehdokasta ei löydy")
            return
        
        self.update_integrity(candidates_data)
        self.save_data('candidates.json')
    
    def remove_candidate(self):
        """Poista ehdokas"""
        candidate_id = input("Poistettavan ehdokkaan ID: ").strip()
        
        candidates_data = self.loaded_data.get('candidates.json', {})
        candidates_data['candidates'] = [
            c for c in candidates_data['candidates'] 
            if str(c['id']) != candidate_id
        ]
        
        self.update_integrity(candidates_data)
        self.save_data('candidates.json')
        print("✅ Ehdokas poistettu")
    
    def add_candidate(self):
        """Lisää uusi ehdokas"""
        print("\n➕ LISÄÄ UUSI EHDOKAS")
        
        candidate_id = input("Ehdokasnumero: ").strip()
        name = input("Nimi: ").strip()
        party = input("Puolue: ").strip()
        district = input("Va-alue: ").strip()
        email = input("Sähköposti: ").strip()
        
        # Generoi demo-avaimet
        public_key = f"ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIcandidate_{candidate_id}"
        
        new_candidate = {
            "id": int(candidate_id),
            "name": name,
            "party": party,
            "district": district,
            "email": email,
            "public_key": public_key,
            "key_fingerprint": f"SHA256:{hashlib.sha256(public_key.encode()).hexdigest()[:32]}",
            "answer_cid": f"QmDemoCandidate{candidate_id}",
            "registration_date": datetime.now().isoformat(),
            "verified": True,
            "verified_by": self.current_admin['admin_id'],
            "verified_at": datetime.now().isoformat()
        }
        
        candidates_data = self.loaded_data.get('candidates.json', {})
        if 'candidates' not in candidates_data:
            candidates_data['candidates'] = []
        
        candidates_data['candidates'].append(new_candidate)
        
        self.update_integrity(candidates_data)
        self.save_data('candidates.json')
        print(f"✅ Ehdokas {name} lisätty")
    
    def show_candidate_details(self):
        """Näytä ehdokkaan tiedot"""
        candidate_id = input("Ehdokkaan ID: ").strip()
        
        candidates_data = self.loaded_data.get('candidates.json', {})
        for candidate in candidates_data['candidates']:
            if str(candidate['id']) == candidate_id:
                print(f"\n📋 EHDOKKAAN {candidate['name']} TIEDOT")
                print("=" * 40)
                for key, value in candidate.items():
                    print(f"{key}: {value}")
                return
        
        print("❌ Ehdokasta ei löydy")
    
    def system_statistics(self):
        """Näytä järjestelmän tilastot"""
        print("\n📊 JÄRJESTELMÄTILASTOT")
        print("=" * 40)
        
        # Lasketaan tilastot
        official_questions = len(self.loaded_data.get('questions.json', {}).get('questions', []))
        user_questions = len(self.loaded_data.get('newquestions.json', {}).get('questions', []))
        candidates = len(self.loaded_data.get('candidates.json', {}).get('candidates', []))
        votes = len(self.loaded_data.get('community_votes.json', {}).get('user_votes', []))
        
        # Kysymysten tilat
        question_status = {}
        for q in self.loaded_data.get('newquestions.json', {}).get('questions', []):
            status = q.get('submission', {}).get('status', 'unknown')
            question_status[status] = question_status.get(status, 0) + 1
        
        # Ehdokkaiden tilat
        verified_candidates = sum(1 for c in self.loaded_data.get('candidates.json', {}).get('candidates', []) 
                                if c.get('verified', False))
        
        print(f"Virallisia kysymyksiä: {official_questions}")
        print(f"Käyttäjien kysymyksiä: {user_questions}")
        print(f"Ehdokkaita: {candidates} ({verified_candidates} vahvistettua)")
        print(f"Yhteisöäänestyksiä: {votes}")
        
        print("\nKäyttäjien kysymysten tila:")
        for status, count in question_status.items():
            print(f"  {status}: {count}")
        
        # Äänestysjakauma
        vote_dist = {}
        for vote in self.loaded_data.get('community_votes.json', {}).get('user_votes', []):
            vote_type = vote['vote']
            vote_dist[vote_type] = vote_dist.get(vote_type, 0) + 1
        
        print("\nÄänestysjakauma:")
        for vote_type, count in vote_dist.items():
            print(f"  {vote_type}: {count}")
    
    # SUPERADMIN TOIMINNOT
    
    def manage_admins(self):
        """Hallinnoi admin-käyttäjiä (vain superadmin)"""
        if self.current_admin['role'] != 'super_admin':
            print("❌ Vain superadmin voi hallita admin-käyttäjiä")
            return
        
        print("\n⚙️ ADMIN-KÄYTTÄJIEN HALLINTA")
        print("=" * 40)
        
        meta_data = self.loaded_data.get('meta.json', {})
        admins = meta_data.get('admins', [])
        
        print("Nykyiset admin-käyttäjät:")
        for i, admin in enumerate(admins, 1):
            print(f"{i}. {admin['name']} ({admin['admin_id']}) - {admin['role']}")
        
        print("\nValitse toiminto:")
        print("1. Lisää admin-käyttäjä")
        print("2. Poista admin-käyttäjä")
        print("3. Muuta roolia")
        
        choice = input("Valinta (1-3): ").strip()
        
        if choice == '1':
            self.add_admin_user()
        elif choice == '2':
            self.remove_admin_user()
        elif choice == '3':
            self.change_admin_role()
        else:
            print("❌ Virheellinen valinta")
    
    def add_admin_user(self):
        """Lisää uusi admin-käyttäjä"""
        admin_id = input("Uusi Admin ID: ").strip()
        name = input("Nimi: ").strip()
        role = input("Rooli (admin/super_admin): ").strip()
        
        if role not in ['admin', 'super_admin']:
            print("❌ Roolin tulee olla 'admin' tai 'super_admin'")
            return
        
        # Generoi demo-julkinen avain
        public_key = f"ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIadmin_{admin_id}"
        
        new_admin = {
            "admin_id": admin_id,
            "public_key": public_key,
            "name": name,
            "role": role,
            "created_by": self.current_admin['admin_id'],
            "created_at": datetime.now().isoformat()
        }
        
        meta_data = self.loaded_data.get('meta.json', {})
        if 'admins' not in meta_data:
            meta_data['admins'] = []
        
        meta_data['admins'].append(new_admin)
        
        self.update_integrity(meta_data)
        self.save_data('meta.json')
        
        # Päivitä myös paikallinen cache
        self.admin_roles[admin_id] = {
            'public_key': public_key,
            'name': name,
            'role': role
        }
        
        print(f"✅ Admin-käyttäjä {name} lisätty")
        print(f"💡 Demo-salasanaksi asetettu: admin_{admin_id}_demo")
    
    def remove_admin_user(self):
        """Poista admin-käyttäjä"""
        admin_id = input("Poistettavan Admin ID: ").strip()
        
        if admin_id == self.current_admin['admin_id']:
            print("❌ Et voi poistaa omaa käyttäjääsi")
            return
        
        meta_data = self.loaded_data.get('meta.json', {})
        meta_data['admins'] = [
            admin for admin in meta_data['admins'] 
            if admin['admin_id'] != admin_id
        ]
        
        self.update_integrity(meta_data)
        self.save_data('meta.json')
        
        # Poista paikallisesta cachesta
        if admin_id in self.admin_roles:
            del self.admin_roles[admin_id]
        
        print("✅ Admin-käyttäjä poistettu")
    
    def change_admin_role(self):
        """Muuta admin-käyttäjän roolia"""
        admin_id = input("Admin ID: ").strip()
        new_role = input("Uusi rooli (admin/super_admin): ").strip()
        
        if new_role not in ['admin', 'super_admin']:
            print("❌ Roolin tulee olla 'admin' tai 'super_admin'")
            return
        
        meta_data = self.loaded_data.get('meta.json', {})
        for admin in meta_data['admins']:
            if admin['admin_id'] == admin_id:
                admin['role'] = new_role
                admin['modified_by'] = self.current_admin['admin_id']
                admin['modified_at'] = datetime.now().isoformat()
                break
        else:
            print("❌ Admin-käyttäjää ei löydy")
            return
        
        self.update_integrity(meta_data)
        self.save_data('meta.json')
        
        # Päivitä paikallinen cache
        if admin_id in self.admin_roles:
            self.admin_roles[admin_id]['role'] = new_role
        
        print(f"✅ Admin-käyttäjän {admin_id} rooli muutettu: {new_role}")
    
    def system_configuration(self):
        """Järjestelmän konfiguraatio (vain superadmin)"""
        if self.current_admin['role'] != 'super_admin':
            print("❌ Vain superadmin voi muokata järjestelmän konfiguraatiota")
            return
        
        print("\n⚙️ JÄRJESTELMÄN KONFIGURAATIO")
        print("=" * 40)
        
        meta_data = self.loaded_data.get('meta.json', {})
        community_config = meta_data.get('community_moderation', {})
        thresholds = community_config.get('thresholds', {})
        
        print("Nykyiset asetukset:")
        print(f"1. Automaattinen esto - kynnys: {thresholds.get('auto_block_inappropriate', 0.7)}")
        print(f"2. Minimääänestysmäärä: {thresholds.get('auto_block_min_votes', 10)}")
        print(f"3. Yhteisöhyväksynnän kynnys: {thresholds.get('community_approval', 0.8)}")
        print(f"4. Yhteisömoderaatio käytössä: {community_config.get('enabled', True)}")
        
        setting = input("\nValitse muutettava asetus (1-4) tai Enter peruuttaaksesi: ").strip()
        
        if setting == '1':
            new_value = float(input("Uusi automaattisen eston kynnys (0.0-1.0): "))
            thresholds['auto_block_inappropriate'] = new_value
        elif setting == '2':
            new_value = int(input("Uusi minimääänestysmäärä: "))
            thresholds['auto_block_min_votes'] = new_value
        elif setting == '3':
            new_value = float(input("Uusi yhteisöhyväksynnän kynnys (0.0-1.0): "))
            thresholds['community_approval'] = new_value
        elif setting == '4':
            new_value = input("Käytössä (k/e): ").strip().lower() == 'k'
            community_config['enabled'] = new_value
        else:
            print("❌ Peruutettu")
            return
        
        meta_data['community_moderation'] = community_config
        self.update_integrity(meta_data)
        self.save_data('meta.json')
        print("✅ Asetukset päivitetty")
    
    def database_maintenance(self):
        """Tietokannan ylläpito"""
        print("\n🗃️ TIETOKANNAN YLLÄPITO")
        print("=" * 40)
        
        print("Valitse toiminto:")
        print("1. Varmuuskopioi data")
        print("2. Palauta varmuuskopio")
        print("3. Siivoa vanhat tiedot")
        print("4. Tarkista data-eheys")
        
        choice = input("Valinta (1-4): ").strip()
        
        if choice == '1':
            self.backup_data()
        elif choice == '2':
            self.restore_backup()
        elif choice == '3':
            self.cleanup_old_data()
        elif choice == '4':
            self.verify_data_integrity()
        else:
            print("❌ Virheellinen valinta")
    
    def backup_data(self):
        """Luo varmuuskopio datasta"""
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"backup_{timestamp}.json"
        
        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "created_by": self.current_admin['admin_id'],
            "data": self.loaded_data
        }
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Varmuuskopio luotu: {backup_file}")
    
    def restore_backup(self):
        """Palauta varmuuskopio"""
        backup_dir = Path("backups")
        if not backup_dir.exists():
            print("❌ Varmuuskopiokansiota ei löydy")
            return
        
        backups = list(backup_dir.glob("backup_*.json"))
        if not backups:
            print("❌ Varmuuskopioita ei löydy")
            return
        
        print("Saatavilla olevat varmuuskopiot:")
        for i, backup in enumerate(backups, 1):
            print(f"{i}. {backup.name}")
        
        try:
            choice = int(input("Valitse varmuuskopio (numero): ").strip())
            selected_backup = backups[choice - 1]
        except (ValueError, IndexError):
            print("❌ Virheellinen valinta")
            return
        
        # Vahvista palautus
        confirm = input(f"Palautetaanko varmuuskopio {selected_backup.name}? (k/e): ").strip().lower()
        if confirm != 'k':
            print("❌ Peruutettu")
            return
        
        with open(selected_backup, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        # Palauta data
        for filename, data in backup_data['data'].items():
            filepath = self.data_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Lataa uudelleen muistiin
        self.load_all_data()
        
        print("✅ Varmuuskopio palautettu")
    
    def cleanup_old_data(self):
        """Siivoa vanhat tiedot"""
        print("\n🧹 VANHOJEN TIETOJEN SIIVOUS")
        print("=" * 40)
        
        # Etsi vanhat kysymykset
        newquestions = self.loaded_data.get('newquestions.json', {})
        old_questions = []
        
        for question in newquestions.get('questions', []):
            submit_time = question.get('submission', {}).get('timestamp')
            if submit_time:
                submit_date = datetime.fromisoformat(submit_time.replace('Z', '+00:00'))
                age_days = (datetime.now().astimezone() - submit_date).days
                if age_days > 30:  # Yli 30 päivää vanhat
                    old_questions.append(question)
        
        if old_questions:
            print(f"Löytyi {len(old_questions)} yli 30 päivää vanhaa kysymystä")
            confirm = input("Poistetaanko nämä? (k/e): ").strip().lower()
            if confirm == 'k':
                newquestions['questions'] = [
                    q for q in newquestions['questions'] 
                    if q not in old_questions
                ]
                self.update_integrity(newquestions)
                self.save_data('newquestions.json')
                print("✅ Vanhat kysymykset poistettu")
        else:
            print("✅ Ei vanhoja kysymyksiä")
    
    def verify_data_integrity(self):
        """Tarkista data-eheys"""
        print("\n🔍 DATA-EHEYDEN TARKISTUS")
        print("=" * 40)
        
        errors = []
        
        for filename, data in self.loaded_data.items():
            if 'integrity' in data:
                computed_hash = self.calculate_hash(data)
                if computed_hash != data['integrity']['hash']:
                    errors.append(f"Hash-eheysvirhe tiedostossa {filename}")
        
        if not errors:
            print("✅ Kaikki tiedostot eheät")
        else:
            print("❌ Löytyi eheysvirheitä:")
            for error in errors:
                print(f"  - {error}")
    
    def run_admin_panel(self):
        """Käynnistä admin-paneeli"""
        if not self.authenticate_admin():
            return
        
        self.load_all_data()
        
        while True:
            print(f"\n🎯 ADMIN PANEL - {self.current_admin['name']} ({self.current_admin['role']})")
            print("=" * 50)
            
            # Perus admin-toiminnot
            print("1. 📝 Moderoi kysymyksiä")
            print("2. 👥 Hallinnoi ehdokkaita")
            print("3. 📊 Järjestelmätilastot")
            print("4. 🗃️ Tietokannan ylläpito")
            
            # Superadmin-toiminnot
            if self.current_admin['role'] == 'super_admin':
                print("5. ⚙️ Hallinnoi admin-käyttäjiä")
                print("6. 🔧 Järjestelmän konfiguraatio")
            
            print("0. 🔒 Kirjaudu ulos")
            
            choice = input("\nValitse toiminto: ").strip()
            
            if choice == '1':
                self.moderate_questions()
            elif choice == '2':
                self.manage_candidates()
            elif choice == '3':
                self.system_statistics()
            elif choice == '4':
                self.database_maintenance()
            elif choice == '5' and self.current_admin['role'] == 'super_admin':
                self.manage_admins()
            elif choice == '6' and self.current_admin['role'] == 'super_admin':
                self.system_configuration()
            elif choice == '0':
                print("🔒 Kirjaudutaan ulos...")
                break
            else:
                print("❌ Virheellinen valinta")

def main():
    """Pääfunktio"""
    parser = argparse.ArgumentParser(description='Admin Tool - Decentralized Candidate Matcher')
    parser.add_argument('--data-dir', default='test_data', help='Data-kansio')
    
    args = parser.parse_args()
    
    # Tarkista että data-kansio on olemassa
    if not Path(args.data_dir).exists():
        print(f"❌ Data-kansiota {args.data_dir} ei löydy")
        print("💡 Luo ensin data ajamalla: python demo.py")
        sys.exit(1)
    
    tool = AdminTool(args.data_dir)
    tool.run_admin_panel()

if __name__ == "__main__":
    main()
