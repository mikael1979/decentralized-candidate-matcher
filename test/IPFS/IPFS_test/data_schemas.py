# data_schemas.py
"""
Määrittelee kaikkien järjestelmän data-tiedostojen oletusrakenteet.
Käytetään sekä asennuksessa että ajonaikaisessa tiedostonhallinnassa.
"""
import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional

def _get_current_time() -> str:
    return datetime.now().isoformat()

# === YDINRAKENTEET ===

def get_questions_schema(election_id: str = "default_election", system_id: str = "") -> Dict[str, Any]:
    return {
        "election_id": election_id,
        "language": "fi",
        "questions": [],
        "metadata": {
            "created": _get_current_time(),
            "system_id": system_id,
            "election_id": election_id,
            "fingerprint": "",
            "signature": None
        }
    }

def get_candidates_schema(election_id: str = "default_election", system_id: str = "") -> Dict[str, Any]:
    return {
        "election_id": election_id,
        "language": "fi",
        "candidates": [],
        "party_keys": {},
        "metadata": {
            "created": _get_current_time(),
            "system_id": system_id,
            "election_id": election_id,
            "fingerprint": "",
            "signature": None
        }
    }

def get_newquestions_schema(election_id: str = "default_election", system_id: str = "") -> Dict[str, Any]:
    return {
        "election_id": election_id,
        "language": "fi",
        "question_type": "user_submitted",
        "questions": [],
        "metadata": {
            "created": _get_current_time(),
            "system_id": system_id,
            "election_id": election_id,
            "fingerprint": "",
            "signature": None
        }
    }

def get_comments_schema(election_id: str = "default_election", system_id: str = "") -> Dict[str, Any]:
    return {
        "election_id": election_id,
        "language": "fi",
        "comments": [],
        "metadata": {
            "created": _get_current_time(),
            "system_id": system_id,
            "election_id": election_id,
            "fingerprint": "",
            "signature": None
        }
    }

def get_ipfs_sync_queue_schema() -> Dict[str, Any]:
    return {
        "pending_questions": [],
        "last_sync": None,
        "sync_interval_minutes": 10,
        "max_questions_per_sync": 20
    }

def get_ipfs_questions_cache_schema() -> Dict[str, Any]:
    return {
        "last_fetch": None,
        "questions": []
    }

def get_active_questions_schema(election_id: str = "default_election") -> Dict[str, Any]:
    return {
        "election_id": election_id,
        "last_updated": _get_current_time(),
        "strategy": "top_elo",
        "questions": [],
        "count": 0,
        "metadata": {
            "generated_by": "DataManager",
            "ttl_seconds": 300  # 5 min välimuistia
        }
    }

def get_meta_schema(
    election_data: Optional[Dict] = None,
    admins: Optional[list] = None,
    public_key_pem: str = "",
    system_id: str = "",
    questions_count: int = 0,
    candidates_count: int = 0,
    parties_count: int = 0
) -> Dict[str, Any]:
    election_data = election_data or {}
    admins = admins or []
    return {
        "system": "Decentralized Candidate Matcher",
        "version": "0.0.6-alpha",
        "election": election_data,
        "community_moderation": {
            "enabled": True,
            "thresholds": {
                "auto_block_inappropriate": 0.7,
                "auto_block_min_votes": 10,
                "community_approval": 0.8
            },
            "ipfs_sync_mode": "elo_priority"
        },
        "admins": admins,
        "key_management": {
            "system_public_key": public_key_pem,
            "key_algorithm": "RSA-2048",
            "parties_require_keys": True,
            "candidates_require_keys": False
        },
        "content": {
            "last_updated": _get_current_time(),
            "questions_count": questions_count,
            "candidates_count": candidates_count,
            "parties_count": parties_count
        },
        "system_info": {
            "system_id": system_id,
            "installation_time": _get_current_time(),
            "key_fingerprint": hashlib.sha256(public_key_pem.encode()).hexdigest() if public_key_pem else ""
        },
        "integrity": {
            "algorithm": "sha256",
            "hash": "",
            "computed": _get_current_time()
        },
        "metadata": {
            "created": _get_current_time(),
            "system_id": system_id,
            "election_id": election_data.get("id", ""),
            "fingerprint": "",
            "signature": None
        }
    }

# === HELPER: SCHEMA-MAPPI ===

SCHEMA_MAP = {
    'questions.json': get_questions_schema,
    'candidates.json': get_candidates_schema,
    'newquestions.json': get_newquestions_schema,
    'comments.json': get_comments_schema,
    'ipfs_sync_queue.json': get_ipfs_sync_queue_schema,
    'ipfs_questions_cache.json': get_ipfs_questions_cache_schema,
    'active_questions.json': get_active_questions_schema,
    'meta.json': get_meta_schema,
}

# === APUMETODI: LATAA TAI LUO TIEDOSTO ===

def ensure_data_file(filepath: str, **kwargs) -> Dict[str, Any]:
    """
    Lataa tiedosto, tai luo se skeeman perusteella, jos sitä ei ole.
    Käytetään DataManagerissa ja install.py:ssä.
    """
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    # Päättele tiedostonimi
    filename = os.path.basename(filepath)
    if filename not in SCHEMA_MAP:
        raise ValueError(f"Tuntematon tiedosto ilman skeemaa: {filename}")

    # Kutsu skeemafunktiota
    schema_func = SCHEMA_MAP[filename]
    data = schema_func(**kwargs)

    # Tallenna
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return data
