from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import os
from datetime import datetime
from question_submission import QuestionSubmission, QuestionSearch
from mock_ipfs import MockIPFS
from party_profile import PartyProfile, PartyComparison

app = Flask(__name__, static_folder='static', template_folder='templates')

# Alusta komponentit
ipfs = MockIPFS()
question_submission = None
question_search = None

# Yksinkertainen election_manager mock
class SimpleElectionManager:
    def get_all_questions(self):
        official = self._load_questions()
        user = self._load_user_questions()
        return official + user
    
    def _load_questions(self):
        try:
            with open('data/questions.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('questions', [])
        except FileNotFoundError:
            return []
    
    def _load_user_questions(self):
        try:
            with open('data/newquestions.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('questions', [])
        except FileNotFoundError:
            return []
    
    def add_question(self, question_data, is_official=False):
        try:
            user_questions = self._load_user_questions()
            user_questions.append(question_data)
            
            data = {
                "election_id": "test_election_2024",
                "language": "fi",
                "question_type": "user_submitted",
                "questions": user_questions
            }
            
            os.makedirs('data', exist_ok=True)
            with open('data/newquestions.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return f"mock_cid_{question_data['id']}"
            
        except Exception as e:
            raise Exception(f"Kysymyksen tallentaminen epäonnistui: {str(e)}")

# Alusta election_manager
election_manager = SimpleElectionManager()
question_submission = QuestionSubmission(ipfs, election_manager)
question_search = QuestionSearch(election_manager)
party_profile = PartyProfile(ipfs, election_manager)
party_comparison = PartyComparison(ipfs, election_manager)

# Reitit
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/vaalikone')
def vaalikone():
    return render_template('vaalikone.html')

@app.route('/kysymysten-hallinta')
def question_management():
    return render_template('question_management.html')

@app.route('/puolueet')
def parties():
    return render_template('parties.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

# API-reitit (sama kuin aiemmin)
@app.route('/api/questions')
def get_questions():
    official_questions = election_manager._load_questions()
    user_questions = election_manager._load_user_questions()
    all_questions = official_questions + user_questions
    
    for q in all_questions:
        q['id'] = str(q['id'])
    
    return jsonify(all_questions)

@app.route('/api/candidates')
def get_candidates():
    try:
        with open('data/candidates.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return jsonify(data.get('candidates', []))
    except FileNotFoundError:
        return jsonify([])

@app.route('/api/parties')
def get_parties():
    try:
        parties = party_comparison.get_all_parties()
        return jsonify(parties)
    except Exception as e:
        return jsonify([])

@app.route('/api/party/<party_name>')
def get_party_profile(party_name):
    try:
        profile = party_profile.calculate_party_answers(party_name)
        consensus = party_profile.get_party_consensus(party_name)
        return jsonify({
            'profile': profile,
            'consensus': consensus
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Muut API-reitit pysyvät samoina...
# /api/search, /api/submit_question, /api/search_questions, /api/available_tags, /api/status

if __name__ == '__main__':
    # Varmista että data-kansio on olemassa
    os.makedirs('data', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("🚀 Käynnistetään Hajautettu Vaalikone...")
    print("📊 Sovellus saatavilla: http://localhost:5000")
    print("📝 Sivut:")
    print("   - http://localhost:5000 (Etusivu)")
    print("   - http://localhost:5000/vaalikone (Vaalikone)")
    print("   - http://localhost:5000/kysymysten-hallinta (Kysymysten hallinta)")
    print("   - http://localhost:5000/puolueet (Puoluevertailu)")
    print("   - http://localhost:5000/admin (Ylläpito)")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
