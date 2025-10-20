import json
import os
import hashlib
from datetime import datetime

class DataManager:
    def __init__(self, debug=False):
        self.debug = debug
        self.data_dir = 'data'
        
    def ensure_directories(self):
        """Varmistaa että tarvittavat kansiot ovat olemassa"""
        directories = ['data', 'templates', 'static']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            if self.debug:
                print(f"📁 Kansio varmistettu: {directory}")
    
    def initialize_data_files(self):
        """Alustaa data-tiedostot"""
        self.ensure_directories()
        
        # Perustiedostot
        files = {
            'questions.json': {
                "election_id": "test_election_2025",
                "language": "fi",
                "questions": [
                    {
                        "id": 1,
                        "category": {"fi": "Ympäristö", "en": "Environment"},
                        "question": {
                            "fi": "Pitäisikö kaupungin vähentää hiilidioksidipäästöjä 50% vuoteen 2030 mennessä?",
                            "en": "Should the city reduce carbon dioxide emissions by 50% by 2030?"
                        },
                        "tags": ["ympäristö", "hiilidioksidi", "ilmasto"],
                        "scale": {"min": -5, "max": 5}
                    },
                    {
                        "id": 2,
                        "category": {"fi": "Liikenne", "en": "Transportation"},
                        "question": {
                            "fi": "Pitäisikö kaupunkipyörien määrää lisätä kesäkaudella?",
                            "en": "Should the number of city bikes be increased during summer season?"
                        },
                        "tags": ["liikenne", "kaupunkipyörät", "kesä"],
                        "scale": {"min": -5, "max": 5}
                    }
                ]
            },
            'candidates.json': {
                "election_id": "test_election_2025", 
                "language": "fi",
                "candidates": [
                    {
                        "id": 1,
                        "name": "Matti Meikäläinen",
                        "party": "Test Puolue", 
                        "district": "Helsinki",
                        "answers": [
                            {"question_id": 1, "answer": 4, "confidence": 0.8},
                            {"question_id": 2, "answer": 3, "confidence": 0.6}
                        ]
                    },
                    {
                        "id": 2,
                        "name": "Liisa Esimerkki",
                        "party": "Toinen Puolue",
                        "district": "Espoo", 
                        "answers": [
                            {"question_id": 1, "answer": 2, "confidence": 0.5},
                            {"question_id": 2, "answer": 5, "confidence": 0.8}
                        ]
                    }
                ]
            },
            'newquestions.json': {
                "election_id": "test_election_2025",
                "language": "fi",
                "question_type": "user_submitted", 
                "questions": []
            },
            'meta.json': {
                "system": "Decentralized Candidate Matcher",
                "version": "0.0.1",
                "election": {
                    "id": "test_election_2025",
                    "country": "FI",
                    "type": "municipal",
                    "name": {
                        "fi": "Testivaalit 2025",
                        "en": "Test Election 2025",
                        "sv": "Testval 2025"
                    },
                    "date": "2025-04-13",
                    "language": "fi"
                },
                "community_moderation": {
                    "enabled": True,
                    "thresholds": {
                        "auto_block_inappropriate": 0.7,
                        "auto_block_min_votes": 10,
                        "community_approval": 0.8
                    }
                },
                "admins": [
                    {
                        "admin_id": "admin_1",
                        "public_key": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIadmin1example123456789",
                        "name": "Election Admin",
                        "role": "super_admin"
                    }
                ],
                "content": {
                    "last_updated": datetime.now().isoformat(),
                    "questions_count": 2,
                    "candidates_count": 2,
                    "parties_count": 2
                },
                "integrity": {
                    "algorithm": "sha256",
                    "hash": "",
                    "computed": datetime.now().isoformat()
                }
            }
        }
        
        for filename, default_data in files.items():
            filepath = os.path.join(self.data_dir, filename)
            if not os.path.exists(filepath):
                # Laske hash ennen tallennusta
                if filename == 'meta.json':
                    default_data['integrity']['hash'] = self._calculate_hash(default_data)
                self.write_json(filename, default_data, f"Alustettu {filename}")
            elif self.debug:
                print(f"✅ Tiedosto on olemassa: {filename}")
    
    def _calculate_hash(self, data):
        """Laskee SHA256 hash datalle"""
        # Poista integrity-kenttä ennen hashin laskemista
        data_without_integrity = data.copy()
        if 'integrity' in data_without_integrity:
            del data_without_integrity['integrity']
        
        # Muunna JSONiksi ja laske hash
        json_str = json.dumps(data_without_integrity, sort_keys=True, ensure_ascii=False)
        return f"sha256:{hashlib.sha256(json_str.encode('utf-8')).hexdigest()}"
    
    def read_json(self, filename):
        """Lukee JSON-tiedoston"""
        try:
            filepath = os.path.join(self.data_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if self.debug:
                print(f"📖 Luettu: {filename}")
            return data
        except Exception as e:
            if self.debug:
                print(f"❌ Virhe lukemisessa {filename}: {e}")
            return None
    
    def write_json(self, filename, data, operation=""):
        """Kirjoittaa JSON-tiedoston"""
        try:
            filepath = os.path.join(self.data_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            if self.debug:
                desc = f" - {operation}" if operation else ""
                print(f"💾 Kirjoitettu: {filename}{desc}")
            return True
        except Exception as e:
            if self.debug:
                print(f"❌ Virhe kirjoittamisessa {filename}: {e}")
            return False
    
    def get_meta(self):
        """Hakee meta-tiedot ja päivittää tilastot"""
        meta = self.read_json('meta.json') or {}
        if meta:
            # Päivitä dynaamiset tilastot
            questions = self.get_questions()
            candidates = self.get_candidates()
            parties = list(set(c.get('party', '') for c in candidates if c.get('party')))
            
            meta['content'] = {
                'last_updated': datetime.now().isoformat(),
                'questions_count': len(questions),
                'candidates_count': len(candidates),
                'parties_count': len(parties)
            }
            
            # Päivitä integrity hash
            meta['integrity'] = {
                'algorithm': 'sha256',
                'hash': self._calculate_hash(meta),
                'computed': datetime.now().isoformat()
            }
            
            # Tallenna päivitetty meta
            self.write_json('meta.json', meta, "Päivitetty meta-tilastot")
        
        return meta
    
    def update_meta(self, new_meta):
        """Päivittää meta-tiedot"""
        try:
            # Säilytä nykyiset tilastot
            current_meta = self.get_meta()
            if current_meta:
                new_meta['content'] = current_meta.get('content', {})
            
            # Päivitä integrity hash
            new_meta['integrity'] = {
                'algorithm': 'sha256',
                'hash': self._calculate_hash(new_meta),
                'computed': datetime.now().isoformat()
            }
            
            success = self.write_json('meta.json', new_meta, "Meta-tiedot päivitetty")
            return success
        except Exception as e:
            if self.debug:
                print(f"❌ Meta-tietojen päivitys epäonnistui: {e}")
            return False
    
    def get_questions(self):
        """Hakee kaikki kysymykset"""
        official = self.read_json('questions.json') or {}
        user = self.read_json('newquestions.json') or {}
        return official.get('questions', []) + user.get('questions', [])
    
    def get_candidates(self):
        """Hakee kaikki ehdokkaat"""
        data = self.read_json('candidates.json') or {}
        return data.get('candidates', [])
    
    def add_question(self, question_data):
        """Lisää uuden kysymyksen"""
        try:
            data = self.read_json('newquestions.json') or {}
            questions = data.get('questions', [])
            
            new_id = max([q.get('id', 0) for q in questions], default=0) + 1
            question_data['id'] = new_id
            questions.append(question_data)
            
            data['questions'] = questions
            success = self.write_json('newquestions.json', data, f"Kysymys {new_id} lisätty")
            
            # Päivitä meta-tilastot
            if success:
                self.get_meta()  # Tämä päivittää automaattisesti
            
            return f"mock_cid_{new_id}" if success else None
        except Exception as e:
            if self.debug:
                print(f"❌ Kysymyksen lisäys epäonnistui: {e}")
            return None
    
    def add_candidate(self, candidate_data):
        """Lisää uuden ehdokkaan"""
        try:
            data = self.read_json('candidates.json') or {}
            candidates = data.get('candidates', [])
            
            new_id = max([c.get('id', 0) for c in candidates], default=0) + 1
            candidate_data['id'] = new_id
            candidates.append(candidate_data)
            
            data['candidates'] = candidates
            success = self.write_json('candidates.json', data, f"Ehdokas {candidate_data.get('name')} lisätty")
            
            # Päivitä meta-tilastot
            if success:
                self.get_meta()  # Tämä päivittää automaattisesti
            
            return new_id if success else None
        except Exception as e:
            if self.debug:
                print(f"❌ Ehdokkaan lisäys epäonnistui: {e}")
            return None
