# party_management_api.py

from flask import request, jsonify
from utils import handle_api_errors
from datetime import datetime

def init_party_management_api(app, data_manager, admin_login_required):
    """
    Alustaa puoluehallinnan API:n:
    - Ehdokkaiden hallinta puoluekohtaisesti
    - Vaatii admin-kirjautumisen (yksinkertaistettu)
    """

    @app.route('/api/party/<party_name>/candidates', methods=['GET'])
    @admin_login_required
    @handle_api_errors
    def get_party_candidates(party_name):
        """Hakee kaikki ehdokkaat tietylle puolueelle"""
        all_candidates = data_manager.get_candidates()
        party_candidates = [c for c in all_candidates if c.get('party') == party_name]
        return jsonify({
            'success': True,
            'party_name': party_name,
            'candidates': party_candidates,
            'count': len(party_candidates)
        })

    @app.route('/api/party/<party_name>/candidates', methods=['POST'])
    @admin_login_required
    @handle_api_errors
    def add_party_candidate(party_name):
        """Lisää uuden ehdokkaan puolueelle"""
        candidate_data = request.json
        if not isinstance(candidate_data, dict):
            return jsonify({'success': False, 'error': 'Virheellinen pyynnön rakenne'}), 400

        # Pakolliset kentät
        required_fields = ['name', 'district']
        for field in required_fields:
            if not candidate_data.get(field):
                return jsonify({'success': False, 'error': f'Kenttä "{field}" on pakollinen'}), 400

        # Varmista, että ehdokas kuuluu oikeaan puolueeseen
        candidate_data['party'] = party_name

        # Varmista, että answers on oikeassa muodossa
        answers = candidate_data.get('answers', [])
        if not isinstance(answers, list):
            return jsonify({'success': False, 'error': 'Answers tulee olla lista'}), 400

        for ans in answers:
            if not isinstance(ans, dict):
                return jsonify({'success': False, 'error': 'Jokaisen vastauksen tulee olla objekti'}), 400
            if 'question_id' not in ans or 'answer' not in ans:
                return jsonify({'success': False, 'error': 'Jokaisessa vastauksessa tulee olla question_id ja answer'}), 400
            if not (-5 <= ans['answer'] <= 5):
                return jsonify({'success': False, 'error': 'Vastaus tulee olla välillä -5–5'}), 400
            ans.setdefault('confidence', 1.0)
            if not (0.0 <= ans['confidence'] <= 1.0):
                return jsonify({'success': False, 'error': 'Confidence tulee olla välillä 0.0–1.0'}), 400
            # Lisää perustelut, jos puuttuu
            ans.setdefault('justification', {'fi': '', 'en': '', 'sv': ''})
            ans.setdefault('justification_metadata', {
                'created_at': datetime.now().isoformat(),
                'version': 1,
                'blocked': False,
                'signature': None
            })

        # Lisää ehdokas
        candidate_id = data_manager.add_candidate(candidate_data)
        if candidate_id:
            return jsonify({
                'success': True,
                'candidate_id': candidate_id,
                'message': f'Ehdokas lisätty puolueelle {party_name}'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Ehdokkaan lisäys epäonnistui'
            }), 500

    @app.route('/api/party/<party_name>/candidate/<candidate_id>', methods=['PUT'])
    @admin_login_required
    @handle_api_errors
    def update_party_candidate(party_name, candidate_id):
        """Päivittää olemassa olevan ehdokkaan tietoja"""
        update_data = request.json
        if not isinstance(update_data, dict):
            return jsonify({'success': False, 'error': 'Virheellinen pyynnön rakenne'}), 400

        # Hae kaikki ehdokkaat
        all_candidates = data_manager.get_candidates()
        target_candidate = None
        for c in all_candidates:
            if str(c.get('id')) == str(candidate_id) and c.get('party') == party_name:
                target_candidate = c
                break

        if not target_candidate:
            return jsonify({
                'success': False,
                'error': 'Ehdokasta ei löytynyt tai se ei kuulu puolueellesi'
            }), 404

        # Päivitä sallitut kentät
        allowed_fields = ['name', 'district', 'answers']
        for field in allowed_fields:
            if field in update_data:
                if field == 'answers':
                    # Validointi kuten lisäyksessä
                    answers = update_data['answers']
                    if not isinstance(answers, list):
                        return jsonify({'success': False, 'error': 'Answers tulee olla lista'}), 400
                    for ans in answers:
                        if 'question_id' not in ans or 'answer' not in ans:
                            return jsonify({'success': False, 'error': 'Vastauksessa puuttuu question_id tai answer'}), 400
                        if not (-5 <= ans['answer'] <= 5):
                            return jsonify({'success': False, 'error': 'Vastaus tulee olla välillä -5–5'}), 400
                        ans.setdefault('confidence', 1.0)
                        ans.setdefault('justification', {'fi': '', 'en': '', 'sv': ''})
                        ans.setdefault('justification_metadata', {
                            'created_at': datetime.now().isoformat(),
                            'version': 1,
                            'blocked': False,
                            'signature': None
                        })
                target_candidate[field] = update_data[field]

        # Tallenna päivitetty lista
        data = {'candidates': all_candidates}
        success = data_manager.write_json('candidates.json', data, f"Ehdokas {candidate_id} päivitetty")
        if success:
            return jsonify({
                'success': True,
                'message': f'Ehdokas {candidate_id} päivitetty onnistuneesti'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Tallennus epäonnistui'
            }), 500

    @app.route('/api/party/<party_name>/candidate/<candidate_id>', methods=['DELETE'])
    @admin_login_required
    @handle_api_errors
    def delete_party_candidate(party_name, candidate_id):
        """Poistaa ehdokkaan (soft delete – merkitsee deleted:ksi)"""
        all_candidates = data_manager.get_candidates()
        target_candidate = None
        for c in all_candidates:
            if str(c.get('id')) == str(candidate_id) and c.get('party') == party_name:
                target_candidate = c
                break

        if not target_candidate:
            return jsonify({
                'success': False,
                'error': 'Ehdokasta ei löytynyt tai se ei kuulu puolueellesi'
            }), 404

        # Soft delete: merkitse poistetuksi
        target_candidate['deleted'] = True
        target_candidate['deleted_at'] = datetime.now().isoformat()

        data = {'candidates': all_candidates}
        success = data_manager.write_json('candidates.json', data, f"Ehdokas {candidate_id} poistettu")
        if success:
            return jsonify({
                'success': True,
                'message': f'Ehdokas {candidate_id} poistettu'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Poisto epäonnistui'
            }), 500
