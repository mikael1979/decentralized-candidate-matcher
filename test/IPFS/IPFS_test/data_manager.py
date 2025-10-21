import json
import os
from datetime import datetime
from utils import ConfigLoader, calculate_hash, generate_next_id

class DataManager:
    def __init__(self, debug=False):
        self.debug = debug
        self.data_dir = 'data'
        self.config_loader = ConfigLoader()
        self.ipfs_client = None  # Uusi attribuutti

    def set_ipfs_client(self, ipfs_client):
        """Aseta IPFS-asiakas (kutsutaan web_app.py:stä)"""
        self.ipfs_client = ipfs_client
        if self.debug:
            print("✅ IPFS-asiakas asetettu DataManagerille")

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
        admins_config = self.config_loader.load_config('admins.json')
        
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
            'comments.json': {
                "election_id": "test_election_2025",
                "language": "fi",
                "comments": []
            },
            'ipfs_sync_queue.json': {
                "pending_questions": [],
                "last_sync": None,
                "sync_interval_minutes": 10,
                "max_questions_per_sync": 20
            },
            'ipfs_questions_cache.json': {
                "last_fetch": None,
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
            },
            "community_moderation": {
                "enabled": True,
                "thresholds": {
                    "auto_block_inappropriate": 0.7,
                    "auto_block_min_votes": 10,
                    "community_approval": 0.8
                },
                "ipfs_sync_mode": "elo_priority"  # elo_priority | fifo
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
            questions = self.get_questions(include_ipfs=False)  # Älä laske IPFS-kysymyksiä tilastoihin
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

    def calculate_current_elo(self, base_rating, deltas):
        """Laskee nykyisen Elo-arvon deltojen perusteella"""
        return base_rating + sum(d.get('delta', 0) for d in deltas)

    def get_questions(self, include_blocked=False, include_ipfs=True):
        """Hakee kaikki kysymykset"""
        all_questions = []
        
        # Paikalliset kysymykset
        official = self.read_json('questions.json') or {}
        user = self.read_json('newquestions.json') or {}
        all_questions.extend(official.get('questions', []))
        all_questions.extend(user.get('questions', []))
        
        # IPFS-kysymykset
        if include_ipfs:
            ipfs_cache = self.read_json('ipfs_questions_cache.json') or {}
            ipfs_questions = ipfs_cache.get('questions', [])
            # Laske nykyinen Elo-arvo jokaiselle IPFS-kysymykselle
            for q in ipfs_questions:
                if 'elo' in q:
                    q['elo']['current_rating'] = self.calculate_current_elo(
                        q['elo']['base_rating'],
                        q['elo']['deltas']
                    )
            all_questions.extend(ipfs_questions)
        
        if include_blocked:
            return all_questions
        return [q for q in all_questions if not q.get('metadata', {}).get('blocked', False)]

    def get_candidates(self):
        """Hakee kaikki ehdokkaat"""
        data = self.read_json('candidates.json') or {}
        return data.get('candidates', [])

    def get_admins(self):
        """Hakee admin-tiedot"""
        return self.config_loader.load_config('admins.json') or {}

    def get_comments(self):
        """Hakee kommentit"""
        data = self.read_json('comments.json') or {}
        return data.get('comments', [])

    def add_question(self, question_data):
        """Lisää uuden kysymyksen"""
        try:
            # Lisää metadata-kentät
            question_data.setdefault('metadata', {
                'elo_rating': 1200,
                'blocked': False,
                'blocked_reason': None,
                'created_at': datetime.now().isoformat(),
                'created_by': 'user',
                'votes_for': 0,
                'votes_against': 0,
                'community_approved': False
            })
            
            # Lisää Elo-rakenne (delta-pohjainen)
            question_data.setdefault('elo', {
                'base_rating': 1200,
                'deltas': [],
                'current_rating': 1200
            })
            
            data = self.read_json('newquestions.json') or {}
            questions = data.get('questions', [])
            question_data['id'] = generate_next_id(questions)
            questions.append(question_data)
            data['questions'] = questions
            success = self.write_json('newquestions.json', data, f"Kysymys {question_data['id']} lisätty")
            
            # Päivitä meta-tilastot
            if success:
                self.get_meta()
                # Lisää synkronointijonoon
                self.queue_for_ipfs_sync(question_data['id'])
            
            return f"mock_cid_{question_data['id']}" if success else None
        except Exception as e:
            if self.debug:
                print(f"❌ Kysymyksen lisäys epäonnistui: {e}")
            return None

    def add_candidate(self, candidate_data):
        """Lisää uuden ehdokkaan"""
        try:
            # Varmista, että answers sisältää justification-kentät
            for ans in candidate_data.get('answers', []):
                ans.setdefault('justification', {
                    'fi': '',
                    'en': '',
                    'sv': ''
                })
                ans.setdefault('justification_metadata', {
                    'created_at': datetime.now().isoformat(),
                    'version': 1,
                    'blocked': False,
                    'signature': None
                })
            
            data = self.read_json('candidates.json') or {}
            candidates = data.get('candidates', [])
            candidate_data['id'] = generate_next_id(candidates)
            candidates.append(candidate_data)
            data['candidates'] = candidates
            success = self.write_json('candidates.json', data, f"Ehdokas {candidate_data.get('name')} lisätty")
            # Päivitä meta-tilastot
            if success:
                self.get_meta()
            return candidate_data['id'] if success else None
        except Exception as e:
            if self.debug:
                print(f"❌ Ehdokkaan lisäys epäonnistui: {e}")
            return None

    def block_question(self, question_id, reason=None):
        """Merkitsee kysymyksen blokatuksi"""
        # Etsi kysymys
        official = self.read_json('questions.json') or {}
        user = self.read_json('newquestions.json') or {}
        
        found = False
        for q in official.get('questions', []):
            if q.get('id') == question_id:
                q.setdefault('metadata', {})['blocked'] = True
                q['metadata']['blocked_reason'] = reason
                self.write_json('questions.json', official, f"Kysymys {question_id} blokattu")
                found = True
                break
        
        if not found:
            for q in user.get('questions', []):
                if q.get('id') == question_id:
                    q.setdefault('metadata', {})['blocked'] = True
                    q['metadata']['blocked_reason'] = reason
                    self.write_json('newquestions.json', user, f"Kysymys {question_id} blokattu")
                    found = True
                    break
        
        if found:
            self.get_meta()
        return found

    def queue_for_ipfs_sync(self, question_id):
        """Lisää kysymys IPFS-synkronointijonoon"""
        queue = self.read_json('ipfs_sync_queue.json') or {
            'pending_questions': [],
            'last_sync': None,
            'sync_interval_minutes': 10,
            'max_questions_per_sync': 20
        }
        
        # Etsi kysymys
        all_questions = self.get_questions(include_blocked=True, include_ipfs=False)
        question = next((q for q in all_questions if q.get('id') == question_id), None)
        if not question:
            return False
        
        queue['pending_questions'].append({
            'question_id': question_id,
            'added_to_queue_at': datetime.now().isoformat(),
            'elo_rating': question.get('elo', {}).get('current_rating', 1200),
            'status': 'pending'
        })
        
        return self.write_json('ipfs_sync_queue.json', queue, "Kysymys lisätty synkronointijonoon")

    def process_ipfs_sync(self):
        """Käsittelee IPFS-synkronoinnin jonosta"""
        queue = self.read_json('ipfs_sync_queue.json') or {'pending_questions': []}
        if not queue.get('pending_questions'):
            return False
        
        # Tarkista trigger
        last_sync = queue.get('last_sync')
        interval = queue.get('sync_interval_minutes', 10)
        if last_sync:
            last_sync_time = datetime.fromisoformat(last_sync.replace('Z', '+00:00'))
            if (datetime.now() - last_sync_time).total_seconds() < interval * 60:
                return False  # Liian aikaista
        
        # Valitse kysymykset
        max_sync = queue.get('max_questions_per_sync', 20)
        pending = [q for q in queue['pending_questions'] if q['status'] == 'pending']
        
        # Valintalogiikka: Elo tai FIFO
        selection_mode = self.get_meta().get('community_moderation', {}).get('ipfs_sync_mode', 'elo_priority')
        if selection_mode == 'elo_priority':
            pending.sort(key=lambda x: x.get('elo_rating', 1200), reverse=True)
        else:  # fifo
            pending.sort(key=lambda x: x.get('added_to_queue_at', ''))
        
        selected = pending[:max_sync]
        
        # Synkronoi IPFS:iin
        if self.ipfs_client:
            ipfs_questions = []
            for item in selected:
                # Hae kysymys
                all_questions = self.get_questions(include_blocked=True, include_ipfs=False)
                question = next((q for q in all_questions if q.get('id') == item['question_id']), None)
                if question:
                    ipfs_questions.append(question)
            
            if ipfs_questions:
                ipfs_data = {
                    "election_id": self.get_meta().get("election", {}).get("id"),
                    "timestamp": datetime.now().isoformat(),
                    "questions": ipfs_questions
                }
                result = self.ipfs_client.add_json(ipfs_data)
                if result:
                    # Päivitä jono
                    for item in selected:
                        item['status'] = 'synced'
                        item['synced_at'] = datetime.now().isoformat()
                        item['ipfs_cid'] = result["Hash"]
                    
                    queue['last_sync'] = datetime.now().isoformat()
                    queue['pending_questions'] = [q for q in queue['pending_questions'] if q not in selected] + selected
                    self.write_json('ipfs_sync_queue.json', queue, f"Synkronoitu {len(selected)} kysymystä IPFS:iin")
                    return True
        
        return False

    def fetch_questions_from_ipfs(self):
        """Lataa kysymykset IPFS:stä ja tallentaa välimuistiin"""
        if not self.ipfs_client:
            return False
        
        try:
            # Käytä well-known CID:tä (tässä vaiheessa voit määrittää sen)
            well_known_cid = "QmWellKnownQuestionsList"  # Tämä pitää korvata oikealla CID:llä
            ipfs_data = self.ipfs_client.get_json(well_known_cid)
            
            if ipfs_data:
                cache = {
                    "last_fetch": datetime.now().isoformat(),
                    "questions": ipfs_data.get("questions", [])
                }
                self.write_json("ipfs_questions_cache.json", cache, "IPFS-kysymykset välimuistiin")
                return True
            return False
        except Exception as e:
            if self.debug:
                print(f"❌ IPFS-haku epäonnistui: {e}")
            return False

    def apply_elo_delta(self, question_id, delta, user_id):
        """Lisää Elo-muutos IPFS-synkronointijonoon"""
        # Hae kysymys
        all_questions = self.get_questions(include_blocked=True, include_ipfs=True)
        question = next((q for q in all_questions if q.get('id') == question_id), None)
        if not question:
            return False
        
        # Luo uusi delta
        new_delta = {
            'timestamp': datetime.now().isoformat(),
            'delta': delta,
            'by': user_id
        }
        
        # Päivitä paikallinen bufferi
        question['elo']['deltas'].append(new_delta)
        question['elo']['current_rating'] = self.calculate_current_elo(
            question['elo']['base_rating'],
            question['elo']['deltas']
        )
        
        # Päivitä tiedosto
        official = self.read_json('questions.json') or {}
        user = self.read_json('newquestions.json') or {}
        
        updated = False
        for q in official.get('questions', []):
            if q.get('id') == question_id:
                q['elo'] = question['elo']
                self.write_json('questions.json', official, f"Elo päivitetty kysymykselle {question_id}")
                updated = True
                break
        
        if not updated:
            for q in user.get('questions', []):
                if q.get('id') == question_id:
                    q['elo'] = question['elo']
                    self.write_json('newquestions.json', user, f"Elo päivitetty kysymykselle {question_id}")
                    updated = True
                    break
        
        if updated:
            # Lisää synkronointijonoon
            self.queue_for_ipfs_sync(question_id)
        
        return updated
