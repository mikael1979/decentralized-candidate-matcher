from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import os
from datetime import datetime
from question_submission import QuestionSubmission, QuestionSearch
from mock_ipfs import MockIPFS
from party_profile import PartyProfile, PartyComparison
import random
import threading

app = Flask(__name__, static_folder='static', template_folder='templates')

# Alusta komponentit
ipfs = MockIPFS()

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
    
    def _load_candidates(self):
        try:
            with open('data/candidates.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('candidates', [])
        except FileNotFoundError:
            return []
    
    def add_question(self, question_data, is_official=False):
        try:
            user_questions = self._load_user_questions()
            # Luo uusi ID
            new_id = max([q.get('id', 0) for q in user_questions], default=0) + 1
            question_data['id'] = new_id
            
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
            
            return f"mock_cid_{new_id}"
            
        except Exception as e:
            raise Exception(f"Kysymyksen tallentaminen epäonnistui: {str(e)}")
    
    def get_election_data(self, filename):
        if filename == "candidates.json":
            return {"candidates": self._load_candidates()}
        elif filename == "questions.json":
            return {"questions": self._load_questions()}
        return {}

# IPFS Synkronointimanageri
class IPFSSyncManager:
    def __init__(self, ipfs, election_manager):
        self.ipfs = ipfs
        self.election_manager = election_manager
        self.sync_status = {
            'last_sync': None,
            'peers_found': 0,
            'data_imported': 0,
            'status': 'not_started'
        }
        self.auto_sync_interval = 300  # 5 minuuttia
        self.is_auto_sync_enabled = False
    
    def manual_sync(self):
        """Manuaalinen synkronointi admin-sivulta"""
        self.sync_status.update({
            'status': 'syncing',
            'last_sync': datetime.now().isoformat(),
            'peers_found': 0,
            'data_imported': 0
        })
        
        try:
            # 1. Etsi muita vaalikonnejärjestelmiä IPFS-verkosta
            peers = self.discover_peers()
            self.sync_status['peers_found'] = len(peers)
            
            # 2. Hae data kustakin peeristä
            imported_data = 0
            for peer in peers:
                if self.sync_from_peer(peer):
                    imported_data += 1
            
            self.sync_status.update({
                'status': 'completed',
                'data_imported': imported_data
            })
            
            return True
            
        except Exception as e:
            self.sync_status.update({
                'status': 'error',
                'error': str(e)
            })
            return False
    
    def discover_peers(self):
        """Etsi muita vaalikonnejärjestelmiä IPFS-verkosta"""
        # Tässä mock-toteutus - oikeassa järjestelmässä käytettäisiin IPFS:n DHT:ta
        mock_peers = [
            {
                'id': 'peer_1',
                'cid': 'mock_cid_123',
                'last_updated': '2024-01-15T10:30:00',
                'data_type': 'election_data'
            },
            {
                'id': 'peer_2', 
                'cid': 'mock_cid_456',
                'last_updated': '2024-01-14T15:45:00',
                'data_type': 'questions'
            }
        ]
        return mock_peers
    
    def sync_from_peer(self, peer):
        """Synkronoi data yhdeltä peeriltä"""
        try:
            # Hae data IPFS:stä
            peer_data = self.ipfs.get_json(peer['cid'])
            
            if peer_data and self.validate_peer_data(peer_data):
                # Integroi data paikalliseen järjestelmään
                self.integrate_peer_data(peer_data, peer['data_type'])
                return True
                
        except Exception as e:
            print(f"Virhe synkronoidessa peeriltä {peer['id']}: {e}")
        
        return False
    
    def validate_peer_data(self, data):
        """Validoi peerin data ennen integrointia"""
        required_fields = {
            'election_data': ['candidates', 'questions'],
            'questions': ['questions']
        }
        
        data_type = data.get('data_type', 'election_data')
        required = required_fields.get(data_type, [])
        
        return all(field in data for field in required)
    
    def integrate_peer_data(self, peer_data, data_type):
        """Integroi peerin data paikalliseen järjestelmään"""
        if data_type == 'questions':
            self._integrate_questions(peer_data.get('questions', []))
        elif data_type == 'election_data':
            self._integrate_election_data(peer_data)
    
    def _integrate_questions(self, questions):
        """Integroi kysymykset"""
        current_questions = self.election_manager.get_all_questions()
        current_ids = {q['id'] for q in current_questions}
        
        new_questions = 0
        for question in questions:
            if question['id'] not in current_ids:
                # Lisää uusi kysymys
                self.election_manager.add_question(question, is_official=False)
                new_questions += 1
        
        return new_questions
    
    def _integrate_election_data(self, election_data):
        """Integroi vaalidata"""
        # Toteutus riippuu datan rakenteesta
        # Tässä yksinkertaistettu esimerkki
        candidates = election_data.get('candidates', [])
        print(f"Integroidaan {len(candidates)} ehdokasta")
    
    def get_sync_status(self):
        """Palauta synkronoinnin tila"""
        return self.sync_status

    def enable_auto_sync(self):
        """Ota automaattinen synkronointi käyttöön"""
        self.is_auto_sync_enabled = True
        self.start_auto_sync()
    
    def disable_auto_sync(self):
        """Poista automaattinen synkronointi käytöstä"""
        self.is_auto_sync_enabled = False
    
    def start_auto_sync(self):
        """Käynnistä automaattinen synkronointi"""
        if self.is_auto_sync_enabled:
            # Ajastettu synkronointi
            threading.Timer(self.auto_sync_interval, self.auto_sync_cycle).start()
    
    def auto_sync_cycle(self):
        """Automaattisen synkronoinnin sykli"""
        if self.is_auto_sync_enabled:
            print("Suoritetaan automaattinen synkronointi...")
            self.manual_sync()
            self.start_auto_sync()  # Käynnistä seuraava sykli

# Alusta managerit
election_manager = SimpleElectionManager()
question_submission = QuestionSubmission(ipfs, election_manager)
question_search = QuestionSearch(election_manager)
party_profile = PartyProfile(ipfs, election_manager)
party_comparison = PartyComparison(ipfs, election_manager)
ipfs_sync_manager = IPFSSyncManager(ipfs, election_manager)

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

# API-reitit
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
        candidates = election_manager._load_candidates()
        return jsonify(candidates)
    except FileNotFoundError:
        return jsonify([])

@app.route('/api/parties')
def get_parties():
    try:
        parties = party_comparison.get_all_parties()
        return jsonify(parties)
    except Exception as e:
        print(f"Virhe puolueiden haussa: {e}")
        return jsonify(["Test Puolue", "Toinen Puolue", "Kolmas Puolue"])

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

# PUUTTUNUT API-REITTI - LISÄTTY TÄHÄN
@app.route('/api/generate_party_profile/<party_name>', methods=['POST'])
def generate_party_profile(party_name):
    """Luo puolueprofiilin ja julkaisee sen IPFS:ään"""
    try:
        print(f"🎯 API-kutsu: Luodaan profiilia puolueelle '{party_name}'")
        
        profile_cid = party_profile.publish_party_profile(party_name)
        
        response_data = {
            'success': True,
            'party_name': party_name,
            'cid': profile_cid,
            'message': f'Puolueprofiili luotu onnistuneesti puolueelle {party_name}'
        }
        
        print(f"✅ API-vastaus: {response_data}")
        
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = f"Virhe puolueprofiilin luonnissa: {str(e)}"
        print(f"❌ API-virhe: {error_msg}")
        
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

@app.route('/api/search', methods=['POST'])
def search_candidates():
    try:
        user_answers = request.json
        
        candidates = election_manager._load_candidates()
        results = []
        
        for candidate in candidates:
            match_percentage = calculate_match(user_answers, candidate)
            
            matched_questions = 0
            match_details = []
            
            for answer in candidate.get('answers', []):
                question_id = str(answer['question_id'])
                if question_id in user_answers:
                    matched_questions += 1
                    match_details.append({
                        'question_id': question_id,
                        'candidate_answer': answer['answer'],
                        'user_answer': user_answers[question_id]
                    })
            
            if matched_questions > 0:
                results.append({
                    'candidate': candidate,
                    'match_percentage': match_percentage,
                    'matched_questions': matched_questions,
                    'match_details': match_details
                })
        
        results.sort(key=lambda x: x['match_percentage'], reverse=True)
        
        return jsonify({
            'success': True,
            'matches': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def calculate_match(user_answers, candidate):
    total_diff = 0
    max_possible_diff = 0
    answered_count = 0
    
    for answer in candidate.get('answers', []):
        question_id = str(answer['question_id'])
        if question_id in user_answers:
            user_answer = user_answers[question_id]
            candidate_answer = answer['answer']
            
            diff = abs(user_answer - candidate_answer)
            total_diff += diff
            max_possible_diff += 10
            answered_count += 1
    
    if answered_count == 0:
        return 0
    
    match_percentage = 1 - (total_diff / max_possible_diff)
    return match_percentage

# Kysymysten hallinta API-reitit
@app.route('/api/submit_question', methods=['POST'])
def submit_question():
    try:
        question_data = request.json
        
        # Tarkista pakolliset kentät
        if not question_data.get('question', {}).get('fi'):
            return jsonify({
                'success': False,
                'errors': ['Kysymys suomeksi on pakollinen']
            }), 400
        
        if not question_data.get('category'):
            return jsonify({
                'success': False,
                'errors': ['Kategoria on pakollinen']
            }), 400
        
        if not question_data.get('tags'):
            return jsonify({
                'success': False,
                'errors': ['Vähintään yksi tagi on pakollinen']
            }), 400
        
        # Lisää puuttuvat kentät
        question_data['scale'] = question_data.get('scale', {
            'min': -5,
            'max': 5,
            'labels': {
                'fi': {'-5': 'Täysin eri mieltä', '0': 'Neutraali', '5': 'Täysin samaa mieltä'}
            }
        })
        
        # Lähetä kysymys
        cid = election_manager.add_question(question_data)
        
        return jsonify({
            'success': True,
            'cid': cid,
            'message': 'Kysymys lähetetty onnistuneesti'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'errors': [f'Lähetys epäonnistui: {str(e)}']
        }), 500

@app.route('/api/search_questions')
def search_questions_api():
    try:
        query = request.args.get('q', '')
        tags = request.args.getlist('tags')
        category = request.args.get('category')
        
        results = question_search.search_questions(
            query=query,
            tags=tags,
            category=category
        )
        
        return jsonify({
            'success': True,
            'results': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/available_tags')
def get_available_tags():
    try:
        # Kerää kaikkien kysymysten tagit
        questions = election_manager.get_all_questions()
        tag_counts = {}
        
        for question in questions:
            for tag in question.get('tags', []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        return jsonify({
            'success': True,
            'tags': tag_counts
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/status')
def get_status():
    questions = election_manager._load_questions()
    user_questions = election_manager._load_user_questions()
    candidates = election_manager._load_candidates()
    
    # Kerää puolueet
    parties = []
    try:
        parties = party_comparison.get_all_parties()
    except:
        parties = list(set(candidate.get('party', '') for candidate in candidates if candidate.get('party')))
    
    return jsonify({
        'official_questions': len(questions),
        'user_questions': len(user_questions),
        'candidates': len(candidates),
        'parties': len(parties),
        'timestamp': datetime.now().isoformat()
    })

# Puoluevertailu API-reitit
@app.route('/api/compare_parties', methods=['POST'])
def compare_parties():
    try:
        data = request.json
        user_answers = data.get('user_answers', {})
        party_name = data.get('party_name')
        
        # Yksinkertainen vertailu
        party_candidates = [c for c in election_manager._load_candidates() 
                          if c.get('party') == party_name]
        
        if not party_candidates:
            return jsonify({
                'success': False,
                'error': 'Puoluetta ei löytynyt'
            }), 404
        
        total_match = 0
        match_count = 0
        
        for candidate in party_candidates:
            match_score = calculate_match(user_answers, candidate)
            total_match += match_score
            match_count += 1
        
        avg_match = total_match / match_count if match_count > 0 else 0
        
        return jsonify({
            'success': True,
            'match_percentage': avg_match * 100,
            'match_score': total_match,
            'max_possible_score': match_count,
            'matched_questions': len(user_answers),
            'candidate_count': len(party_candidates)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/compare_all_parties', methods=['POST'])
def compare_all_parties():
    try:
        user_answers = request.json.get('user_answers', {})
        parties = party_comparison.get_all_parties()
        
        comparisons = []
        for party in parties:
            # Yksinkertainen vertailu
            party_candidates = [c for c in election_manager._load_candidates() 
                              if c.get('party') == party]
            
            if party_candidates:
                total_match = sum(calculate_match(user_answers, c) for c in party_candidates)
                avg_match = total_match / len(party_candidates)
                
                comparisons.append({
                    'party_name': party,
                    'match_percentage': avg_match * 100,
                    'candidate_count': len(party_candidates),
                    'overall_consensus': random.randint(60, 95)  # Mock data
                })
        
        comparisons.sort(key=lambda x: x['match_percentage'], reverse=True)
        
        return jsonify(comparisons)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Admin API-reitit
@app.route('/api/admin/status')
def admin_status():
    return jsonify({
        'is_running': True,
        'active_users': random.randint(1, 50),
        'last_backup': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/admin/moderation_queue')
def moderation_queue():
    # Mock data - oikeassa sovelluksessa haettaisiin tietokannasta
    return jsonify([])

@app.route('/api/admin/ipfs_status')
def ipfs_status():
    return jsonify({
        'connected': True,
        'peer_count': random.randint(5, 20),
        'storage_used': '125 MB',
        'storage_max': '1 GB',
        'pinned_count': random.randint(10, 50)
    })

@app.route('/api/admin/stats')
def admin_stats():
    questions = election_manager._load_questions()
    user_questions = election_manager._load_user_questions()
    candidates = election_manager._load_candidates()
    
    return jsonify({
        'total_users': random.randint(100, 1000),
        'total_questions': len(questions) + len(user_questions),
        'total_candidates': len(candidates),
        'total_parties': len(set(c.get('party', '') for c in candidates if c.get('party')))
    })

@app.route('/api/admin/export_data')
def export_data():
    # Mock data export
    data = {
        'questions': election_manager.get_all_questions(),
        'candidates': election_manager._load_candidates(),
        'exported_at': datetime.now().isoformat()
    }
    
    return jsonify(data)

@app.route('/api/admin/import_data', methods=['POST'])
def import_data():
    # Mock import
    return jsonify({'success': True, 'message': 'Data tuotu onnistuneesti'})

@app.route('/api/admin/clear_cache', methods=['POST'])
def clear_cache():
    # Mock cache clear
    return jsonify({'success': True, 'message': 'Välimuisti tyhjennetty'})

@app.route('/api/admin/approve_question/<int:question_id>', methods=['POST'])
def approve_question(question_id):
    # Mock approval
    return jsonify({'success': True, 'message': 'Kysymys hyväksytty'})

@app.route('/api/admin/reject_question/<int:question_id>', methods=['POST'])
def reject_question(question_id):
    # Mock rejection
    return jsonify({'success': True, 'message': 'Kysymys hylätty'})

# IPFS Synkronointi API-reitit
@app.route('/api/admin/sync', methods=['POST'])
def manual_sync():
    """Käynnistä manuaalinen synkronointi"""
    try:
        success = ipfs_sync_manager.manual_sync()
        status = ipfs_sync_manager.get_sync_status()
        
        return jsonify({
            'success': success,
            'status': status
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/admin/sync_status')
def get_sync_status():
    """Hae synkronoinnin tila"""
    status = ipfs_sync_manager.get_sync_status()
    return jsonify(status)

@app.route('/api/admin/peers')
def get_peers():
    """Hae löydetyt peerit"""
    peers = ipfs_sync_manager.discover_peers()
    return jsonify(peers)

@app.route('/api/admin/enable_auto_sync', methods=['POST'])
def enable_auto_sync():
    """Ota automaattinen synkronointi käyttöön"""
    try:
        ipfs_sync_manager.enable_auto_sync()
        return jsonify({
            'success': True,
            'message': 'Automaattinen synkronointi käytössä'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/admin/disable_auto_sync', methods=['POST'])
def disable_auto_sync():
    """Poista automaattinen synkronointi käytöstä"""
    try:
        ipfs_sync_manager.disable_auto_sync()
        return jsonify({
            'success': True,
            'message': 'Automaattinen synkronointi pois käytöstä'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Varmista että kansiot ovat olemassa
    os.makedirs('data', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Luo tarvittavat tiedostot jos ne eivät ole olemassa
    if not os.path.exists('data/questions.json'):
        with open('data/questions.json', 'w', encoding='utf-8') as f:
            json.dump({
                "questions": [
                    {
                        "id": 1,
                        "category": {"fi": "Ympäristö", "en": "Environment"},
                        "question": {
                            "fi": "Pitäisikö kaupungin vähentää hiilidioksidipäästöjä 50% vuoteen 2030 mennessä?",
                            "en": "Should the city reduce carbon dioxide emissions by 50% by 2030?"
                        },
                        "tags": ["ympäristö", "hiilidioksidi", "ilmasto"]
                    },
                    {
                        "id": 2,
                        "category": {"fi": "Liikenne", "en": "Transportation"},
                        "question": {
                            "fi": "Pitäisikö kaupunkipyörien määrää lisätä kesäkaudella?",
                            "en": "Should the number of city bikes be increased during summer season?"
                        },
                        "tags": ["liikenne", "kaupunkipyörät", "kesä"]
                    }
                ]
            }, f, indent=2, ensure_ascii=False)
    
    if not os.path.exists('data/candidates.json'):
        with open('data/candidates.json', 'w', encoding='utf-8') as f:
            json.dump({
                "candidates": [
                    {
                        "id": 1,
                        "name": "Matti Meikäläinen",
                        "party": "Test Puolue",
                        "district": "Helsinki",
                        "answers": [
                            {"question_id": 1, "answer": 4, "confidence": 0.8},
                            {"question_id": 2, "answer": 3, "confidence": 0.6}
                        ]
                    },
                    {
                        "id": 2,
                        "name": "Liisa Esimerkki",
                        "party": "Toinen Puolue",
                        "district": "Espoo",
                        "answers": [
                            {"question_id": 1, "answer": 2, "confidence": 0.5},
                            {"question_id": 2, "answer": 5, "confidence": 0.8}
                        ]
                    }
                ]
            }, f, indent=2, ensure_ascii=False)
    
    if not os.path.exists('data/newquestions.json'):
        with open('data/newquestions.json', 'w', encoding='utf-8') as f:
            json.dump({
                "election_id": "test_election_2024",
                "language": "fi",
                "question_type": "user_submitted",
                "questions": []
            }, f, indent=2, ensure_ascii=False)
    
    print("🚀 Käynnistetään Hajautettu Vaalikone...")
    print("📊 Sovellus saatavilla: http://localhost:5000")
    print("📝 Sivut:")
    print("   - http://localhost:5000 (Etusivu)")
    print("   - http://localhost:5000/vaalikone (Vaalikone)")
    print("   - http://localhost:5000/kysymysten-hallinta (Kysymysten hallinta)")
    print("   - http://localhost:5000/puolueet (Puoluevertailu)")
    print("   - http://localhost:5000/admin (Ylläpito)")
    print("🔧 API-reitit:")
    print("   - /api/generate_party_profile/<party_name> [POST] - LUOTU PUOLUEPROFIILEJA VARTEN")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
