"""
Admin API -reitit erilliseen moduuliin
"""
from flask import Blueprint, jsonify, request
from data_manager import DataManager
from route_handlers import RouteHandlers
from utils import handle_api_errors

# Luo Blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Alusta komponentit (nämä injektoidaan myöhemmin)
data_manager = None
handlers = None

def init_admin_api(app, dm, rh):
    """Alustaa admin API:n"""
    global data_manager, handlers
    data_manager = dm
    handlers = rh
    app.register_blueprint(admin_bp)


@admin_bp.route('/status')
@handle_api_errors
def admin_status():
    """Palauttaa admin-paneelin tilan"""
    return jsonify({
        'is_running': True,
        'active_users': 0,
        'last_backup': data_manager.get_meta().get('content', {}).get('last_updated', ''),
        'version': '0.0.1'
    })


@admin_bp.route('/moderation_queue')
@handle_api_errors
def moderation_queue():
    """Palauttaa moderointijonon"""
    # Mock data
    return jsonify([])


@admin_bp.route('/ipfs_status')
@handle_api_errors
def ipfs_status():
    """Palauttaa IPFS-tilan"""
    return jsonify({
        'connected': False,
        'peer_count': 0,
        'storage_used': '0 MB',
        'storage_max': '1 GB'
    })


@admin_bp.route('/stats')
@handle_api_errors
def admin_stats():
    """Palauttaa admin-tilastot"""
    meta = data_manager.get_meta()
    stats = meta.get('content', {})
    
    return jsonify({
        'total_users': 0,
        'total_questions': stats.get('questions_count', 0),
        'total_candidates': stats.get('candidates_count', 0),
        'total_parties': stats.get('parties_count', 0)
    })


@admin_bp.route('/export_data')
@handle_api_errors
def export_data():
    """Vie kaiken datan"""
    data = {
        'questions': data_manager.get_questions(),
        'candidates': data_manager.get_candidates(),
        'meta': data_manager.get_meta(),
        'exported_at': data_manager.get_meta().get('content', {}).get('last_updated', '')
    }
    
    return jsonify(data)


@admin_bp.route('/import_data', methods=['POST'])
@handle_api_errors
def import_data():
    """Tuodaan data"""
    # Mock toteutus
    return jsonify({'success': True, 'message': 'Data tuotu onnistuneesti'})


@admin_bp.route('/clear_cache', methods=['POST'])
@handle_api_errors
def clear_cache():
    """Tyhjentää välimuistin"""
    # Mock toteutus
    return jsonify({'success': True, 'message': 'Välimuisti tyhjennetty'})


@admin_bp.route('/approve_question/<int:question_id>', methods=['POST'])
@handle_api_errors
def approve_question(question_id):
    """Hyväksyy kysymyksen"""
    # Mock toteutus
    return jsonify({'success': True, 'message': 'Kysymys hyväksytty'})


@admin_bp.route('/reject_question/<int:question_id>', methods=['POST'])
@handle_api_errors
def reject_question(question_id):
    """Hylkää kysymyksen"""
    # Mock toteutus
    return jsonify({'success': True, 'message': 'Kysymys hylätty'})


# IPFS Synkronointi API-reitit
@admin_bp.route('/sync', methods=['POST'])
@handle_api_errors
def manual_sync():
    """Käynnistää manuaalisen synkronoinnin"""
    return jsonify({
        'success': True,
        'message': 'Synkronointi käynnistetty',
        'status': 'completed'
    })


@admin_bp.route('/sync_status')
@handle_api_errors
def get_sync_status():
    """Hakee synkronoinnin tilan"""
    return jsonify({
        'status': 'completed',
        'last_sync': data_manager.get_meta().get('content', {}).get('last_updated', ''),
        'peers_found': 0,
        'data_imported': 0
    })


@admin_bp.route('/peers')
@handle_api_errors
def get_peers():
    """Hakee löydetyt peerit"""
    return jsonify([])


@admin_bp.route('/enable_auto_sync', methods=['POST'])
@handle_api_errors
def enable_auto_sync():
    """Ota automaattinen synkronointi käyttöön"""
    return jsonify({'success': True, 'message': 'Automaattinen synkronointi käytössä'})


@admin_bp.route('/disable_auto_sync', methods=['POST'])
@handle_api_errors
def disable_auto_sync():
    """Poista automaattinen synkronointi käytöstä"""
    return jsonify({'success': True, 'message': 'Automaattinen synkronointi pois käytöstä'})
