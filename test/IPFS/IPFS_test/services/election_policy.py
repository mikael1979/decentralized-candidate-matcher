# services/election_policy.py
import json
import os
from datetime import datetime, timedelta
from typing import Optional

class ElectionPolicy:
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

    def is_content_editing_allowed(self, content_type: str = "all") -> bool:
        """
        Tarkistaa, onko sisällön muokkaus sallittu vaalilukituksen perusteella.
        """
        meta_path = os.path.join(self.data_dir, 'meta.json')
        meta = self._read_json_safe(meta_path)
        if not meta:
            # Jos metaa ei ole, oletetaan, että muokkaus on sallittu
            return True

        deadline_str = meta.get("election", {}).get("content_edit_deadline")
        if not deadline_str:
            return True

        try:
            # Tukemaan ISO-formaattia (mukaan lukien Z-loppuinen UTC)
            if deadline_str.endswith('Z'):
                deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
            else:
                deadline = datetime.fromisoformat(deadline_str)

            grace_hours = meta.get("election", {}).get("grace_period_hours", 24)
            grace_end = deadline + timedelta(hours=grace_hours)

            # Vertaa samaan aikavyöhykkeeseen (tai ilman, jos ei määritelty)
            now = datetime.now(deadline.tzinfo if deadline.tzinfo else None)

            allowed = now < grace_end
            return allowed

        except Exception as e:
            if self.debug:
                print(f"⚠️  Deadline-tarkistusvirhe: {e}")
            return True
