# services/meta_service.py
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from utils import calculate_hash
from data_schemas import SCHEMA_MAP

class MetaService:
    def __init__(self, data_dir: str = 'data', debug: bool = False):
        self.data_dir = data_dir
        self.debug = debug

    def _read_json_safe(self, filepath: str):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            if self.debug:
                print(f"❌ Virhe lukemisessa {filepath}: {e}")
            return None

    def _write_json(self, filename: str, data: Any, operation: str = "") -> bool:
        try:
            filepath = os.path.join(self.data_dir, filename)
            tmp_filepath = filepath + '.tmp'
            with open(tmp_filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_filepath, filepath)
            if self.debug:
                desc = f" - {operation}" if operation else ""
                print(f"💾 Kirjoitettu turvallisesti: {filename}{desc}")
            return True
        except Exception as e:
            tmp_path = os.path.join(self.data_dir, filename + '.tmp')
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
            if self.debug:
                print(f"❌ Virhe turvallisessa kirjoituksessa {filename}: {e}")
            return False

    def _ensure_meta_file(self) -> Dict:
        """Luo meta.json, jos sitä ei ole."""
        filepath = os.path.join(self.data_dir, 'meta.json')
        if os.path.exists(filepath):
            return self._read_json_safe(filepath) or {}

        # Lue system_id, jos meta.json on olemassa (mutta tässä vaiheessa ei ole)
        system_id = ""
        meta_path = filepath
        if os.path.exists(meta_path):
            try:
                existing_meta = self._read_json_safe(meta_path)
                if existing_meta:
                    system_id = existing_meta.get("system_info", {}).get("system_id", system_id)
            except Exception:
                pass

        default_meta = {
            "system": "Decentralized Candidate Matcher",
            "version": "0.0.6-alpha",
            "election": {
                "id": "default_election",
                "country": "FI",
                "name": {"fi": "Nimetön vaalit", "en": "Unnamed Election", "sv": "Namnlös val"},
                "date": "2025-01-01",
                "language": "fi"
            },
            "community_moderation": {
                "enabled": True,
                "thresholds": {
                    "auto_block_inappropriate": 0.7,
                    "auto_block_min_votes": 10,
                    "community_approval": 0.8
                },
                "ipfs_sync_mode": "elo_priority"
            },
            "admins": [],
            "key_management": {
                "system_public_key": "",
                "key_algorithm": "RSA-2048",
                "parties_require_keys": True,
                "candidates_require_keys": False
            },
            "content": {
                "last_updated": datetime.now().isoformat(),
                "questions_count": 0,
                "candidates_count": 0,
                "parties_count": 0
            },
            "system_info": {
                "system_id": system_id,
                "installation_time": datetime.now().isoformat(),
                "key_fingerprint": ""
            }
        }

        meta_data = default_meta.copy()
        meta_data["integrity"] = {
            "algorithm": "sha256",
            "hash": calculate_hash(meta_data),
            "computed": datetime.now().isoformat()
        }

        self._write_json('meta.json', meta_data, "Luotiin meta.json")
        return meta_data

    def get_meta(self, content_service) -> Dict:
        """
        Hakee ja päivittää meta-tiedot.
        :param content_service: ContentService-instanssi tilastojen laskemiseen
        """
        meta = self._ensure_meta_file()

        # Hae tilastot ContentServiceltä
        questions = content_service.get_questions(include_blocked=False, include_ipfs=False)
        candidates = content_service.get_candidates()
        parties = list(set(c.get('party', '') for c in candidates if c.get('party')))

        meta['content'] = {
            'last_updated': datetime.now().isoformat(),
            'questions_count': len(questions),
            'candidates_count': len(candidates),
            'parties_count': len(parties)
        }

        meta['integrity'] = {
            'algorithm': 'sha256',
            'hash': calculate_hash(meta),
            'computed': datetime.now().isoformat()
        }

        self._write_json('meta.json', meta, "Päivitetty meta-tilastot")
        return meta

    def update_meta(self, new_meta: Dict) -> bool:
        """Päivittää meta.json ilman tilastojen laskemista (olettaa, että ne on jo asetettu)."""
        try:
            current_meta = self._ensure_meta_file()
            # Säilytä nykyiset tilastot, ellei niitä anneta
            if 'content' not in new_meta and 'content' in current_meta:
                new_meta['content'] = current_meta['content']

            new_meta['integrity'] = {
                'algorithm': 'sha256',
                'hash': calculate_hash(new_meta),
                'computed': datetime.now().isoformat()
            }

            return self._write_json('meta.json', new_meta, "Meta-tiedot päivitetty")
        except Exception as e:
            if self.debug:
                print(f"❌ Meta-tietojen päivitys epäonnistui: {e}")
            return False
