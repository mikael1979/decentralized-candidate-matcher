from flask import Flask, render_template, request, jsonify
from data_manager import DataManager
from route_handlers import RouteHandlers

# DEBUG-tila
DEBUG = True

# Alusta komponentit
data_manager = DataManager(debug=DEBUG)
handlers = RouteHandlers(data_manager, debug=DEBUG)

# Alusta data
data_manager.initialize_data_files()

# Flask-sovellus
app = Flask(__name__, static_folder='static', template_folder='templates')

# Staattiset reitit
@app.route('/')
def index(): 
    # Lähetä meta-tiedot templatelle
    meta = data_manager.get_meta()
    return render_template('index.html', 
                         system_name=meta.get('system', 'Vaalikone'),
                         version=meta.get('version', '0.0.1'),
                         election_name=meta.get('election', {}).get('name', {}).get('fi', 'Testivaalit'),
                         election_date=meta.get('election', {}).get('date', '2025-04-13'))

@app.route('/vaalikone')
def vaalikone(): 
    meta = data_manager.get_meta()
    return render_template('vaalikone.html', 
                         election_name=meta.get('election', {}).get('name', {}).get('fi', 'Testivaalit'))

@app.route('/kysymysten-hallinta') 
def question_management(): 
    meta = data_manager.get_meta()
    return render_template('question_management.html',
                         election_name=meta.get('election', {}).get('name', {}).get('fi', 'Testivaalit'))

@app.route('/puolueet')
def parties(): 
    meta = data_manager.get_meta()
    return render_template('parties.html',
                         election_name=meta.get('election', {}).get('name', {}).get('fi', 'Testivaalit'))

@app.route('/admin')
def admin(): 
    meta = data_manager.get_meta()
    return render_template('admin.html', 
                         system_name=meta.get('system', 'Vaalikone'),
                         version=meta.get('version', '0.0.1'),
                         election_name=meta.get('election', {}).get('name', {}).get('fi', 'Testivaalit'))

# API-reitit
@app.route('/api/meta')
def api_meta():
    """Palauttaa järjestelmän meta-tiedot"""
    return jsonify(data_manager.get_meta())

@app.route('/api/system_info')
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
def api_update_meta():
    """Päivittää meta-tiedot (admin-only)"""
    try:
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
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Virhe: {str(e)}'
        }), 500

@app.route('/api/questions')
def api_questions():
    """Palauttaa kaikki kysymykset"""
    try:
        questions = data_manager.get_questions()
        # Muunna ID:t stringeiksi frontendia varten
        for q in questions:
            q['id'] = str(q['id'])
        return jsonify(questions)
    except Exception as e:
        return jsonify({'error': f'Kysymysten haku epäonnistui: {str(e)}'}), 500

@app.route('/api/candidates')
def api_candidates():
    """Palauttaa kaikki ehdokkaat"""
    try:
        candidates = data_manager.get_candidates()
        return jsonify(candidates)
    except Exception as e:
        return jsonify({'error': f'Ehdokkaiden haku epäonnistui: {str(e)}'}), 500

@app.route('/api/parties')
def api_parties():
    """Palauttaa kaikki puolueet"""
    try:
        parties = handlers.get_parties()
        return jsonify(parties)
    except Exception as e:
        return jsonify({'error': f'Puolueiden haku epäonnistui: {str(e)}'}), 500

@app.route('/api/party/<party_name>')
def api_party_profile(party_name):
    """Palauttaa puolueen profiilin"""
    try:
        profile, consensus = handlers.get_party_profile(party_name)
        return jsonify({'profile': profile, 'consensus': consensus})
    except Exception as e:
        return jsonify({'error': f'Puolueprofiilin haku epäonnistui: {str(e)}'}), 500

@app.route('/api/add_candidate', methods=['POST'])
def api_add_candidate():
    """Lisää uuden ehdokkaan"""
    try:
        candidate_data = request.json
        
        # Tarkista pakolliset kentät
        if not candidate_data.get('name'):
            return jsonify({
                'success': False,
                'error': 'Ehdokkaan nimi on pakollinen'
            }), 400
        
        if not candidate_data.get('party'):
            return jsonify({
                'success': False,
                'error': 'Puolue on pakollinen'
            }), 400
        
        # Tallenna ehdokas
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
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Ehdokkaan lisäys epäonnistui: {str(e)}'
        }), 500

@app.route('/api/submit_question', methods=['POST'])
def api_submit_question():
    """Lähettää uuden kysymyksen"""
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
        
        # Lisää puuttuvat kentät
        question_data.setdefault('scale', {
            'min': -5,
            'max': 5,
            'labels': {
                'fi': {'-5': 'Täysin eri mieltä', '0': 'Neutraali', '5': 'Täysin samaa mieltä'}
            }
        })
        
        # Lähetä kysymys
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
            
    except Exception as e:
        return jsonify({
            'success': False,
            'errors': [f'Lähetys epäonnistui: {str(e)}']
        }), 500

@app.route('/api/search_questions')
def api_search_questions():
    """Hakee kysymyksiä hakusanalla"""
    try:
        query = request.args.get('q', '')
        results = handlers.search_questions(query)
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Haku epäonnistui: {str(e)}'
        }), 500

@app.route('/api/available_tags')
def api_available_tags():
    """Palauttaa saatavilla olevat tagit"""
    try:
        questions = data_manager.get_questions()
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
            'error': f'Tagien haku epäonnistui: {str(e)}'
        }), 500

@app.route('/api/status')
def api_status():
    """Palauttaa järjestelmän tilan"""
    try:
        meta = data_manager.get_meta()
        return jsonify({
            'success': True,
            'system_status': 'running',
            'meta': meta
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Tilan haku epäonnistui: {str(e)}'
        }), 500

@app.route('/api/compare_parties', methods=['POST'])
def api_compare_parties():
    """Vertaa käyttäjän vastauksia puolueeseen"""
    try:
        data = request.json
        user_answers = data.get('user_answers', {})
        party_name = data.get('party_name')
        
        # Yksinkertainen vertailu
        party_candidates = [c for c in data_manager.get_candidates() if c.get('party') == party_name]
        
        if not party_candidates:
            return jsonify({
                'success': False,
                'error': 'Puoluetta ei löytynyt'
            }), 404
        
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
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Vertailu epäonnistui: {str(e)}'
        }), 500

@app.route('/api/compare_all_parties', methods=['POST'])
def api_compare_all_parties():
    """Vertaa käyttäjän vastauksia kaikkiin puolueisiin"""
    try:
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
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Vertailu epäonnistui: {str(e)}'
        }), 500

# Admin API-reitit
@app.route('/api/admin/status')
def admin_status():
    """Palauttaa admin-paneelin tilan"""
    return jsonify({
        'is_running': True,
        'active_users': 0,  # Mock data
        'last_backup': datetime.now().isoformat(),
        'version': '0.0.1'
    })

@app.route('/api/admin/moderation_queue')
def moderation_queue():
    """Palauttaa moderointijonon"""
    # Mock data - oikeassa sovelluksessa haettaisiin tietokannasta
    return jsonify([])

@app.route('/api/admin/ipfs_status')
def ipfs_status():
    """Palauttaa IPFS-tilan"""
    return jsonify({
        'connected': False,  # Mock data
        'peer_count': 0,
        'storage_used': '0 MB',
        'storage_max': '1 GB'
    })

@app.route('/api/admin/stats')
def admin_stats():
    """Palauttaa admin-tilastot"""
    meta = data_manager.get_meta()
    stats = meta.get('content', {})
    
    return jsonify({
        'total_users': 0,  # Mock data
        'total_questions': stats.get('questions_count', 0),
        'total_candidates': stats.get('candidates_count', 0),
        'total_parties': stats.get('parties_count', 0)
    })

@app.route('/api/admin/export_data')
def export_data():
    """Vie kaiken datan"""
    try:
        data = {
            'questions': data_manager.get_questions(),
            'candidates': data_manager.get_candidates(),
            'meta': data_manager.get_meta(),
            'exported_at': datetime.now().isoformat()
        }
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': f'Vienti epäonnistui: {str(e)}'}), 500

@app.route('/api/admin/import_data', methods=['POST'])
def import_data():
    """Tuodaan data"""
    # Mock toteutus
    return jsonify({'success': True, 'message': 'Data tuotu onnistuneesti'})

@app.route('/api/admin/clear_cache', methods=['POST'])
def clear_cache():
    """Tyhjentää välimuistin"""
    # Mock toteutus
    return jsonify({'success': True, 'message': 'Välimuisti tyhjennetty'})

@app.route('/api/admin/approve_question/<int:question_id>', methods=['POST'])
def approve_question(question_id):
    """Hyväksyy kysymyksen"""
    # Mock toteutus
    return jsonify({'success': True, 'message': 'Kysymys hyväksytty'})

@app.route('/api/admin/reject_question/<int:question_id>', methods=['POST'])
def reject_question(question_id):
    """Hylkää kysymyksen"""
    # Mock toteutus
    return jsonify({'success': True, 'message': 'Kysymys hylätty'})

# IPFS Synkronointi API-reitit
@app.route('/api/admin/sync', methods=['POST'])
def manual_sync():
    """Käynnistää manuaalisen synkronoinnin"""
    # Mock toteutus
    return jsonify({
        'success': True,
        'message': 'Synkronointi käynnistetty',
        'status': 'completed'
    })

@app.route('/api/admin/sync_status')
def get_sync_status():
    """Hakee synkronoinnin tilan"""
    return jsonify({
        'status': 'completed',
        'last_sync': datetime.now().isoformat(),
        'peers_found': 0,
        'data_imported': 0
    })

@app.route('/api/admin/peers')
def get_peers():
    """Hakee löydetyt peerit"""
    return jsonify([])

@app.route('/api/admin/enable_auto_sync', methods=['POST'])
def enable_auto_sync():
    """Ota automaattinen synkronointi käyttöön"""
    return jsonify({'success': True, 'message': 'Automaattinen synkronointi käytössä'})

@app.route('/api/admin/disable_auto_sync', methods=['POST'])
def disable_auto_sync():
    """Poista automaattinen synkronointi käytöstä"""
    return jsonify({'success': True, 'message': 'Automaattinen synkronointi pois käytöstä'})

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
        print("🗳️  Vaalit: Testivaalit 2025")
        print("📝 Sivut:")
        print("   - http://localhost:5000 (Etusivu)")
        print("   - http://localhost:5000/vaalikone (Vaalikone)")
        print("   - http://localhost:5000/kysymysten-hallinta (Kysymysten hallinta)")
        print("   - http://localhost:5000/puolueet (Puoluevertailu)")
        print("   - http://localhost:5000/admin (Ylläpito)")
        print("🔧 API-reitit:")
        print("   - /api/meta - Järjestelmän meta-tiedot")
        print("   - /api/update_meta - Meta-tietojen päivitys")
        print("   - /api/system_info - Järjestelmätiedot")
    
    app.run(debug=DEBUG, host='0.0.0.0', port=5000)
