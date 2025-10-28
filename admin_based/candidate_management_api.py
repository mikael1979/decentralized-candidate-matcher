# candidate_management_api.py

from flask import request, jsonify
from utils import handle_api_errors
from datetime import datetime

def init_candidate_management_api(app, data_manager, admin_login_required):
    """
    Alustaa ehdokashallinnan API:n:
    - Ehdokkaan oman profiilin hallinta (vastaukset, perustelut)
    - Vaatii kirjautumisen (aluksi admin-pohjainen, myöhemmin ehdokaskohtainen auth)
    """

    @app.route('/api/candidate/<candidate_id>/profile', methods=['GET'])
    @admin_login_required
    @handle_api_errors
    def get_candidate_profile(candidate_id):
        """Hakee ehdokkaan profiilin"""
        all_candidates = data_manager.get_candidates()
        candidate = next((c for c in all_candidates if str(c.get('id')) == str(candidate_id)), None)
        if not candidate:
            return jsonify({
                'success': False,
                'error': 'Ehdokasta ei löytynyt'
            }), 404
        return jsonify({
            'success': True,
            'candidate': candidate
        })

    @app.route('/api/candidate/<candidate_id>/answers', methods=['PUT'])
    @admin_login_required
    @handle_api_errors
    def update_candidate_answers(candidate_id):
        """Päivittää ehdokkaan vastauksia ja perusteluja"""
        update_data = request.json
        if not isinstance(update_data, dict):
            return jsonify({'success': False, 'error': 'Virheellinen pyynnön rakenne'}), 400

        # Hae kaikki ehdokkaat
        all_candidates = data_manager.get_candidates()
        target_candidate = None
        for c in all_candidates:
            if str(c.get('id')) == str(candidate_id):
                target_candidate = c
                break

        if not target_candidate:
            return jsonify({
                'success': False,
                'error': 'Ehdokasta ei löytynyt'
            }), 404

        # Päivitä vastaukset
        new_answers = update_data.get('answers')
        if not isinstance(new_answers, list):
            return jsonify({'success': False, 'error': 'Answers tulee olla lista'}), 400

        validated_answers = []
        for ans in new_answers:
            if not isinstance(ans, dict):
                return jsonify({'success': False, 'error': 'Jokaisen vastauksen tulee olla objekti'}), 400
            if 'question_id' not in ans or 'answer' not in ans:
                return jsonify({'success': False, 'error': 'Jokaisessa vastauksessa tulee olla question_id ja answer'}), 400
            if not (-5 <= ans['answer'] <= 5):
                return jsonify({'success': False, 'error': 'Vastaus tulee olla välillä -5–5'}), 400
            ans.setdefault('confidence', 1.0)
            if not (0.0 <= ans['confidence'] <= 1.0):
                return jsonify({'success': False, 'error': 'Confidence tulee olla välillä 0.0–1.0'}), 400
            # Päivitä perustelut
            ans.setdefault('justification', {'fi': '', 'en': '', 'sv': ''})
            ans.setdefault('justification_metadata', {
                'created_at': datetime.now().isoformat(),
                'version': 1,
                'blocked': False,
                'signature': None
            })
            validated_answers.append(ans)

        target_candidate['answers'] = validated_answers

        # Tallenna päivitetty lista
        data = {'candidates': all_candidates}
        success = data_manager.write_json('candidates.json', data, f"Ehdokas {candidate_id} päivitti vastauksia")
        if success:
            return jsonify({
                'success': True,
                'message': f'Ehdokkaan {candidate_id} vastaukset päivitetty onnistuneesti'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Tallennus epäonnistui'
            }), 500

    @app.route('/api/candidate/<candidate_id>/profile', methods=['PUT'])
    @admin_login_required
    @handle_api_errors
    def update_candidate_profile(candidate_id):
        """Päivittää ehdokkaan perustietoja (nimi, piirikunta)"""
        update_data = request.json
        if not isinstance(update_data, dict):
            return jsonify({'success': False, 'error': 'Virheellinen pyynnön rakenne'}), 400

        # Hae kaikki ehdokkaat
        all_candidates = data_manager.get_candidates()
        target_candidate = None
        for c in all_candidates:
            if str(c.get('id')) == str(candidate_id):
                target_candidate = c
                break

        if not target_candidate:
            return jsonify({
                'success': False,
                'error': 'Ehdokasta ei löytynyt'
            }), 404

        # Päivitä sallitut kentät
        allowed_fields = ['name', 'district']
        for field in allowed_fields:
            if field in update_data:
                if isinstance(update_data[field], str) and update_data[field].strip():
                    target_candidate[field] = update_data[field].strip()

        # Tallenna päivitetty lista
        data = {'candidates': all_candidates}
        success = data_manager.write_json('candidates.json', data, f"Ehdokas {candidate_id} päivitti profiilia")
        if success:
            return jsonify({
                'success': True,
                'message': f'Ehdokkaan {candidate_id} profiili päivitetty onnistuneesti'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Tallennus epäonnistui'
            }), 500
