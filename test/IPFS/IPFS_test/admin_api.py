from flask import request, jsonify
from utils import handle_api_errors
import json

def init_admin_api(app, data_manager, handlers):
    """Alustaa admin API-reitit"""
    
    @app.route('/api/admin/questions')
    @handle_api_errors
    def admin_get_questions():
        """Hakee kaikki kysymykset (mukaan lukien blokatut)"""
        questions = data_manager.get_questions(include_blocked=True)
        for q in questions:
            q['id'] = str(q['id'])
        return jsonify(questions)
    
    @app.route('/api/admin/block_question', methods=['POST'])
    @handle_api_errors
    def admin_block_question():
        """Merkitsee kysymyksen blokatuksi"""
        data = request.json
        question_id = data.get('question_id')
        reason = data.get('reason', 'Asiattomat sisältö')
        
        if not question_id:
            return jsonify({
                'success': False,
                'error': 'Kysymyksen ID on pakollinen'
            }), 400
        
        # Yritä muuntaa ID numeroksi
        try:
            question_id = int(question_id)
        except ValueError:
            pass
        
        success = data_manager.block_question(question_id, reason)
        if success:
            return jsonify({
                'success': True,
                'message': f'Kysymys {question_id} merkitty blokatuksi'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Kysymystä ei löytynyt'
            }), 404
    
    @app.route('/api/admin/unblock_question', methods=['POST'])
    @handle_api_errors
    def admin_unblock_question():
        """Poistaa kysymyksen blokkaus"""
        data = request.json
        question_id = data.get('question_id')
        
        if not question_id:
            return jsonify({
                'success': False,
                'error': 'Kysymyksen ID on pakollinen'
            }), 400
        
        # Etsi ja päivitä kysymys
        official = data_manager.read_json('questions.json') or {}
        user = data_manager.read_json('newquestions.json') or {}
        
        found = False
        for q in official.get('questions', []):
            if q.get('id') == question_id:
                q.setdefault('metadata', {})['blocked'] = False
                q['metadata']['blocked_reason'] = None
                data_manager.write_json('questions.json', official, f"Kysymys {question_id} vapautettu")
                found = True
                break
        
        if not found:
            for q in user.get('questions', []):
                if q.get('id') == question_id:
                    q.setdefault('metadata', {})['blocked'] = False
                    q['metadata']['blocked_reason'] = None
                    data_manager.write_json('newquestions.json', user, f"Kysymys {question_id} vapautettu")
                    found = True
                    break
        
        if found:
            data_manager.get_meta()  # Päivitä tilastot
            return jsonify({
                'success': True,
                'message': f'Kysymys {question_id} vapautettu'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Kysymystä ei löytynyt'
            }), 404
    
    @app.route('/api/admin/ipfs_sync_queue')
    @handle_api_errors
    def admin_get_ipfs_queue():
        """Hakee IPFS-synkronointijonon"""
        queue = data_manager.read_json('ipfs_sync_queue.json') or {
            'pending_questions': [],
            'last_sync': None,
            'sync_interval_minutes': 10,
            'max_questions_per_sync': 20
        }
        return jsonify(queue)
    
    @app.route('/api/admin/process_ipfs_sync', methods=['POST'])
    @handle_api_errors
    def admin_process_ipfs_sync():
        """Käsittelee IPFS-synkronoinnin manuaalisesti"""
        success = data_manager.process_ipfs_sync()
        if success:
            return jsonify({
                'success': True,
                'message': 'IPFS-synkronointi suoritettu'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'IPFS-synkronointia ei tarvittu tai se epäonnistui'
            })
    
    @app.route('/api/admin/elo_update', methods=['POST'])
    @handle_api_errors
    def admin_elo_update():
        """Päivittää kysymyksen Elo-arvoa manuaalisesti"""
        data = request.json
        question_id = data.get('question_id')
        delta = data.get('delta', 0)
        user_id = data.get('user_id', 'admin')
        
        if not question_id:
            return jsonify({
                'success': False,
                'error': 'Kysymyksen ID on pakollinen'
            }), 400
        
        try:
            question_id = int(question_id)
        except ValueError:
            pass
        
        success = handlers.apply_elo_update(question_id, delta, user_id)
        if success:
            return jsonify({
                'success': True,
                'message': f'Elo-arvo päivitetty kysymykselle {question_id}'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Kysymystä ei löytynyt'
            }), 404
    
    @app.route('/api/admin/system_stats')
    @handle_api_errors
    def admin_system_stats():
        """Palauttaa järjestelmän tilastot"""
        stats = handlers.get_system_stats()
        return jsonify(stats)
    
    @app.route('/api/admin/fetch_ipfs_questions', methods=['POST'])
    @handle_api_errors
    def admin_fetch_ipfs_questions():
        """Hakee kysymykset IPFS:stä manuaalisesti"""
        success = handlers.fetch_ipfs_questions()
        if success:
            return jsonify({
                'success': True,
                'message': 'IPFS-kysymykset haettu onnistuneesti'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'IPFS-kysymysten haku epäonnistui'
            })
    
    @app.route('/api/admin/questions/elo_ranking')
    @handle_api_errors
    def admin_elo_ranking():
        """Palauttaa kysymykset Elo-arvon mukaan järjestettynä"""
        questions = data_manager.get_questions(include_blocked=True)
        # Lisää nykyinen Elo-arvo jokaiselle kysymykselle
        for q in questions:
            elo_info = q.get('elo', {})
            if isinstance(elo_info, dict):
                current_rating = elo_info.get('current_rating')
                if current_rating is None:
                    base = elo_info.get('base_rating', 1200)
                    deltas = elo_info.get('deltas', [])
                    current_rating = base + sum(d.get('delta', 0) for d in deltas)
                    q['elo']['current_rating'] = current_rating
            else:
                q['elo'] = {'current_rating': 1200}
        
        # Järjestä Elo-arvon mukaan
        questions.sort(key=lambda x: x.get('elo', {}).get('current_rating', 1200), reverse=True)
        
        for q in questions:
            q['id'] = str(q['id'])
        
        return jsonify(questions)
    
    @app.route('/api/admin/questions/select_for_sync')
    @handle_api_errors
    def admin_select_for_sync():
        """Valitsee kysymykset IPFS-synkronointiin eri strategioilla"""
        strategy = request.args.get('strategy', 'balanced')
        limit = int(request.args.get('limit', 20))
        
        questions = handlers.select_questions_for_display(strategy=strategy, limit=limit)
        
        for q in questions:
            q['id'] = str(q['id'])
        
        return jsonify({
            'success': True,
            'strategy': strategy,
            'limit': limit,
            'questions': questions,
            'count': len(questions)
        })
