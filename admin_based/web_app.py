# web_app.py - KORVAA KOKO TIEDOSTO TÄLLÄ:

import signal
import sys
import os
from flask import Flask, render_template, request, jsonify, session
import json
import hashlib
from datetime import datetime

# Graceful shutdown handler
def signal_handler(sig, frame):
    print('\n\n🔴 Säästävästi sammutetaan Vaalikone...')
    if hasattr(app, 'ipfs_client'):
        print('🔌 Suljetaan IPFS-yhteys...')
    print('💾 Tallennetaan tila...')
    print('👋 Näkemiin!')
    sys.exit(0)

# Rekisteröi signal handlerit
signal.signal(signal.SIGINT, signal_handler)  # Ctrl-C
signal.signal(signal.SIGTERM, signal_handler) # Kubernetes/container shutdown

# DEBUG-tila
DEBUG = True
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

# Alusta DataManager
from data_manager import DataManager
data_manager = DataManager(debug=DEBUG)
data_manager.set_ipfs_client(ipfs_client)

# Varmista että perushakemistot on olemassa
data_manager.ensure_directories()

# Alusta RouteHandlers
from route_handlers import RouteHandlers
handlers = RouteHandlers(data_manager, debug=DEBUG)

# Flask-sovellus
app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'vaalikone-secret-key-2025'

def admin_login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_authenticated'):
            return jsonify({
                'success': False,
                'error': 'Admin-kirjautuminen vaaditaan',
                'login_required': True
            }), 401
        return f(*args, **kwargs)
    return decorated_function

def verify_admin_password(password):
    try:
        with open('keys/system_info.json', 'r') as f:
            system_info = json.load(f)
        stored_hash = system_info.get('password_hash')
        salt = system_info.get('password_salt')
        if not stored_hash or not salt:
            return False
        computed_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
        return computed_hash == stored_hash
    except Exception as e:
        print(f"❌ Salasanan tarkistusvirhe: {e}")
        return False

# === ADMIN-KIRJAUTUMISREITIT ===
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    password = data.get('password')
    if not password:
        return jsonify({'success': False, 'error': 'Salasana vaaditaan'}), 400
    if verify_admin_password(password):
        session['admin_authenticated'] = True
        session['admin_login_time'] = datetime.now().isoformat()
        return jsonify({'success': True, 'message': 'Kirjautuminen onnistui'})
    else:
        return jsonify({'success': False, 'error': 'Väärä salasana'}), 401

@app.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    session.pop('admin_authenticated', None)
    session.pop('admin_login_time', None)
    return jsonify({'success': True, 'message': 'Uloskirjautuminen onnistui'})

@app.route('/api/admin/status')
def admin_status():
    return jsonify({
        'authenticated': session.get('admin_authenticated', False),
        'login_time': session.get('admin_login_time')
    })

# === INTEGROI ADMIN-MODUULIT ===
from admin_api import init_admin_api
from admin_settings_api import init_admin_settings_api
from party_management_api import init_party_management_api
from candidate_management_api import init_candidate_management_api

init_admin_api(app, data_manager, handlers, admin_login_required)
init_admin_settings_api(app, data_manager, admin_login_required)
init_party_management_api(app, data_manager, admin_login_required)
init_candidate_management_api(app, data_manager, admin_login_required)

# === APUFUNKTIO META-TIEDOILLA ===
def _render_template(template, **extra_context):
    meta = data_manager.get_meta()
    base_context = {
        'system_name': meta.get('system', 'Vaalikone'),
        'version': meta.get('version', '0.0.1'),
        'election_name': meta.get('election', {}).get('name', {}).get('fi', 'Nimetön vaalit'),
        'election_date': meta.get('election', {}).get('date', '2025-01-01')
    }
    base_context.update(extra_context)
    return render_template(template, **base_context)

# === SIVUREITIT ===
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

# === API-REITIT ===
@app.route('/api/meta')
def api_meta():
    return jsonify(data_manager.get_meta())

@app.route('/api/system_info')
def api_system_info():
    meta = data_manager.get_meta()
    return jsonify({
        'system_name': meta.get('system', 'Vaalikone'),
        'version': meta.get('version', '0.0.1'),
        'election': meta.get('election', {}),
        'stats': meta.get('content', {}),
        'community_moderation': meta.get('community_moderation', {})
    })

@app.route('/api/update_meta', methods=['POST'])
@admin_login_required
def api_update_meta():
    new_meta = request.json
    success = data_manager.update_meta(new_meta)
    if success:
        return jsonify({'success': True, 'message': 'Meta-tiedot päivitetty'})
    else:
        return jsonify({'success': False, 'error': 'Päivitys epäonnistui'}), 500

@app.route('/api/questions')
def api_questions():
    questions = data_manager.get_questions()
    for q in questions:
        q['id'] = str(q['id'])
    return jsonify(questions)

@app.route('/api/active_questions')
def api_active_questions():
    """Palauttaa korkeimman Elo-arvon kysymykset kevyesti frontendille"""
    active = data_manager.ensure_data_file('active_questions.json')
    return jsonify(active)

@app.route('/api/candidates')
def api_candidates():
    return jsonify(data_manager.get_candidates())

@app.route('/api/parties')
def api_parties():
    return jsonify(handlers.get_parties())

@app.route('/api/party/<party_name>')
def api_party_profile(party_name):
    profile, consensus = handlers.get_party_profile(party_name)
    return jsonify({'profile': profile, 'consensus': consensus})

@app.route('/api/add_candidate', methods=['POST'])
@admin_login_required
def api_add_candidate():
    candidate_data = request.json
    if not candidate_data.get('name') or not candidate_data.get('party'):
        return jsonify({'success': False, 'error': 'Nimi ja puolue pakollisia'}), 400
    candidate_id = data_manager.add_candidate(candidate_data)
    if candidate_id:
        return jsonify({'success': True, 'candidate_id': candidate_id})
    else:
        return jsonify({'success': False, 'error': 'Ehdokkaan lisäys epäonnistui'}), 500

@app.route('/api/submit_question', methods=['POST'])
def api_submit_question():
    question_data = request.json
    if not question_data.get('question', {}).get('fi'):
        return jsonify({'success': False, 'errors': ['Kysymys suomeksi pakollinen']}), 400
    question_data.setdefault('scale', {'min': -5, 'max': 5})
    cid = data_manager.add_question(question_data)
    if cid:
        return jsonify({'success': True, 'cid': cid})
    else:
        return jsonify({'success': False, 'errors': ['Tallennus epäonnistui']}), 500

@app.route('/api/search_questions')
def api_search_questions():
    query = request.args.get('q', '')
    results = handlers.search_questions(query)
    return jsonify({'success': True, 'results': results})

@app.route('/api/available_tags')
def api_available_tags():
    questions = data_manager.get_questions()
    tag_counts = {}
    for q in questions:
        for tag in q.get('tags', []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    return jsonify({'success': True, 'tags': tag_counts})

@app.route('/api/compare_parties', methods=['POST'])
def api_compare_parties():
    data = request.json
    user_answers = data.get('user_answers', {})
    party_name = data.get('party_name')
    party_candidates = [c for c in data_manager.get_candidates() if c.get('party') == party_name]
    if not party_candidates:
        return jsonify({'success': False, 'error': 'Puoluetta ei löytynyt'}), 404
    total_match = sum(handlers.calculate_match(user_answers, c) for c in party_candidates)
    avg_match = total_match / len(party_candidates)
    return jsonify({
        'success': True,
        'match_percentage': avg_match * 100,
        'candidate_count': len(party_candidates),
        'matched_questions': len(user_answers)
    })

@app.route('/api/compare_all_parties', methods=['POST'])
def api_compare_all_parties():
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

# === VIRHEENKÄSITTELY ===
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Sivua ei löytynyt'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Sisäinen palvelinvirhe'}), 500

# === KÄYNNISTYS ===
if __name__ == '__main__':
    print("💡 Vinkki: Käytä Ctrl-C sulkeaksesi sovelluksen säästävästi")
    
    # Joukkotuonti ennen käynnistystä
    if '--bulk-import-candidates' in sys.argv:
        idx = sys.argv.index('--bulk-import-candidates')
        if idx + 1 < len(sys.argv):
            filepath = sys.argv[idx + 1]
            if os.path.exists(filepath):
                print(f"📤 Tuodaan ehdokkaita tiedostosta: {filepath}")
                with open(filepath, 'r', encoding='utf-8') as f:
                    batch = json.load(f)
                for candidate in batch.get('candidates', []):
                    candidate_id = data_manager.add_candidate(candidate)
                    if candidate_id:
                        print(f"✅ Lisätty ehdokas: {candidate['name']} (ID: {candidate_id})")
                    else:
                        print(f"❌ Ehdokkaan lisäys epäonnistui: {candidate.get('name', 'Nimetön')}")

    app.run(debug=DEBUG, host='0.0.0.0', port=5000)
