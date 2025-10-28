# services/security.py
import json
import os
import hashlib
import base64
from datetime import datetime
from typing import List, Dict, Optional

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


def _read_json_safe(data_dir: str, filename: str):
    filepath = os.path.join(data_dir, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def _write_json(data_dir: str, filename: str,  Any, operation: str = "", debug: bool = False):
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


def _load_private_key(keys_dir: str = 'keys'):
    """Lataa salausavaimen (ei salasanasuojattu tässä versiossa)"""
    key_path = os.path.join(keys_dir, 'private_key.pem')
    with open(key_path, 'rb') as f:
        return serialization.load_pem_private_key(
            f.read(),
            password=None
        )


def update_system_chain_ipfs(
    data_dir: str,
    modified_files: List[str],
    ipfs_cids: Dict[str, str],
    debug: bool = False
) -> bool:
    """
    Päivittää järjestelmäketjun (system_chain.json) ja kirjoittaa turvallisuuslokin.
    """
    chain_path = os.path.join(data_dir, 'system_chain.json')
    chain = _read_json_safe(data_dir, 'system_chain.json') or {}

    # Alusta ketju, jos sitä ei ole
    if not chain:
        meta = _read_json_safe(data_dir, 'meta.json') or {}
        election_id = meta.get("election", {}).get("id", "default_election")
        system_id = meta.get("system_info", {}).get("system_id", "")

        chain = {
            "chain_id": election_id,
            "created_at": datetime.now().isoformat(),
            "description": "Fingerprint-ketju kaikille järjestelmän tiedostoille",
            "version": "0.0.6-alpha",
            "blocks": [],
            "current_state": {},
            "ipfs_cids": {},
            "metadata": {
                "algorithm": "sha256",
                "system_id": system_id,
                "election_id": election_id
            }
        }

    # Päivitä tiedostojen nykytila (hashit)
    for filepath in modified_files:
        filename = os.path.basename(filepath)
        full_path = os.path.join(data_dir, filename)
        if os.path.exists(full_path):
            with open(full_path, 'rb') as f:
                chain['current_state'][filename] = hashlib.sha256(f.read()).hexdigest()

    # Päivitä IPFS CID:t
    current_cids = chain.get('ipfs_cids', {})
    current_cids.update(ipfs_cids)
    chain['ipfs_cids'] = current_cids

    # Luo uusi lohko
    last_block = chain['blocks'][-1] if chain['blocks'] else None
    new_block = {
        "block_id": len(chain['blocks']),
        "timestamp": datetime.now().isoformat(),
        "description": f"IPFS-päivitys: {', '.join(modified_files)}",
        "files": chain['current_state'].copy(),
        "ipfs_cids": current_cids.copy(),
        "previous_hash": last_block['block_hash'] if last_block else None
    }

    # Laske lohkon hash
    block_data = {k: v for k, v in new_block.items() if k != 'block_hash'}
    block_hash = hashlib.sha256(json.dumps(block_data, sort_keys=True).encode()).hexdigest()
    new_block['block_hash'] = f"sha256:{block_hash}"

    # Allekirjoita lohko
    try:
        private_key = _load_private_key()
        signature = private_key.sign(
            json.dumps(block_data, sort_keys=True).encode(),
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        new_block['signature'] = base64.b64encode(signature).decode()
    except Exception as e:
        if debug:
            print(f"⚠️  Allekirjoitus epäonnistui: {e}")
        new_block['signature'] = None

    chain['blocks'].append(new_block)

    # Allekirjoita koko ketju
    try:
        clean_chain = {k: v for k, v in chain.items() if k != 'metadata'}
        chain_signature = private_key.sign(
            json.dumps(clean_chain, sort_keys=True).encode(),
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        chain['metadata']['signature'] = base64.b64encode(chain_signature).decode()
    except Exception as e:
        if debug:
            print(f"⚠️  Ketjun allekirjoitus epäonnistui: {e}")
        chain['metadata']['signature'] = None

    # Kirjoita ketju tiedostoon
    success = _write_json(data_dir, 'system_chain.json', chain, "IPFS-system chain päivitetty", debug)

    if success:
        cid_str = ', '.join(f"{k}:{v}" for k, v in ipfs_cids.items()) if ipfs_cids else "ei CID:iä"
        log_entry = (
            f"{datetime.now().isoformat()} | ACTION=chain_update | "
            f"FILES={', '.join(modified_files)} | CIDS={cid_str}\n"
        )
        with open("security_audit.log", "a", encoding="utf-8") as log:
            log.write(log_entry)

    return success
