from datetime import datetime

class EloMixin:
    def calculate_current_elo(self, base_rating, deltas):
        return base_rating + sum(d.get('delta', 0) for d in deltas)

    def apply_elo_delta(self, question_id, delta, user_id):
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
