# admin_settings_api.py

from flask import request, jsonify
from utils import handle_api_errors
import re
from datetime import datetime

def init_admin_settings_api(app, data_manager, admin_login_required):
    """
    Alustaa admin-asetus API:n:
    - Vaalitiedot (nimi, päivämäärä, kieliversiot)
    - Yhteisömoderaation kynnysarvot
    - IPFS-synkronointistrategia
    """

    @app.route('/api/admin/settings', methods=['GET'])
    @admin_login_required
    @handle_api_errors
    def admin_get_settings():
        """Palauttaa nykyiset muokattavat asetukset"""
        meta = data_manager.get_meta()
        if not meta:
            return jsonify({'success': False, 'error': 'Meta-tietoja ei löydy'}), 500

        return jsonify({
            'election': meta.get('election', {}),
            'community_moderation': meta.get('community_moderation', {}),
            'system': {
                'name': meta.get('system'),
                'version': meta.get('version')
            }
        })

    @app.route('/api/admin/settings', methods=['POST'])
    @admin_login_required
    @handle_api_errors
    def admin_update_settings():
        """Päivittää järjestelmäasetukset"""
        new_data = request.json
        if not isinstance(new_data, dict):
            return jsonify({'success': False, 'error': 'Virheellinen pyynnön rakenne'}), 400

        # Hae nykyinen meta
        current_meta = data_manager.get_meta()
        if not current_meta:
            return jsonify({'success': False, 'error': 'Meta-tietoja ei löydy'}), 500

        errors = []

        # === 1. VAALITIEDOT ===
        if 'election' in new_data:
            election = new_data['election']
            # Päivämäärä
            if 'date' in election:
                date_str = election['date']
                if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
                    errors.append('election.date: Virheellinen muoto (YYYY-MM-DD)')
                else:
                    try:
                        datetime.strptime(date_str, '%Y-%m-%d')
                    except ValueError:
                        errors.append('election.date: Virheellinen päivämäärä')
            # Kieliversiot
            for lang in ['fi', 'en', 'sv']:
                if 'name' in election and lang in election['name']:
                    name = election['name'][lang]
                    if not isinstance(name, str) or len(name.strip()) == 0:
                        errors.append(f'election.name.{lang}: Ei saa olla tyhjä')

            if not errors:
                current_meta['election'] = election

        # === 2. YHTEISÖMODERAATIO ===
        if 'community_moderation' in new_data:
            cm = new_data['community_moderation']
            thresholds = cm.get('thresholds', {})
            # auto_block_inappropriate (0.0–1.0)
            if 'auto_block_inappropriate' in thresholds:
                val = thresholds['auto_block_inappropriate']
                if not (isinstance(val, (int, float)) and 0.0 <= val <= 1.0):
                    errors.append('community_moderation.thresholds.auto_block_inappropriate: Arvon tulee olla 0.0–1.0')
            # community_approval (0.0–1.0)
            if 'community_approval' in thresholds:
                val = thresholds['community_approval']
                if not (isinstance(val, (int, float)) and 0.0 <= val <= 1.0):
                    errors.append('community_moderation.thresholds.community_approval: Arvon tulee olla 0.0–1.0')
            # auto_block_min_votes (positiivinen kokonaisluku)
            if 'auto_block_min_votes' in thresholds:
                val = thresholds['auto_block_min_votes']
                if not (isinstance(val, int) and val >= 1):
                    errors.append('community_moderation.thresholds.auto_block_min_votes: Arvon tulee olla positiivinen kokonaisluku')
            # IPFS-synkronointistrategia
            if 'ipfs_sync_mode' in cm:
                mode = cm['ipfs_sync_mode']
                if mode not in ['elo_priority', 'fifo']:
                    errors.append('community_moderation.ipfs_sync_mode: Sallitut arvot: "elo_priority", "fifo"')

            if not errors:
                current_meta['community_moderation'] = cm

        # === 3. JÄRJESTELMÄN PERUSTIEDOT ===
        if 'system' in new_data:
            sys = new_data['system']
            if 'name' in sys and isinstance(sys['name'], str):
                current_meta['system'] = sys['name']
            if 'version' in sys and isinstance(sys['version'], str):
                current_meta['version'] = sys['version']

        # Palauta virheet, jos niitä on
        if errors:
            return jsonify({'success': False, 'errors': errors}), 400

        # Tallenna päivitetty meta
        success = data_manager.update_meta(current_meta)
        if success:
            return jsonify({'success': True, 'message': 'Asetukset päivitetty onnistuneesti'})
        else:
            return jsonify({'success': False, 'error': 'Tallennus epäonnistui'}), 500
