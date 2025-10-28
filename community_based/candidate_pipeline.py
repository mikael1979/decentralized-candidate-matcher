# candidate_pipeline.py
class CandidatePipeline:
    def __init__(self, runtime_dir="runtime"):
        self.runtime_dir = runtime_dir
        
    def add_new_candidate_profile(self, candidate_data):
        """Lisää uusi ehdokasprofiili putkeen"""
        # 1. Lataa new_candidate_profiles.json
        new_profiles = self._load_json('new_candidate_profiles.json')
        
        # 2. Luo tmp_new_candidate_profiles.json
        tmp_profiles = new_profiles.copy()
        
        # 3. Lisää uusi ehdokas väliaikaiseen tiedostoon
        candidate_id = self._generate_candidate_id()
        candidate_data['candidate_id'] = candidate_id
        candidate_data['profile_metadata'] = {
            'status': 'new',
            'created_at': datetime.now().isoformat(),
            'last_modified': datetime.now().isoformat(),
            'version': '1.0.0',
            'completeness_score': self._calculate_completeness(candidate_data)
        }
        
        tmp_profiles['candidates'].append(candidate_data)
        
        # 4. Tallenna tmp tiedosto
        self._save_json('tmp_new_candidate_profiles.json', tmp_profiles)
        
        return candidate_id
        
    def add_candidate_answer(self, candidate_id, question_id, answer_data):
        """Lisää vastaus ehdokkaan profiiliin"""
        # 1. Lataa candidate_profiles.json
        profiles = self._load_json('candidate_profiles.json')
        
        # 2. Etsi ehdokas
        candidate = self._find_candidate(profiles, candidate_id)
        if not candidate:
            raise ValueError(f"Ehdokasta ei löydy: {candidate_id}")
            
        # 3. Päivitä tai lisää vastaus
        existing_answer = None
        for answer in candidate['answers']:
            if answer['question_id'] == question_id:
                existing_answer = answer
                break
                
        if existing_answer:
            # Päivitä olemassa oleva vastaus
            existing_answer.update({
                'answer_value': answer_data['answer_value'],
                'explanation': answer_data['explanation'],
                'confidence': answer_data.get('confidence', 3),
                'last_updated': datetime.now().isoformat()
            })
        else:
            # Lisää uusi vastaus
            candidate['answers'].append({
                'question_id': question_id,
                'answer_value': answer_data['answer_value'],
                'explanation': answer_data['explanation'],
                'confidence': answer_data.get('confidence', 3),
                'last_updated': datetime.now().isoformat()
            })
        
        # 4. Päivitä profiilin metadata
        candidate['profile_metadata']['last_modified'] = datetime.now().isoformat()
        candidate['profile_metadata']['completeness_score'] = self._calculate_completeness(candidate)
        
        # 5. Tallenna
        self._save_json('candidate_profiles.json', profiles)
        
        print(f"Vastaus lisätty ehdokkaalle {candidate_id}, kysymys {question_id}")
        
    def sync_new_candidates_to_main(self):
        """Synkronoi new_candidate_profiles.json → candidate_profiles.json"""
        # 1. Lataa tmp_new_candidate_profiles.json
        tmp_profiles = self._load_json('tmp_new_candidate_profiles.json')
        
        # 2. Lataa candidate_profiles.json
        main_profiles = self._load_json('candidate_profiles.json')
        
        # 3. Siirrä uudet ehdokkaat
        new_count = 0
        for candidate in tmp_profiles['candidates']:
            if candidate['profile_metadata']['status'] == 'new':
                candidate['profile_metadata']['status'] = 'active'
                main_profiles['candidates'].append(candidate)
                new_count += 1
        
        # 4. Päivitä metadata
        main_profiles['metadata']['total_candidates'] = len(main_profiles['candidates'])
        main_profiles['metadata']['last_updated'] = datetime.now().isoformat()
        
        # 5. Päivitä tiedostot
        self._save_json('candidate_profiles.json', main_profiles)
        
        # 6. Tyhjennä tmp ja päivitä new_candidate_profiles
        tmp_profiles['candidates'] = [c for c in tmp_profiles['candidates'] if c['profile_metadata']['status'] != 'new']
        self._save_json('new_candidate_profiles.json', tmp_profiles)
        self._save_json('tmp_new_candidate_profiles.json', {'candidates': []})
        
        print(f"Synkronoitu {new_count} uutta ehdokasta")
        return new_count
