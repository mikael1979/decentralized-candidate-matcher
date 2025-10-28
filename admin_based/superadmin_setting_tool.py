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

# superadmin_setting_tool.py - KORJATTU LUONTI-FUNKTIO
def create_tmp_file(data_dir: str, file_type: str) -> bool:
    """Luo tmp-tiedoston tietystä tiedostotyypistä - KORJATTU VERSIO"""
    file_map = {
        'questions': 'questions.json',
        'candidates': 'candidates.json', 
        'newquestions': 'newquestions.json',
        'all': None
    }
    
    if file_type not in file_map:
        print(f"❌ Tuntematon tiedostotyyppi: {file_type}")
        return False
    
    # Käsittele 'all' erikseen
    if file_type == 'all':
        return create_all_tmp_files(data_dir)
    
    base_file = file_map[file_type]
    tmp_file = base_file.replace('.json', '_tmp.json')
    
    # Tarkista että data-hakemisto on olemassa
    if not os.path.exists(data_dir):
        print(f"❌ Data-hakemistoa ei löydy: {data_dir}")
        return False
        
    official_path = os.path.join(data_dir, base_file)
    tmp_path = os.path.join(data_dir, tmp_file)
    
    # Tarkista onko tmp-tiedosto jo olemassa
    if os.path.exists(tmp_path):
        print(f"📁 Tmp-tiedosto on jo olemassa: {tmp_file}")
        return True
        
    # Tarkista onko virallista tiedostoa
    if not os.path.exists(official_path):
        print(f"❌ Virallista tiedostoa ei löydy: {base_file}")
        print(f"📁 Data-hakemiston sisältö: {os.listdir(data_dir)}")
        return False
        
    print(f"📁 Luodaan: {base_file} → {tmp_file}")
    
    try:
        # Lue virallinen tiedosto
        with open(official_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Kirjoita tmp-tiedosto
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Luotiin tmp-tiedosto: {tmp_file}")
        return True
        
    except Exception as e:
        print(f"❌ Tmp-tiedoston luonti epäonnistui: {e}")
        return False

def create_all_tmp_files(data_dir: str) -> bool:
    """Luo tmp-tiedostot kaikille data-tiedostoille"""
    print("🔄 LUODAAN TMP-TIEDOSTOT KAIKILLE DATA-TIEDOSTOILLE")
    print("-" * 50)
    
    file_types = ['questions', 'candidates', 'newquestions']
    success_count = 0
    total_count = len(file_types)
    
    for file_type in file_types:
        if create_tmp_file(data_dir, file_type):
            success_count += 1
    
    print(f"\n📊 YHTEENVETO: {success_count}/{total_count} tmp-tiedostoa luotu onnistuneesti")
    return success_count == total_count

def sync_tmp_to_official(data_dir: str, content_type: str) -> bool:
    """Synkronoi tmp → official"""
    file_map = {
        'questions': 'questions.json',
        'candidates': 'candidates.json',
        'newquestions': 'newquestions.json',
        'all': None  # Erikoistapaus - käsitellään erikseen
    }
    
    if content_type not in file_map:
        return False
    
    # Käsittele 'all' erikseen
    if content_type == 'all':
        return sync_all_tmp_files(data_dir)
    
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

def sync_all_tmp_files(data_dir: str) -> bool:
    """Synkronoi kaikki tmp-tiedostot official-tiedostoihin"""
    print("🔄 SYNKRONOIDAAN KAIKKI TMP-TIEDOSTOT")
    print("-" * 40)
    
    file_types = ['questions', 'candidates', 'newquestions']
    success_count = 0
    total_count = len(file_types)
    
    for file_type in file_types:
        if sync_tmp_to_official(data_dir, file_type):
            success_count += 1
    
    print(f"\n📊 YHTEENVETO: {success_count}/{total_count} tiedostoa synkronoitu onnistuneesti")
    return success_count == total_count

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
        data = load_json_file(data_dir, base_file)
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

def list_tmp_files(data_dir: str) -> None:
    """Listaa kaikki tmp-tiedostot"""
    print("📁 TMP-TIEDOSTOT DATA-HAKEMISTOSSA:")
    print("-" * 40)
    
    files = os.listdir(data_dir)
    tmp_files = [f for f in files if f.endswith('_tmp.json')]
    
    if not tmp_files:
        print("❌ Ei tmp-tiedostoja löytynyt")
        return
    
    for tmp_file in sorted(tmp_files):
        filepath = os.path.join(data_dir, tmp_file)
        file_size = os.path.getsize(filepath)
        modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))
        
        print(f"📄 {tmp_file}")
        print(f"   📏 Koko: {file_size} tavua")
        print(f"   ⏰ Muokattu: {modified_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Lataa data ja näytä perustiedot
        data = load_json_file(data_dir, tmp_file)
        if data:
            if 'questions' in data:
                count = len(data.get('questions', []))
                print(f"   ❓ Kysymyksiä: {count} kpl")
            elif 'candidates' in data:
                count = len(data.get('candidates', []))
                print(f"   👤 Ehdokkaita: {count} kpl")
        print()

def cleanup_tmp_file(data_dir: str, file_type: str) -> bool:
    """Poistaa tmp-tiedoston tietystä tiedostotyypistä"""
    file_map = {
        'questions': 'questions_tmp.json',
        'candidates': 'candidates_tmp.json', 
        'newquestions': 'newquestions_tmp.json',
        'all': None  # Erikoistapaus - käsitellään erikseen
    }
    
    if file_type not in file_map:
        print(f"❌ Tuntematon tiedostotyyppi: {file_type}")
        return False
    
    # Käsittele 'all' erikseen
    if file_type == 'all':
        return cleanup_all_tmp_files(data_dir)
    
    tmp_file = file_map[file_type]
    tmp_path = os.path.join(data_dir, tmp_file)
    
    if os.path.exists(tmp_path):
        try:
            os.remove(tmp_path)
            print(f"✅ Poistettu: {tmp_file}")
            return True
        except Exception as e:
            print(f"❌ Virhe poistaessa {tmp_file}: {e}")
            return False
    else:
        print(f"📄 Ei löytynyt: {tmp_file}")
        return True  # Palauta True koska tiedostoa ei ole = "siivottu"

def cleanup_all_tmp_files(data_dir: str) -> bool:
    """Poistaa kaikki tmp-tiedostot"""
    print("🧹 POISTETAAN KAIKKI TMP-TIEDOSTOT")
    print("-" * 40)
    
    files = os.listdir(data_dir)
    tmp_files = [f for f in files if f.endswith('_tmp.json')]
    
    success_count = 0
    total_count = len(tmp_files)
    
    for tmp_file in tmp_files:
        tmp_path = os.path.join(data_dir, tmp_file)
        try:
            os.remove(tmp_path)
            print(f"✅ Poistettu: {tmp_file}")
            success_count += 1
        except Exception as e:
            print(f"❌ Virhe poistaessa {tmp_file}: {e}")
    
    if total_count == 0:
        print("📄 Ei tmp-tiedostoja löytynyt")
        return True
    
    print(f"\n📊 YHTEENVETO: {success_count}/{total_count} tmp-tiedostoa poistettu")
    return success_count == total_count

def ipfs_sync(data_dir: str, sync_type: str) -> bool:
    """Suorittaa IPFS-synkronoinnin"""
    print("🌐 IPFS-SYNKRONOINTI")
    print("-" * 30)
    
    try:
        # Yritä importata IPFS-moduulit
        try:
            from data_manager import DataManager
            from mock_ipfs import MockIPFS
            from real_ipfs import RealIPFS
        except ImportError as e:
            print(f"❌ IPFS-moduulien importointi epäonnistui: {e}")
            print("   Varmista että data_manager.py ja IPFS-moduulit ovat saatavilla")
            return False
        
        # Alusta DataManager ja IPFS
        data_manager = DataManager(debug=True)
        
        # Valitse IPFS-asiakas (tarkista --real-ipfs lippu)
        use_real_ipfs = '--real-ipfs' in sys.argv
        if use_real_ipfs:
            ipfs_client = RealIPFS()
            print("🌍 Käytetään oikeaa IPFS-solmua")
        else:
            ipfs_client = MockIPFS()
            print("🧪 Käytetään mock-IPFS:ää")
        
        data_manager.set_ipfs_client(ipfs_client)
        
        if sync_type == 'push':
            print("📤 Työnnetään data IPFS:ään...")
            success = data_manager.process_ipfs_sync()
            if success:
                print("✅ Data työnnetty onnistuneesti IPFS:ään")
                return True
            else:
                print("❌ IPFS-synkronointi epäonnistui tai ei tarvittu")
                return False
                
        elif sync_type == 'pull':
            print("📥 Haetaan data IPFS:stä...")
            success = data_manager.fetch_questions_from_ipfs()
            if success:
                print("✅ Data haettu onnistuneesti IPFS:stä")
                return True
            else:
                print("❌ IPFS-datan haku epäonnistui")
                return False
                
        elif sync_type == 'status':
            print("📊 IPFS-tilan tarkistus...")
            queue = data_manager.read_json('ipfs_sync_queue.json') or {}
            cache = data_manager.read_json('ipfs_questions_cache.json') or {}
            
            print(f"📋 Synkronointijono: {len(queue.get('pending_questions', []))} kysymystä")
            print(f"💾 Välimuisti: {len(cache.get('questions', []))} kysymystä")
            print(f"⏰ Viimeisin synkronointi: {queue.get('last_sync', 'Ei koskaan')}")
            
            # Testaa IPFS-yhteys
            if hasattr(ipfs_client, 'connected'):
                print(f"🔗 IPFS-yhteys: {'✅ On' if ipfs_client.connected else '❌ Ei'}")
            
            return True
            
        else:
            print(f"❌ Tuntematon IPFS-synkronointityyppi: {sync_type}")
            return False
            
    except Exception as e:
        print(f"❌ IPFS-synkronointi epäonnistui: {e}")
        return False

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
    sync_parser.add_argument('--type', choices=['questions', 'candidates', 'newquestions', 'all'], 
                           required=True, help='Sisällön tyyppi')

    # PÄIVITYS
    update_parser = subparsers.add_parser('update', help='Päivitä sisältöä tmp-tiedostossa')
    update_parser.add_argument('--type', choices=['question', 'candidate', 'newquestion'], required=True, help='Kohdetyyppi')
    update_parser.add_argument('--id', type=int, required=True, help='Kohteen ID')
    update_parser.add_argument('--changes', required=True, help='Muutokset JSON-muodossa')

    # JÄRJESTELMÄKETJUN TARKISTUS
    chain_parser = subparsers.add_parser('verify-chain', help='Tarkista system_chain.json')

    # TMP-TIEDOSTOJEN HALLINTA
    create_parser = subparsers.add_parser('create-tmp-file', help='Luo tmp-tiedosto')
    create_parser.add_argument('--type', choices=['questions', 'candidates', 'newquestions', 'all'], 
                             required=True, help='Tiedostotyyppi')

    list_tmp_parser = subparsers.add_parser('list-tmp-files', help='Listaa kaikki tmp-tiedostot')

    cleanup_parser = subparsers.add_parser('cleanup-tmp-file', help='Poista tmp-tiedosto')
    cleanup_parser.add_argument('--type', choices=['questions', 'candidates', 'newquestions', 'all'], 
                              required=True, help='Tiedostotyyppi')

    # IPFS-SYNKRONOINTI
    ipfs_parser = subparsers.add_parser('ipfs-sync', help='IPFS-synkronointi')
    ipfs_parser.add_argument('--type', choices=['push', 'pull', 'status'], required=True,
                           help='push: työnnä data IPFS:ään, pull: hae data IPFS:stä, status: näytä tila')
    ipfs_parser.add_argument('--real-ipfs', action='store_true', 
                           help='Käytä oikeaa IPFS-solmua (oletus: mock-IPFS)')

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

    elif args.command == 'create-tmp-file':
        if create_tmp_file(data_dir, args.type):
            print("✅ Tmp-tiedoston luonti onnistui")
        else:
            print("❌ Tmp-tiedoston luonti epäonnistui")
            sys.exit(1)

    elif args.command == 'list-tmp-files':
        list_tmp_files(data_dir)

    elif args.command == 'cleanup-tmp-file':
        if cleanup_tmp_file(data_dir, args.type):
            print("✅ Tmp-tiedoston siivous onnistui")
        else:
            print("❌ Tmp-tiedoston siivous epäonnistui")
            sys.exit(1)

    elif args.command == 'ipfs-sync':
        if ipfs_sync(data_dir, args.type):
            print("✅ IPFS-synkronointi onnistui")
        else:
            print("❌ IPFS-synkronointi epäonnistui")
            sys.exit(1)

if __name__ == '__main__':
    main()
