# services/content_service.py
import json
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from utils import calculate_hash, generate_next_id
from data_schemas import SCHEMA_MAP

class ContentService:
    def __init__(self, data_dir: str = 'data', debug: bool = False):
        self.data_dir = data_dir
        self.debug = debug

    def _read_json_safe(self, filepath: str):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            if self.debug:
                print(f"❌ Virhe lukemisessa {filepath}: {e}")
            return None

    def _write_json(self, filename: str, data: Any, operation: str = "") -> bool:
        """Käyttää DataManagerin write_json -logiikkaa – siirretään myöhemmin file_io.py:hyn"""
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

    def _ensure_data_file(self, filename: str) -> Optional[Dict]:
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
            raise ValueError("meta.json ei kuulu ContentServiceen")
        else:
            data = schema_func(**kwargs)

        self._write_json(filename, data, f"Luotiin puuttuva tiedosto: {filename}")
        return data

    def calculate_current_elo(self, base_rating: float, deltas: List[Dict]) -> float:
        return base_rating + sum(d.get('delta', 0) for d in deltas)

    def get_questions(self, include_blocked: bool = False, include_ipfs: bool = True) -> List[Dict]:
        all_questions = []
        official = self._ensure_data_file('questions.json')
        user = self._ensure_data_file('newquestions.json')
        all_questions.extend(official.get('questions', []))
        all_questions.extend(user.get('questions', []))
        if include_ipfs:
            ipfs_cache = self._ensure_data_file('ipfs_questions_cache.json')
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

    def get_candidates(self) -> List[Dict]:
        data = self._ensure_data_file('candidates.json')
        return data.get('candidates', [])

    def get_comments(self) -> List[Dict]:
        data = self._ensure_data_file('comments.json')
        return data.get('comments', [])

    def add_question(self, question_data: Dict, is_editing_allowed: bool) -> Optional[str]:
        if not is_editing_allowed:
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
            data = self._ensure_data_file('newquestions.json')
            questions = data.get('questions', [])
            question_data['id'] = generate_next_id(questions)
            questions.append(question_data)
            data['questions'] = questions
            success = self._write_json('newquestions.json', data, f"Kysymys {question_data['id']} lisätty")
            return f"mock_cid_{question_data['id']}" if success else None
        except Exception as e:
            if self.debug:
                print(f"❌ Kysymyksen lisäys epäonnistui: {e}")
            return None

    def add_candidate(self, candidate_data: Dict, is_editing_allowed: bool) -> Optional[int]:
        if not is_editing_allowed:
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
            data = self._ensure_data_file('candidates.json')
            candidates = data.get('candidates', [])
            candidate_data['id'] = generate_next_id(candidates)
            candidates.append(candidate_data)
            data['candidates'] = candidates
            success = self._write_json('candidates.json', data, f"Ehdokas {candidate_data.get('name')} lisätty")
            return candidate_data['id'] if success else None
        except Exception as e:
            if self.debug:
                print(f"❌ Ehdokkaan lisäys epäonnistui: {e}")
            return None

    def block_question(self, question_id: int, reason: Optional[str], is_editing_allowed: bool) -> bool:
        if not is_editing_allowed:
            if self.debug:
                print("🔒 Kysymysten muokkaus estetty – aikalukitus aktiivinen")
            return False
        official = self._ensure_data_file('questions.json')
        user = self._ensure_data_file('newquestions.json')
        found = False
        for q in official.get('questions', []):
            if q.get('id') == question_id:
                q.setdefault('metadata', {})['blocked'] = True
                q['metadata']['blocked_reason'] = reason
                self._write_json('questions.json', official, f"Kysymys {question_id} blokattu")
                found = True
                break
        if not found:
            for q in user.get('questions', []):
                if q.get('id') == question_id:
                    q.setdefault('metadata', {})['blocked'] = True
                    q['metadata']['blocked_reason'] = reason
                    self._write_json('newquestions.json', user, f"Kysymys {question_id} blokattu")
                    found = True
                    break
        return found

    def apply_elo_delta(self, question_id: int, delta: float, user_id: str, is_editing_allowed: bool) -> bool:
        if not is_editing_allowed:
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
        official = self._ensure_data_file('questions.json')
        user = self._ensure_data_file('newquestions.json')
        updated = False
        for q in official.get('questions', []):
            if q.get('id') == question_id:
                q['elo'] = question['elo']
                self._write_json('questions.json', official, f"Elo päivitetty kysymykselle {question_id}")
                updated = True
                break
        if not updated:
            for q in user.get('questions', []):
                if q.get('id') == question_id:
                    q['elo'] = question['elo']
                    self._write_json('newquestions.json', user, f"Elo päivitetty kysymykselle {question_id}")
                    updated = True
                    break
        return updated
