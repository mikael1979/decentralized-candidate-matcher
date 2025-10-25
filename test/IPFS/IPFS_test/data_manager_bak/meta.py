import json
from datetime import datetime
from utils import calculate_hash

class MetaMixin:
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
