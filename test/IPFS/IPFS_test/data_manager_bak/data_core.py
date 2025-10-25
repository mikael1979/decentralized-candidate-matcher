import json
import os
from datetime import datetime
from utils import ConfigLoader, calculate_hash, generate_next_id
from data_schemas import SCHEMA_MAP

class DataManagerCore:
    def __init__(self, debug=False):
        self.debug = debug
        self.data_dir = 'data'
        self.config_loader = ConfigLoader()
        self.ipfs_client = None

    def set_ipfs_client(self, ipfs_client):
        self.ipfs_client = ipfs_client
        if self.debug:
            print("✅ IPFS-asiakas asetettu DataManagerille")

    def ensure_directories(self):
        directories = ['data', 'templates', 'static', 'config']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            if self.debug:
                print(f"📁 Kansio varmistettu: {directory}")

    def _read_json_safe(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            if self.debug:
                print(f"❌ Virhe lukemisessa {filepath}: {e}")
            return None

    def ensure_data_file(self, filename):
        filepath = os.path.join(self.data_dir, filename)
        if os.path.exists(filepath):
            return self._read_json_safe(filepath)

        if filename not in SCHEMA_MAP:
            raise ValueError(f"Tuntematon tiedosto ilman skeemaa: {filename}")

        election_id = "default_election"
        system_id = ""
        meta_path = os.path.join(self.data_dir, 'meta.json')
        if os.path.exists(meta_path):
            try:
                existing_meta = self._read_json_safe(meta_path)
                if existing_meta:
                    election_id = existing_meta.get("election", {}).get("id", election_id)
                    system_id = existing_meta.get("system_info", {}).get("system_id", system_id)
            except Exception:
                pass

        schema_func = SCHEMA_MAP[filename]
        kwargs = {}
        if 'election_id' in schema_func.__code__.co_varnames:
            kwargs['election_id'] = election_id
        if 'system_id' in schema_func.__code__.co_varnames:
            kwargs['system_id'] = system_id

        if filename == 'meta.json':
            default_meta = {
                "system": "Decentralized Candidate Matcher",
                "version": "0.0.6-alpha",
                "election": {
                    "id": election_id,
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
            data = self._initialize_meta_data(default_meta)
        else:
            data = schema_func(**kwargs)

        self.write_json(filename, data, f"Luotiin puuttuva tiedosto: {filename}")
        return data

    def _initialize_meta_data(self, default_meta):
        meta_data = default_meta.copy()
        meta_data.update({
            "integrity": {
                "algorithm": "sha256",
                "hash": "",
                "computed": datetime.now().isoformat()
            }
        })
        meta_data['integrity']['hash'] = calculate_hash(meta_data)
        return meta_data

    def read_json(self, filename):
        return self.ensure_data_file(filename)

    def write_json(self, filename, data, operation=""):
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
