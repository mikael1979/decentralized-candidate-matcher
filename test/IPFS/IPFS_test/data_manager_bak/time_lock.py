import json
import os
from datetime import datetime, timedelta

class TimeLockMixin:
    def is_content_editing_allowed(self, content_type: str = "all") -> bool:
        meta = self.get_meta()
        deadline_str = meta.get("election", {}).get("content_edit_deadline")
        if not deadline_str:
            return True
        try:
            if deadline_str.endswith('Z'):
                deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
            else:
                deadline = datetime.fromisoformat(deadline_str)
            grace_hours = meta.get("election", {}).get("grace_period_hours", 24)
            grace_end = deadline + timedelta(hours=grace_hours)
            now = datetime.now(deadline.tzinfo if deadline.tzinfo else None)
            return now < grace_end
        except Exception as e:
            if self.debug:
                print(f"⚠️  Deadline-tarkistusvirhe: {e}")
            return True

    def lock_election_content(self):
        if not self.ipfs_client:
            raise RuntimeError("IPFS-asiakas vaaditaan")

        questions = self.ensure_data_file('questions.json')
        candidates = self.ensure_data_file('candidates.json')
        meta = self.get_meta()

        snapshot = {
            "election_id": meta["election"]["id"],
            "locked_at": datetime.now().isoformat(),
            "questions": questions.get("questions", []),
            "candidates": candidates.get("candidates", []),
            "meta_hash": meta["integrity"]["hash"]
        }

        result = self.ipfs_client.add_json(snapshot)
        cid = result["Hash"]

        # Päivitä system_chain (oletetaan että update_system_chain_ipfs on olemassa)
        self.update_system_chain_ipfs(
            modified_files=['election_snapshot.json'],
            ipfs_cids={'election_snapshot.json': cid}
        )

        with open("security_audit.log", "a", encoding="utf-8") as log:
            log.write(f"{datetime.now().isoformat()} | ACTION=election_lock | CID={cid}\n")

        return cid
