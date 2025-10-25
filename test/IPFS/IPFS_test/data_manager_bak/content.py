from datetime import datetime
from utils import generate_next_id

class ContentMixin:
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

    def add_question(self, question_data):
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
