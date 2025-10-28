# services/election_locker.py
import json
import os
from datetime import datetime
from typing import Any


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


def lock_election_content(
    data_dir: str,
    ipfs_client,
    content_service,
    meta_service,
    debug: bool = False
) -> str:
    """
    Lukitsee vaalisisällön IPFS:iin ja kirjoittaa turvallisuuslokin.
    """
    if not ipfs_client:
        raise RuntimeError("IPFS-asiakas vaaditaan")

    # Hae nykyiset tiedot
    questions_data = content_service._ensure_data_file('questions.json')
    candidates_data = content_service._ensure_data_file('candidates.json')
    meta = meta_service.get_meta(content_service)

    snapshot = {
        "election_id": meta["election"]["id"],
        "locked_at": datetime.now().isoformat(),
        "questions": questions_data.get("questions", []),
        "candidates": candidates_data.get("candidates", []),
        "meta_hash": meta["integrity"]["hash"]
    }

    # Tallenna paikallisesti (valinnainen, mutta hyödyllinen)
    _write_json(data_dir, 'election_snapshot.json', snapshot, "Vaalilukitus-snapshot", debug)

    # Lähetä IPFS:iin
    result = ipfs_client.add_json(snapshot)
    if not result or 'Hash' not in result:
        raise RuntimeError("IPFS-lähetys epäonnistui")

    cid = result["Hash"]

    # Päivitä järjestelmäketju (käytä security-palvelua)
    from services.security import update_system_chain_ipfs
    update_system_chain_ipfs(
        data_dir=data_dir,
        modified_files=['election_snapshot.json'],
        ipfs_cids={'election_snapshot.json': cid},
        debug=debug
    )

    # Kirjoita turvallisuusloki
    log_entry = f"{datetime.now().isoformat()} | ACTION=election_lock | CID={cid}\n"
    with open("security_audit.log", "a", encoding="utf-8") as log:
        log.write(log_entry)

    return cid
