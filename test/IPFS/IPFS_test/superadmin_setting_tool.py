#!/usr/bin/env python3
"""
Superadmin CLI-työkalu vaalikoneen hallintaan
Mahdollistaa tmp/official -tiedostojen hallinnan ilman web-käyttöliittymää
"""
import os
import sys
import json
import argparse
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional

# === KONFIGURAATIO ===
DATA_DIR = 'data'  # data-hakemisto on olemassa

# === APUFUNKTIOT ===

def ensure_data_dir(data_dir: str) -> bool:
    """Varmistaa, että data-hakemisto on olemassa"""
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"✅ Luotiin data-hakemisto: {data_dir}")
    return True

def load_json_file(data_dir: str, filename: str) -> Optional[Dict]:
    """Lataa JSON-tiedoston"""
    filepath = os.path.join(data_dir, filename)
    if not os.path.exists(filepath):
        print(f"❌ Tiedostoa ei löydy: {filepath}")
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Virhe tiedoston {filename} lukemisessa: {e}")
        return None

def save_json_file(data_dir: str, filename: str, data: Dict) -> bool:
    """Tallentaa JSON-tiedoston turvallisesti (os.replace)"""
    try:
        ensure_data_dir(data_dir)
        filepath = os.path.join(data_dir, filename)
        tmp_path = filepath + '.tmp'
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, filepath)
        return True
    except Exception as e:
        print(f"❌ Virhe tiedoston {filename} tallentamisessa: {e}")
        tmp_path = os.path.join(data_dir, filename + '.tmp')
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        return False

def get_content_list(data_dir: str, content_type: str, source: str = 'official') -> List[Dict]:
    """Hakee sisällön listan"""
    file_map = {
        'questions': ('questions.json', 'questions'),
        'candidates': ('candidates.json', 'candidates'),
        'parties': ('candidates.json', 'candidates')
    }
    if content_type not in file_map:
        return []
    base_file, key = file_map[content_type]
    tmp_file = base_file.replace('.json', '_tmp.json')
    
    if source == 'tmp' and os.path.exists(os.path.join(data_dir, tmp_file)):
        print(f"📁 Ladataan tmp-tiedostosta: {tmp_file}")
        data = load_json_file(data_dir, tmp_file)
    else:
        print(f"📁 Ladataan virallisesta tiedostosta: {base_file}")
        data = load_json_file(data_dir, base_file)
    
    if not data:
        print(f"❌ Ei dataa ladattu tiedostosta")
        return []
        
    if content_type == 'parties':
        candidates = data.get(key, [])
        parties = list({c.get('party') for c in candidates if c.get('party')})
        return [{'name': p} for p in sorted(parties)]
    return data.get(key, [])

def sync_tmp_to_official(data_dir: str, content_type: str) -> bool:
    """Synkronoi tmp → official"""
    file_map = {
        'questions': 'questions.json',
        'candidates': 'candidates.json',
        'newquestions': 'newquestions.json'
    }
    if content_type not in file_map:
        return False
    base_file = file_map[content_type]
    tmp_file = base_file.replace('.json', '_tmp.json')
    tmp_path = os.path.join(data_dir, tmp_file)
    if not os.path.exists(tmp_path):
        print(f"❌ Tmp-tiedostoa ei löydy: {tmp_file}")
        print(f"📁 Hakemistossa olevat tiedostot: {os.listdir(data_dir)}")
        return False
    data = load_json_file(data_dir, tmp_file)
    if data is None:
        return False
    if save_json_file(data_dir, base_file, data):
        print(f"✅ Synkronoitu: {tmp_file} → {base_file}")
        return True
    return False

def update_content_in_tmp(data_dir: str, update_data: Dict) -> bool:
    """Muokkaa sisältöä tmp-tiedostossa (luo tmp-tiedoston tarvittaessa)"""
    content_type = update_data.get('type')
    item_id = update_data.get('id')
    changes = update_data.get('changes', {})
    file_map = {
        'question': 'questions.json',
        'candidate': 'candidates.json',
        'newquestion': 'newquestions.json'
    }
    if content_type not in file_map:
        print("❌ Tuntematon sisältötyyppi")
        return False
    base_file = file_map[content_type]
    tmp_file = base_file.replace('.json', '_tmp.json')
    
    # Lataa tmp-tiedosto tai luo uusi kopio virallisesta tiedostosta
    tmp_path = os.path.join(data_dir, tmp_file)
    if os.path.exists(tmp_path):
        print(f"📁 Käytetään olemassa olevaa tmp-tiedostoa: {tmp_file}")
        data = load_json_file(data_dir, tmp_file)
    else:
        official_path = os.path.join(data_dir, base_file)
        if not os.path.exists(official_path):
            print(f"❌ Virallista tiedostoa ei löydy: {base_file}")
            print(f"📁 Hakemistossa olevat tiedostot: {os.listdir(data_dir)}")
            return False
        print(f"📁 Luodaan tmp-tiedosto virallisesta: {base_file} → {tmp_file}")
        data = load_json_file(data_dir, base_file)  # Korjattu: käytetään base_file eikä koko polkua
        if data is None:
            return False
        # Luo tmp-tiedosto
        if not save_json_file(data_dir, tmp_file, data):
            print(f"❌ Tmp-tiedoston luonti epäonnistui: {tmp_file}")
            return False
        print(f"✅ Luotiin tmp-tiedosto: {tmp_file}")

    # Etsi kohde
    key = 'questions' if 'question' in content_type else 'candidates'
    items = data.get(key, [])
    target = None
    for item in items:
        if item.get('id') == item_id:
            target = item
            break
    if not target:
        print(f"❌ Kohdetta ei löytynyt ID:llä {item_id}")
        available_ids = [item.get('id') for item in items]
        print(f"✅ Käytettävissä olevat ID:t: {available_ids}")
        return False

    print(f"✅ Kohde löytyi: {target.get('question', {}).get('fi', target.get('name', 'Nimetön'))}")

    # Päivitä muutokset
    if 'elo_delta' in changes:
        delta = changes['elo_delta']
        target.setdefault('elo', {}).setdefault('deltas', []).append({
            'timestamp': datetime.now().isoformat(),
            'delta': delta.get('value', 0),
            'by': delta.get('user_id', 'superadmin'),
            'reason': delta.get('reason', 'Manual update')
        })
        base = target['elo'].get('base_rating', 1200)
        total_delta = sum(d.get('delta', 0) for d in target['elo']['deltas'])
        target['elo']['current_rating'] = base + total_delta
        print(f"✅ Päivitetty ELO: {base} → {base + total_delta}")
    else:
        # Käsittele sisäkkäiset polut kuten "question.fi"
        for path, value in changes.items():
            keys = path.split('.')
            current = target
            for key_part in keys[:-1]:
                if key_part not in current or not isinstance(current[key_part], dict):
                    current[key_part] = {}
                current = current[key_part]
            old_value = current.get(keys[-1], 'ei asetettu')
            current[keys[-1]] = value
            print(f"✅ Päivitetty kenttä {path}: '{old_value}' → '{value}'")

    return save_json_file(data_dir, tmp_file, data)

# === KOMENTORIVILIITTYMÄ ===

def main():
    parser = argparse.ArgumentParser(description='Superadmin CLI-työkalu vaalikoneeseen')
    subparsers = parser.add_subparsers(dest='command', help='Käytettävissä olevat komennot')

    # LISTAUS
    list_parser = subparsers.add_parser('list', help='Listaa sisältöä')
    list_parser.add_argument('--type', choices=['questions', 'candidates', 'parties'], required=True, help='Sisällön tyyppi')
    list_parser.add_argument('--source', choices=['official', 'tmp'], default='official', help='Lähde (oletus: official)')

    # SYNKRONOINTI
    sync_parser = subparsers.add_parser('sync', help='Synkronoi tmp → official')
    sync_parser.add_argument('--type', choices=['questions', 'candidates', 'newquestions'], required=True, help='Sisällön tyyppi')

    # PÄIVITYS
    update_parser = subparsers.add_parser('update', help='Päivitä sisältöä tmp-tiedostossa')
    update_parser.add_argument('--type', choices=['question', 'candidate', 'newquestion'], required=True, help='Kohdetyyppi')
    update_parser.add_argument('--id', type=int, required=True, help='Kohteen ID')
    update_parser.add_argument('--changes', required=True, help='Muutokset JSON-muodossa')

    # JÄRJESTELMÄKETJUN TARKISTUS
    chain_parser = subparsers.add_parser('verify-chain', help='Tarkista system_chain.json')

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    data_dir = DATA_DIR

    if args.command == 'list':
        items = get_content_list(data_dir, args.type, args.source)
        print(f"\n📋 {args.type.capitalize()} ({args.source}): {len(items)} kpl\n")
        for item in items:
            if args.type == 'parties':
                print(f"- {item['name']}")
            else:
                name = item.get('name', item.get('question', {}).get('fi', 'Nimetön'))
                item_id = item.get('id', '?')
                print(f"- ID {item_id}: {name}")

    elif args.command == 'sync':
        if sync_tmp_to_official(data_dir, args.type):
            print("✅ Synkronointi onnistui")
        else:
            print("❌ Synkronointi epäonnistui")
            sys.exit(1)

    elif args.command == 'update':
        try:
            changes = json.loads(args.changes)
        except json.JSONDecodeError:
            print("❌ Virheellinen JSON muutoksissa")
            sys.exit(1)
        update_data = {
            'type': args.type,
            'id': args.id,
            'changes': changes
        }
        if update_content_in_tmp(data_dir, update_data):
            print("✅ Päivitys onnistui tmp-tiedostoon")
        else:
            print("❌ Päivitys epäonnistui")
            sys.exit(1)

    elif args.command == 'verify-chain':
        chain_path = os.path.join(data_dir, 'system_chain.json')
        if not os.path.exists(chain_path):
            print("❌ system_chain.json ei löydy")
            sys.exit(1)
        with open(chain_path, 'r') as f:
            chain = json.load(f)
        current = chain.get('current_state', {})
        mismatches = []
        for filename, expected_hash in current.items():
            filepath = os.path.join(data_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    actual_hash = hashlib.sha256(f.read()).hexdigest()
                if actual_hash != expected_hash:
                    mismatches.append(filename)
        if mismatches:
            print("❌ EHEYSRIKKOMUS:")
            for f in mismatches:
                print(f"  - {f}")
            sys.exit(1)
        else:
            print("✅ Järjestelmän eheys tarkistettu onnistuneesti")

if __name__ == '__main__':
    main()
