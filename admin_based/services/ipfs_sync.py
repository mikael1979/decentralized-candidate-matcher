# services/ipfs_sync.py
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any

from utils import generate_next_id


def _read_json_safe(data_dir: str, filename: str):
    filepath = os.path.join(data_dir, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def _write_json(data_dir: str, filename: str, data: Any, operation: str = "", debug: bool = False):
    try:
        filepath = os.path.join(data_dir, filename)
        tmp_filepath = filepath + '.tmp'
        with open(tmp_filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_filepath, filepath)
        if debug:
            desc = f" - {operation}" if operation else ""
            print(f"💾 Kirjoitettu turvallisesti: {filename}{desc}")
        return True
    except Exception as e:
        tmp_path = os.path.join(data_dir, filename + '.tmp')
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass
        if debug:
            print(f"❌ Virhe turvallisessa kirjoituksessa {filename}: {e}")
        return False


def queue_for_ipfs_sync(data_dir: str, question_id: int, content_service, debug: bool = False) -> bool:
    queue = _read_json_safe(data_dir, 'ipfs_sync_queue.json')
    if queue is None:
        queue = {"pending_questions": [], "last_sync": None, "sync_interval_minutes": 10, "max_questions_per_sync": 20}

    all_questions = content_service.get_questions(include_blocked=True, include_ipfs=False)
    question = next((q for q in all_questions if q.get('id') == question_id), None)
    if not question:
        return False

    queue['pending_questions'].append({
        'question_id': question_id,
        'added_to_queue_at': datetime.now().isoformat(),
        'elo_rating': question.get('elo', {}).get('current_rating', 1200),
        'status': 'pending'
    })

    return _write_json(data_dir, 'ipfs_sync_queue.json', queue, "Kysymys lisätty synkronointijonoon", debug)


def process_ipfs_sync(data_dir: str, ipfs_client, meta_service, content_service, debug: bool = False) -> bool:
    queue = _read_json_safe(data_dir, 'ipfs_sync_queue.json')
    if not queue or not queue.get('pending_questions'):
        return False

    last_sync = queue.get('last_sync')
    interval = queue.get('sync_interval_minutes', 10)
    if last_sync:
        last_sync_time = datetime.fromisoformat(last_sync.replace('Z', '+00:00'))
        if (datetime.now() - last_sync_time).total_seconds() < interval * 60:
            return False

    max_sync = queue.get('max_questions_per_sync', 20)
    pending = [q for q in queue['pending_questions'] if q['status'] == 'pending']

    meta = meta_service._ensure_meta_file()  # huom: väliaikainen – myöhemmin get_meta ilman content_service
    selection_mode = meta.get('community_moderation', {}).get('ipfs_sync_mode', 'elo_priority')

    if selection_mode == 'elo_priority':
        pending.sort(key=lambda x: x.get('elo_rating', 1200), reverse=True)
    else:
        pending.sort(key=lambda x: x.get('added_to_queue_at', ''))

    selected = pending[:max_sync]
    if not selected or not ipfs_client:
        return False

    ipfs_questions = []
    all_questions = content_service.get_questions(include_blocked=True, include_ipfs=False)
    for item in selected:
        question = next((q for q in all_questions if q.get('id') == item['question_id']), None)
        if question:
            ipfs_questions.append(question)

    if not ipfs_questions:
        return False

    ipfs_data = {
        "election_id": meta.get("election", {}).get("id"),
        "timestamp": datetime.now().isoformat(),
        "questions": ipfs_questions
    }

    result = ipfs_client.add_json(ipfs_data)
    if not result:
        return False

    for item in selected:
        item['status'] = 'synced'
        item['synced_at'] = datetime.now().isoformat()
        item['ipfs_cid'] = result["Hash"]

    queue['last_sync'] = datetime.now().isoformat()
    # Päivitä jono: poista vanhat ja lisää päivitetyt
    remaining = [q for q in queue['pending_questions'] if q not in selected]
    queue['pending_questions'] = remaining + selected

    success = _write_json(data_dir, 'ipfs_sync_queue.json', queue, f"Synkronoitu {len(selected)} kysymystä IPFS:iin", debug)
    return success


def fetch_questions_from_ipfs(data_dir: str, ipfs_client, debug: bool = False) -> bool:
    if not ipfs_client:
        return False

    try:
        well_known_cid = "QmWellKnownQuestionsList"
        ipfs_data = ipfs_client.get_json(well_known_cid)
        if not ipfs_data:
            return False

        cache = {
            "last_fetch": datetime.now().isoformat(),
            "questions": ipfs_data.get("questions", [])
        }

        return _write_json(data_dir, "ipfs_questions_cache.json", cache, "IPFS-kysymykset välimuistiin", debug)

    except Exception as e:
        if debug:
            print(f"❌ IPFS-haku epäonnistui: {e}")
        return False
