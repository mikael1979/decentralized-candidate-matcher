from flask import Flask, render_template, request, jsonify
import sys
from data_manager import DataManager
from route_handlers import RouteHandlers
from utils import handle_api_errors
from admin_api import init_admin_api
from datetime import datetime

# DEBUG-tila
DEBUG = True

# Tarkista --real-ipfs -lippu
USE_REAL_IPFS = '--real-ipfs' in sys.argv

# Valitse IPFS-asiakas
if USE_REAL_IPFS:
    from real_ipfs import RealIPFS as IPFSClient
    print("🌍 Käytetään oikeaa IPFS-solmua")
else:
    from mock_ipfs import MockIPFS as IPFSClient
    print("🧪 Käytetään mock-IPFS:ää (testitila)")

# Alusta IPFS-asiakas
ipfs_client = IPFSClient()

# Alusta komponentit
data_manager = DataManager(debug=DEBUG)
data_manager.set_ipfs_client(ipfs_client)  # Uusi metodi!
handlers = RouteHandlers(data_manager, debug=DEBUG)

# Alusta data
data_manager.initialize_data_files()

# Flask-sovellus
app = Flask(__name__, static_folder='static', template_folder='templates')

# Alusta Admin API
init_admin_api(app, data_manager, handlers)

def _render_template(template, **extra_context):
    """Yhteinen template-renderöinti meta-tiedoilla"""
    meta = data_manager.get_meta()
    base_context = {
        'system_name': meta.get('system', 'Vaalikone'),
        'version': meta.get('version', '0.0.1'),
        'election_name': meta.get('election', {}).get('name', {}).get('fi', 'Testivaalit'),
        'election_date': meta.get('election', {}).get('date', '2025-04-13')
    }
    base_context.update(extra_context)
    return render_template(template, **base_context)

# Staattiset reitit
@app.route('/')
def index(): 
    return _render_template('index.html')

@app.route('/vaalikone')
def vaalikone(): 
    return _render_template('vaalikone.html')

@app.route('/kysymysten-hallinta') 
def question_management(): 
    return _render_template('question_management.html')

@app.route('/puolueet')
def parties(): 
    return _render_template('parties.html')

@app.route('/admin')
def admin(): 
    return _render_template('admin.html')

# API-reitit
@app.route('/api/meta')
@handle_api_errors
def api_meta():
    """Palauttaa järjestelmän meta-tiedot"""
    return jsonify(data_manager.get_meta())

@app.route('/api/system_info')
@handle_api_errors
def api_system_info():
    """Palauttaa järjestelmätiedot frontendia varten"""
    meta = data_manager.get_meta()
    return jsonify({
        'system_name': meta.get('system', 'Vaalikone'),
        'version': meta.get('version', '0.0.1'),
        'election': meta.get('election', {}),
        'stats': meta.get('content', {}),
        'community_moderation': meta.get('community_moderation', {})
    })

@app.route('/api/update_meta', methods=['POST'])
@handle_api_errors
def api_update_meta():
    """Päivittää meta-tiedot (admin-only)"""
    new_meta = request.json
    success = data_manager.update_meta(new_meta)
    if success:
        return jsonify({
            'success': True,
            'message': 'Meta-tiedot päivitetty onnistuneesti'
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Meta-tietojen päivitys epäonnistui'
        }), 500

@app.route('/api/questions')
@handle_api_errors
def api_questions():
    """Palauttaa kaikki kysymykset (mukaan lukien IPFS-kysymykset)"""
    questions = data_manager.get_questions()
    for q in questions:
        q['id'] = str(q['id'])
    return jsonify(questions)

@app.route('/api/candidates')
@handle_api_errors
def api_candidates():
    """Palauttaa kaikki ehdokkaat"""
    candidates = data_manager.get_candidates()
    return jsonify(candidates)

@app.route('/api/parties')
@handle_api_errors
def api_parties():
    """Palauttaa kaikki puolueet"""
    parties = handlers.get_parties()
    return jsonify(parties)

@app.route('/api/party/<party_name>')
@handle_api_errors
def api_party_profile(party_name):
    """Palauttaa puolueen profiilin"""
    profile, consensus = handlers.get_party_profile(party_name)
    return jsonify({'profile': profile, 'consensus': consensus})

@app.route('/api/add_candidate', methods=['POST'])
@handle_api_errors
def api_add_candidate():
    """Lisää uuden ehdokkaan"""
    candidate_data = request.json
    if not candidate_data.get('name'):
        return jsonify({'success': False, 'error': 'Ehdokkaan nimi on pakollinen'}), 400
    if not candidate_data.get('party'):
        return jsonify({'success': False, 'error': 'Puolue on pakollinen'}), 400
    candidate_id = data_manager.add_candidate(candidate_data)
    if candidate_id:
        return jsonify({
            'success': True,
            'candidate_id': candidate_id,
            'message': 'Ehdokas lisätty onnistuneesti'
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Ehdokkaan tallentaminen epäonnistui'
        }), 500

@app.route('/api/submit_question', methods=['POST'])
@handle_api_errors
def api_submit_question():
    """Lähettää uuden kysymyksen"""
    question_data = request.json
    if not question_data.get('question', {}).get('fi'):
        return jsonify({'success': False, 'errors': ['Kysymys suomeksi on pakollinen']}), 400
    if not question_data.get('category'):
        return jsonify({'success': False, 'errors': ['Kategoria on pakollinen']}), 400
    
    question_data.setdefault('scale', {
        'min': -5,
        'max': 5,
        'labels': {
            'fi': {'-5': 'Täysin eri mieltä', '0': 'Neutraali', '5': 'Täysin samaa mieltä'}
        }
    })
    
    cid = data_manager.add_question(question_data)
    if cid:
        return jsonify({
            'success': True,
            'cid': cid,
            'message': 'Kysymys lähetetty onnistuneesti'
        })
    else:
        return jsonify({
            'success': False,
            'errors': ['Kysymyksen tallentaminen epäonnistui']
        }), 500

@app.route('/api/search_questions')
@handle_api_errors
def api_search_questions():
    """Hakee kysymyksiä hakusanalla"""
    query = request.args.get('q', '')
    results = handlers.search_questions(query)
    return jsonify({'success': True, 'results': results})

@app.route('/api/available_tags')
@handle_api_errors
def api_available_tags():
    """Palauttaa saatavilla olevat tagit"""
    questions = data_manager.get_questions()
    tag_counts = {}
    for question in questions:
        for tag in question.get('tags', []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    return jsonify({'success': True, 'tags': tag_counts})

@app.route('/api/status')
@handle_api_errors
def api_status():
    """Palauttaa järjestelmän tilan"""
    meta = data_manager.get_meta()
    return jsonify({
        'success': True,
        'system_status': 'running',
        'meta': meta
    })

@app.route('/api/compare_parties', methods=['POST'])
@handle_api_errors
def api_compare_parties():
    """Vertaa käyttäjän vastauksia puolueeseen"""
    data = request.json
    user_answers = data.get('user_answers', {})
    party_name = data.get('party_name')
    party_candidates = [c for c in data_manager.get_candidates() if c.get('party') == party_name]
    if not party_candidates:
        return jsonify({'success': False, 'error': 'Puoluetta ei löytynyt'}), 404
    total_match = 0
    for candidate in party_candidates:
        match_score = handlers.calculate_match(user_answers, candidate)
        total_match += match_score
    avg_match = total_match / len(party_candidates) if party_candidates else 0
    return jsonify({
        'success': True,
        'match_percentage': avg_match * 100,
        'candidate_count': len(party_candidates),
        'matched_questions': len(user_answers)
    })

@app.route('/api/compare_all_parties', methods=['POST'])
@handle_api_errors
def api_compare_all_parties():
    """Vertaa käyttäjän vastauksia kaikkiin puolueisiin"""
    user_answers = request.json.get('user_answers', {})
    parties = handlers.get_parties()
    comparisons = []
    for party in parties:
        party_candidates = [c for c in data_manager.get_candidates() if c.get('party') == party]
        if party_candidates:
            total_match = sum(handlers.calculate_match(user_answers, c) for c in party_candidates)
            avg_match = total_match / len(party_candidates)
            comparisons.append({
                'party_name': party,
                'match_percentage': avg_match * 100,
                'candidate_count': len(party_candidates)
            })
    comparisons.sort(key=lambda x: x['match_percentage'], reverse=True)
    return jsonify(comparisons)

# Virheenkäsittely
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Sivua ei löytynyt'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Sisäinen palvelinvirhe'}), 500

if __name__ == '__main__':
    if DEBUG:
        print("🚀 Hajautettu Vaalikone käynnistyy...")
        print("📊 Sovellus saatavilla: http://localhost:5000")
        print("🔧 DEBUG-tila: PÄÄLLÄ")
        if USE_REAL_IPFS:
            print("🌍 IPFS-TILA: OIKEA IPFS")
        else:
            print("🧪 IPFS-TILA: MOCK-IPFS")
        print("🗳️  Vaalit: Testivaalit 2025")
        print("📝 Sivut:")
        print("   - http://localhost:5000 (Etusivu)")
        print("   - http://localhost:5000/vaalikone (Vaalikone)")
        print("   - http://localhost:5000/kysymysten-hallinta (Kysymysten hallinta)")
        print("   - http://localhost:5000/puolueet (Puoluevertailu)")
        print("   - http://localhost:5000/admin (Ylläpito)")
        print("🔧 API-reitit:")
        print("   - /api/meta - Järjestelmän meta-tiedot")
        print("   - /api/questions - Kaikki kysymykset")
        print("   - /api/candidates - Kaikki ehdokkaat")
        print("   - /api/admin/* - Admin-toiminnot")
    app.run(debug=DEBUG, host='0.0.0.0', port=5000)
