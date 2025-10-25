import json
import os
import hashlib
import base64
from datetime import datetime, timedelta
from utils import ConfigLoader, calculate_hash, generate_next_id
from data_schemas import SCHEMA_MAP
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

class DataManager:
    def __init__(self, debug=False):
        self.debug = debug
        self.data_dir = 'data'
        self.config_loader = ConfigLoader()
        self.ipfs_client = None

    def set_ipfs_client(self, ipfs_client):
        self.ipfs_client = ipfs_client
        if self.debug:
            print("✅ IPFS-asiakas asetettu DataManagerille")

    def ensure_directories(self):
        directories = ['data', 'templates', 'static', 'config']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            if self.debug:
                print(f"📁 Kansio varmistettu: {directory}")

    def _read_json_safe(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            if self.debug:
                print(f"❌ Virhe lukemisessa {filepath}: {e}")
            return None

    def _get_installation_password(self):
        """Hakee asennussalasanan system_info.json:sta"""
        with open('keys/system_info.json', 'r') as f:
            info = json.load(f)
        return info['password_hash']  # Huom: tämä ei ole salasana, vaan sen hash

    def _load_private_key(self):
        """Lataa salausavaimen (ei salasanasuojattu tässä versiossa)"""
        with open('keys/private_key.pem', 'rb') as f:
            return serialization.load_pem_private_key(
                f.read(),
                password=None
            )

    def is_content_editing_allowed(self, content_type: str = "all") -> bool:
        """Tarkistaa, onko sisällön muokkaus sallittu vaalilukituksen perusteella"""
        meta = self.get_meta()
        deadline_str = meta.get("election", {}).get("content_edit_deadline")
        if not deadline_str:
            return True
        try:
            if deadline_str.endswith('Z'):
                deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
            else:
                deadline = datetime.fromisoformat(deadline_str)
            grace_hours = meta.get("election", {}).get("grace_period_hours", 24)
            grace_end = deadline + timedelta(hours=grace_hours)
            now = datetime.now(deadline.tzinfo if deadline.tzinfo else None)
            return now < grace_end
        except Exception as e:
            if self.debug:
                print(f"⚠️  Deadline-tarkistusvirhe: {e}")
            return True

    def ensure_data_file(self, filename):
        filepath = os.path.join(self.data_dir, filename)
        if os.path.exists(filepath):
            return self._read_json_safe(filepath)

        if filename not in SCHEMA_MAP:
            raise ValueError(f"Tuntematon tiedosto ilman skeemaa: {filename}")

        election_id = "default_election"
        system_id = ""
        meta_path = os.path.join(self.data_dir, 'meta.json')
        if os.path.exists(meta_path):
            try:
                existing_meta = self._read_json_safe(meta_path)
                if existing_meta:
                    election_id = existing_meta.get("election", {}).get("id", election_id)
                    system_id = existing_meta.get("system_info", {}).get("system_id", system_id)
            except Exception:
                pass

        schema_func = SCHEMA_MAP[filename]
        kwargs = {}
        if 'election_id' in schema_func.__code__.co_varnames:
            kwargs['election_id'] = election_id
        if 'system_id' in schema_func.__code__.co_varnames:
            kwargs['system_id'] = system_id

        if filename == 'meta.json':
            default_meta = {
                "system": "Decentralized Candidate Matcher",
                "version": "0.0.6-alpha",
                "election": {
                    "id": election_id,
                    "country": "FI",
                    "name": {"fi": "Nimetön vaalit", "en": "Unnamed Election", "sv": "Namnlös val"},
                    "date": "2025-01-01",
                    "language": "fi"
                },
                "community_moderation": {
                    "enabled": True,
                    "thresholds": {
                        "auto_block_inappropriate": 0.7,
                        "auto_block_min_votes": 10,
                        "community_approval": 0.8
                    },
                    "ipfs_sync_mode": "elo_priority"
                },
                "admins": [],
                "key_management": {
                    "system_public_key": "",
                    "key_algorithm": "RSA-2048",
                    "parties_require_keys": True,
                    "candidates_require_keys": False
                },
                "content": {
                    "last_updated": datetime.now().isoformat(),
                    "questions_count": 0,
                    "candidates_count": 0,
                    "parties_count": 0
                },
                "system_info": {
                    "system_id": system_id,
                    "installation_time": datetime.now().isoformat(),
                    "key_fingerprint": ""
                }
            }
            data = self._initialize_meta_data(default_meta)
        else:
            data = schema_func(**kwargs)

        self.write_json(filename, data, f"Luotiin puuttuva tiedosto: {filename}")
        return data

    def _initialize_meta_data(self, default_meta):
        meta_data = default_meta.copy()
        meta_data.update({
            "integrity": {
                "algorithm": "sha256",
                "hash": "",
                "computed": datetime.now().isoformat()
            }
        })
        meta_data['integrity']['hash'] = calculate_hash(meta_data)
        return meta_data

    def read_json(self, filename):
        return self.ensure_data_file(filename)

    def write_json(self, filename, data, operation=""):
        try:
            filepath = os.path.join(self.data_dir, filename)
            tmp_filepath = filepath + '.tmp'
            with open(tmp_filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_filepath, filepath)
            if self.debug:
                desc = f" - {operation}" if operation else ""
                print(f"💾 Kirjoitettu turvallisesti: {filename}{desc}")
            return True
        except Exception as e:
            tmp_path = os.path.join(self.data_dir, filename + '.tmp')
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
            if self.debug:
                print(f"❌ Virhe turvallisessa kirjoituksessa {filename}: {e}")
            return False

    def get_meta(self):
        meta = self.ensure_data_file('meta.json')
        questions = self.get_questions(include_ipfs=False)
        candidates = self.get_candidates()
        parties = list(set(c.get('party', '') for c in candidates if c.get('party')))
        meta['content'] = {
            'last_updated': datetime.now().isoformat(),
            'questions_count': len(questions),
            'candidates_count': len(candidates),
            'parties_count': len(parties)
        }
        meta['integrity'] = {
            'algorithm': 'sha256',
            'hash': calculate_hash(meta),
            'computed': datetime.now().isoformat()
        }
        self.write_json('meta.json', meta, "Päivitetty meta-tilastot")
        return meta

    def update_meta(self, new_meta):
        try:
            current_meta = self.get_meta()
            if current_meta:
                new_meta['content'] = current_meta.get('content', {})
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
        return base_rating + sum(d.get('delta', 0) for d in deltas)

    def get_questions(self, include_blocked=False, include_ipfs=True):
        all_questions = []
        official = self.ensure_data_file('questions.json')
        user = self.ensure_data_file('newquestions.json')
        all_questions.extend(official.get('questions', []))
        all_questions.extend(user.get('questions', []))
        if include_ipfs:
            ipfs_cache = self.ensure_data_file('ipfs_questions_cache.json')
            ipfs_questions = ipfs_cache.get('questions', [])
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
        data = self.ensure_data_file('candidates.json')
        return data.get('candidates', [])

    def get_admins(self):
        return self.config_loader.load_config('admins.json') or {}

    def get_comments(self):
        data = self.ensure_data_file('comments.json')
        return data.get('comments', [])

    def add_question(self, question_data):
        if not self.is_content_editing_allowed():
            if self.debug:
                print("🔒 Kysymysten lisäys estetty – aikalukitus aktiivinen")
            return None
        try:
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
            question_data.setdefault('elo', {
                'base_rating': 1200,
                'deltas': [],
                'current_rating': 1200
            })
            data = self.ensure_data_file('newquestions.json')
            questions = data.get('questions', [])
            question_data['id'] = generate_next_id(questions)
            questions.append(question_data)
            data['questions'] = questions
            success = self.write_json('newquestions.json', data, f"Kysymys {question_data['id']} lisätty")
            if success:
                self.get_meta()
                self.queue_for_ipfs_sync(question_data['id'])
            return f"mock_cid_{question_data['id']}" if success else None
        except Exception as e:
            if self.debug:
                print(f"❌ Kysymyksen lisäys epäonnistui: {e}")
            return None

    def add_candidate(self, candidate_data):
        if not self.is_content_editing_allowed():
            if self.debug:
                print("🔒 Ehdokkaiden lisäys estetty – aikalukitus aktiivinen")
            return None
        try:
            for ans in candidate_data.get('answers', []):
                ans.setdefault('justification', {'fi': '', 'en': '', 'sv': ''})
                ans.setdefault('justification_metadata', {
                    'created_at': datetime.now().isoformat(),
                    'version': 1,
                    'blocked': False,
                    'signature': None
                })
            data = self.ensure_data_file('candidates.json')
            candidates = data.get('candidates', [])
            candidate_data['id'] = generate_next_id(candidates)
            candidates.append(candidate_data)
            data['candidates'] = candidates
            success = self.write_json('candidates.json', data, f"Ehdokas {candidate_data.get('name')} lisätty")
            if success:
                self.get_meta()
            return candidate_data['id'] if success else None
        except Exception as e:
            if self.debug:
                print(f"❌ Ehdokkaan lisäys epäonnistui: {e}")
            return None

    def block_question(self, question_id, reason=None):
        if not self.is_content_editing_allowed():
            if self.debug:
                print("🔒 Kysymysten muokkaus estetty – aikalukitus aktiivinen")
            return False
        official = self.ensure_data_file('questions.json')
        user = self.ensure_data_file('newquestions.json')
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
        queue = self.ensure_data_file('ipfs_sync_queue.json')
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
        queue = self.ensure_data_file('ipfs_sync_queue.json')
        if not queue.get('pending_questions'):
            return False
        last_sync = queue.get('last_sync')
        interval = queue.get('sync_interval_minutes', 10)
        if last_sync:
            last_sync_time = datetime.fromisoformat(last_sync.replace('Z', '+00:00'))
            if (datetime.now() - last_sync_time).total_seconds() < interval * 60:
                return False
        max_sync = queue.get('max_questions_per_sync', 20)
        pending = [q for q in queue['pending_questions'] if q['status'] == 'pending']
        selection_mode = self.get_meta().get('community_moderation', {}).get('ipfs_sync_mode', 'elo_priority')
        if selection_mode == 'elo_priority':
            pending.sort(key=lambda x: x.get('elo_rating', 1200), reverse=True)
        else:
            pending.sort(key=lambda x: x.get('added_to_queue_at', ''))
        selected = pending[:max_sync]
        if self.ipfs_client and selected:
            ipfs_questions = []
            all_questions = self.get_questions(include_blocked=True, include_ipfs=False)
            for item in selected:
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
        if not self.ipfs_client:
            return False
        try:
            well_known_cid = "QmWellKnownQuestionsList"
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
        if not self.is_content_editing_allowed():
            if self.debug:
                print("🔒 Elo-päivitys estetty – aikalukitus aktiivinen")
            return False
        all_questions = self.get_questions(include_blocked=True, include_ipfs=True)
        question = next((q for q in all_questions if q.get('id') == question_id), None)
        if not question:
            return False
        new_delta = {
            'timestamp': datetime.now().isoformat(),
            'delta': delta,
            'by': user_id
        }
        question['elo']['deltas'].append(new_delta)
        question['elo']['current_rating'] = self.calculate_current_elo(
            question['elo']['base_rating'],
            question['elo']['deltas']
        )
        official = self.ensure_data_file('questions.json')
        user = self.ensure_data_file('newquestions.json')
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
            self.queue_for_ipfs_sync(question_id)
        return updated

    def update_system_chain_ipfs(self, modified_files: list, ipfs_cids: dict = None):
        if ipfs_cids is None:
            ipfs_cids = {}

        chain_path = os.path.join(self.data_dir, 'system_chain.json')
        if os.path.exists(chain_path):
            with open(chain_path, 'r', encoding='utf-8') as f:
                chain = json.load(f)
        else:
            chain = {
                "chain_id": "default_election",
                "created_at": datetime.now().isoformat(),
                "description": "Fingerprint-ketju kaikille järjestelmän tiedostoille",
                "version": "0.0.6-alpha",
                "blocks": [],
                "current_state": {},
                "ipfs_cids": {},
                "metadata": {
                    "algorithm": "sha256",
                    "system_id": "",
                    "election_id": "default_election"
                }
            }

        for filepath in modified_files:
            filename = os.path.basename(filepath)
            full_path = os.path.join(self.data_dir, filename)
            if os.path.exists(full_path):
                with open(full_path, 'rb') as f:
                    chain['current_state'][filename] = hashlib.sha256(f.read()).hexdigest()

        current_cids = chain.get('ipfs_cids', {})
        current_cids.update(ipfs_cids)
        chain['ipfs_cids'] = current_cids

        last_block = chain['blocks'][-1] if chain['blocks'] else None
        new_block = {
            "block_id": len(chain['blocks']),
            "timestamp": datetime.now().isoformat(),
            "description": f"IPFS-päivitys: {', '.join(modified_files)}",
            "files": chain['current_state'].copy(),
            "ipfs_cids": current_cids.copy(),
            "previous_hash": last_block['block_hash'] if last_block else None
        }

        block_data = {k: v for k, v in new_block.items() if k != 'block_hash'}
        block_hash = hashlib.sha256(json.dumps(block_data, sort_keys=True).encode()).hexdigest()
        new_block['block_hash'] = f"sha256:{block_hash}"

        try:
            private_key = self._load_private_key()
            signature = private_key.sign(
                json.dumps(block_data, sort_keys=True).encode(),
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256()
            )
            new_block['signature'] = base64.b64encode(signature).decode()
        except Exception as e:
            if self.debug:
                print(f"⚠️  Allekirjoitus epäonnistui: {e}")
            new_block['signature'] = None

        chain['blocks'].append(new_block)

        try:
            clean_chain = {k: v for k, v in chain.items() if k != 'metadata'}
            chain_signature = private_key.sign(
                json.dumps(clean_chain, sort_keys=True).encode(),
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256()
            )
            chain['metadata']['signature'] = base64.b64encode(chain_signature).decode()
        except Exception as e:
            if self.debug:
                print(f"⚠️  Ketjun allekirjoitus epäonnistui: {e}")
            chain['metadata']['signature'] = None

        success = self.write_json('system_chain.json', chain, "IPFS-system chain päivitetty")
        if success:
            cid_str = ', '.join(f"{k}:{v}" for k, v in ipfs_cids.items()) if ipfs_cids else "ei CID:iä"
            with open("security_audit.log", "a", encoding="utf-8") as log:
                log.write(f"{datetime.now().isoformat()} | ACTION=chain_update | FILES={', '.join(modified_files)} | CIDS={cid_str}\n")
        return success

    def lock_election_content(self):
        if not self.ipfs_client:
            raise RuntimeError("IPFS-asiakas vaaditaan")

        questions = self.ensure_data_file('questions.json')
        candidates = self.ensure_data_file('candidates.json')
        meta = self.get_meta()

        snapshot = {
            "election_id": meta["election"]["id"],
            "locked_at": datetime.now().isoformat(),
            "questions": questions.get("questions", []),
            "candidates": candidates.get("candidates", []),
            "meta_hash": meta["integrity"]["hash"]
        }

        result = self.ipfs_client.add_json(snapshot)
        cid = result["Hash"]

        self.update_system_chain_ipfs(
            modified_files=['election_snapshot.json'],
            ipfs_cids={'election_snapshot.json': cid}
        )

        with open("security_audit.log", "a", encoding="utf-8") as log:
            log.write(f"{datetime.now().isoformat()} | ACTION=election_lock | CID={cid}\n")

        return cid
