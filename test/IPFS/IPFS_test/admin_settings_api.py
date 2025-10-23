# admin_settings_api.py

import json
import os
import argparse
import re
from datetime import datetime
from typing import Dict, Any, Optional

# ----------------------------
# Ydinlogiikka (ei riipu Flaskista)
# ----------------------------

def load_meta(data_dir: str = 'data') -> Optional[Dict]:
    filepath = os.path.join(data_dir, 'meta.json')
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def calculate_hash(data: Dict) -> str:
    from hashlib import sha256
    data_str = json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    return sha256(data_str.encode()).hexdigest()

def save_meta(meta: Dict, data_dir: str = 'data') -> bool:
    try:
        filepath = os.path.join(data_dir, 'meta.json')
        tmp_path = filepath + '.tmp'

        # Päivitä integrity
        meta['integrity'] = {
            'algorithm': 'sha256',
            'hash': calculate_hash(meta),
            'computed': datetime.now().isoformat()
        }

        # Kirjoita väliaikaistiedostoon
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, filepath)
        return True
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        return False

def update_settings_core(new_settings: Dict[str, Any], data_dir: str = 'data') -> bool:
    current = load_meta(data_dir)
    if not current:
        return False

    # Päivitä election
    if 'election' in new_settings:
        current['election'] = new_settings['election']

    # Päivitä community_moderation
    if 'community_moderation' in new_settings:
        current['community_moderation'] = new_settings['community_moderation']

    # Päivitä system name/version
    if 'system' in new_settings:
        sys = new_settings['system']
        if 'name' in sys:
            current['system'] = sys['name']
        if 'version' in sys:
            current['version'] = sys['version']

    return save_meta(current, data_dir)

# ----------------------------
# Flask-integraatio
# ----------------------------

def init_admin_settings_api(app, data_manager, admin_login_required):
    from flask import request, jsonify
    from utils import handle_api_errors

    @app.route('/api/admin/settings', methods=['GET'])
    @admin_login_required
    @handle_api_errors
    def get_settings():
        meta = data_manager.get_meta()
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
    def update_settings():
        new_data = request.json
        if not isinstance(new_data, dict):
            return jsonify({'success': False, 'error': 'Invalid request'}), 400

        # Validointi
        errors = []

        if 'election' in new_data:
            e = new_data['election']
            if 'date' in e and not re.match(r'^\d{4}-\d{2}-\d{2}$', e['date']):
                errors.append('election.date must be YYYY-MM-DD')
            try:
                if 'date' in e:
                    datetime.strptime(e['date'], '%Y-%m-%d')
            except ValueError:
                errors.append('Invalid election date')

        if 'community_moderation' in new_data:
            cm = new_data['community_moderation']
            th = cm.get('thresholds', {})
            for k in ['auto_block_inappropriate', 'community_approval']:
                if k in th and not (0.0 <= th[k] <= 1.0):
                    errors.append(f'{k} must be between 0.0 and 1.0')
            if 'auto_block_min_votes' in th:
                v = th['auto_block_min_votes']
                if not isinstance(v, int) or v < 1:
                    errors.append('auto_block_min_votes must be a positive integer')
            if 'ipfs_sync_mode' in cm and cm['ipfs_sync_mode'] not in ['elo_priority', 'fifo']:
                errors.append('ipfs_sync_mode must be "elo_priority" or "fifo"')

        if errors:
            return jsonify({'success': False, 'errors': errors}), 400

        # Päivitä koko meta
        current_meta = data_manager.get_meta()
        if 'election' in new_data:
            current_meta['election'] = new_data['election']
        if 'community_moderation' in new_data:
            current_meta['community_moderation'] = new_data['community_moderation']
        if 'system' in new_data:
            sys = new_data['system']
            if 'name' in sys:
                current_meta['system'] = sys['name']
            if 'version' in sys:
                current_meta['version'] = sys['version']

        success = data_manager.update_meta(current_meta)
        return jsonify({'success': success})

# ----------------------------
# CLI-rajapinta
# ----------------------------

def main_cli():
    parser = argparse.ArgumentParser(description='Vaalikoneen asetusmuokkaus')
    parser.add_argument('--election-name-fi', help='Vaalien nimi suomeksi')
    parser.add_argument('--election-date', help='Vaalipäivä (YYYY-MM-DD)')
    parser.add_argument('--auto-block-threshold', type=float, help='Auto-block kynnys (0.0–1.0)')
    parser.add_argument('--ipfs-sync-mode', choices=['elo_priority', 'fifo'], help='IPFS-synkronointistrategia')
    parser.add_argument('--system-name', help='Järjestelmän nimi')
    parser.add_argument('--system-version', help='Järjestelmän versio')
    parser.add_argument('--data-dir', default='data', help='Data-hakemisto')

    args = parser.parse_args()
    new_settings = {}

    if any([args.election_name_fi, args.election_date]):
        meta = load_meta(args.data_dir)
        if not meta:
            print("❌ Ei löydy meta.json:ia")
            return
        new_settings['election'] = meta.get('election', {}).copy()
        if args.election_name_fi:
            new_settings['election']['name']['fi'] = args.election_name_fi
        if args.election_date:
            new_settings['election']['date'] = args.election_date

    if args.auto_block_threshold is not None or args.ipfs_sync_mode:
        meta = load_meta(args.data_dir)
        if not meta:
            print("❌ Ei löydy meta.json:ia")
            return
        new_settings['community_moderation'] = meta.get('community_moderation', {}).copy()
        if args.auto_block_threshold is not None:
            new_settings['community_moderation']['thresholds']['auto_block_inappropriate'] = args.auto_block_threshold
        if args.ipfs_sync_mode:
            new_settings['community_moderation']['ipfs_sync_mode'] = args.ipfs_sync_mode

    if args.system_name or args.system_version:
        new_settings['system'] = {}
        if args.system_name:
            new_settings['system']['name'] = args.system_name
        if args.system_version:
            new_settings['system']['version'] = args.system_version

    if new_settings:
        if update_settings_core(new_settings, args.data_dir):
            print("✅ Asetukset päivitetty")
        else:
            print("❌ Päivitys epäonnistui")
    else:
        print("ℹ️  Käytä --help nähdäksesi vaihtoehdot")

if __name__ == '__main__':
    main_cli()
