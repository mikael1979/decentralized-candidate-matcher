import json
import os
from datetime import datetime
from utils import ConfigLoader, calculate_hash, generate_next_id


class DataManager:
    def __init__(self, debug=False):
        self.debug = debug
        self.data_dir = 'data'
        self.config_loader = ConfigLoader()
        
    def ensure_directories(self):
        """Varmistaa että tarvittavat kansiot ovat olemassa"""
        directories = ['data', 'templates', 'static', 'config']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            if self.debug:
                print(f"📁 Kansio varmistettu: {directory}")
    
    def initialize_data_files(self):
        """Alustaa data-tiedostot konfiguraatioista"""
        self.ensure_directories()
        
        # Lataa konfiguraatiot
        questions_config = self.config_loader.load_config('questions.json')
        candidates_config = self.config_loader.load_config('candidates.json')
        meta_config = self.config_loader.load_config('meta.json')
        
        # Perustiedostot
        files = {
            'questions.json': {
                "election_id": "test_election_2025",
                "language": "fi",
                "questions": questions_config.get('default_questions', [])
            },
            'candidates.json': {
                "election_id": "test_election_2025", 
                "language": "fi",
                "candidates": candidates_config.get('default_candidates', [])
            },
            'newquestions.json': {
                "election_id": "test_election_2025",
                "language": "fi",
                "question_type": "user_submitted", 
                "questions": []
            },
            'meta.json': self._initialize_meta_data(meta_config.get('default_meta', {}))
        }
        
        for filename, default_data in files.items():
            filepath = os.path.join(self.data_dir, filename)
            if not os.path.exists(filepath):
                self.write_json(filename, default_data, f"Alustettu {filename}")
            elif self.debug:
                print(f"✅ Tiedosto on olemassa: {filename}")
    
    def _initialize_meta_data(self, default_meta):
        """Alustaa meta-tiedot"""
        meta_data = default_meta.copy()
        
        # Lisää dynaamiset kentät
        meta_data.update({
            "content": {
                "last_updated": datetime.now().isoformat(),
                "questions_count": len(self.config_loader.load_config('questions.json').get('default_questions', [])),
                "candidates_count": len(self.config_loader.load_config('candidates.json').get('default_candidates', [])),
                "parties_count": len(set(
                    c.get('party', '') 
                    for c in self.config_loader.load_config('candidates.json').get('default_candidates', [])
                    if c.get('party')
                ))
            },
            "integrity": {
                "algorithm": "sha256",
                "hash": "",
                "computed": datetime.now().isoformat()
            }
        })
        
        # Laske hash
        meta_data['integrity']['hash'] = calculate_hash(meta_data)
        
        return meta_data
    
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
                'hash': calculate_hash(meta),
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
                'hash': calculate_hash(new_meta),
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
            
            question_data['id'] = generate_next_id(questions)
            questions.append(question_data)
            
            data['questions'] = questions
            success = self.write_json('newquestions.json', data, f"Kysymys {question_data['id']} lisätty")
            
            # Päivitä meta-tilastot
            if success:
                self.get_meta()  # Tämä päivittää automaattisesti
            
            return f"mock_cid_{question_data['id']}" if success else None
        except Exception as e:
            if self.debug:
                print(f"❌ Kysymyksen lisäys epäonnistui: {e}")
            return None
    
    def add_candidate(self, candidate_data):
        """Lisää uuden ehdokkaan"""
        try:
            data = self.read_json('candidates.json') or {}
            candidates = data.get('candidates', [])
            
            candidate_data['id'] = generate_next_id(candidates)
            candidates.append(candidate_data)
            
            data['candidates'] = candidates
            success = self.write_json('candidates.json', data, f"Ehdokas {candidate_data.get('name')} lisätty")
            
            # Päivitä meta-tilastot
            if success:
                self.get_meta()  # Tämä päivittää automaattisesti
            
            return candidate_data['id'] if success else None
        except Exception as e:
            if self.debug:
                print(f"❌ Ehdokkaan lisäys epäonnistui: {e}")
            return None
