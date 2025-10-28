# question_pipeline.py
class QuestionPipeline:
    def __init__(self, runtime_dir="runtime"):
        self.runtime_dir = runtime_dir
        
    def add_new_question(self, question_data):
        """Lisää uusi kysymys putkeen"""
        # 1. Lataa new_questions.json
        new_questions = self._load_json('new_questions.json')
        
        # 2. Luo tmp_new_questions.json
        tmp_questions = new_questions.copy()
        
        # 3. Lisää uusi kysymys väliaikaiseen tiedostoon
        question_id = self._generate_question_id()
        question_data['id'] = question_id
        question_data['status'] = 'new'
        question_data['created_at'] = datetime.now().isoformat()
        question_data['elo_rating'] = {
            'base_rating': 1000,
            'comparison_delta': 0,
            'vote_delta': 0,
            'current_rating': 1000
        }
        
        tmp_questions['data'].append(question_data)
        
        # 4. Tallenna tmp tiedosto
        self._save_json('tmp_new_questions.json', tmp_questions)
        
        return question_id
        
    def sync_new_to_main(self):
        """Synkronoi new_questions.json → questions.json"""
        # 1. Lataa tmp_new_questions.json
        tmp_questions = self._load_json('tmp_new_questions.json')
        
        # 2. Lataa questions.json
        main_questions = self._load_json('questions.json')
        
        # 3. Siirrä uudet kysymykset
        for question in tmp_questions['data']:
            if question['status'] == 'new':
                question['status'] = 'active'
                main_questions['data'].append(question)
        
        # 4. Päivitä tiedostot
        self._save_json('questions.json', main_questions)
        
        # 5. Tyhjennä tmp ja päivitä new_questions
        tmp_questions['data'] = [q for q in tmp_questions['data'] if q['status'] != 'new']
        self._save_json('new_questions.json', tmp_questions)
        self._save_json('tmp_new_questions.json', {'data': []})
        
        print("Synkronoitu new_questions.json -> questions.json")
