# data_manager.py
import os
from typing import Optional, List, Dict, Any

from utils import ConfigLoader

# Palvelut
from services.content_service import ContentService
from services.meta_service import MetaService
from services.election_policy import ElectionPolicy
from services.ipfs_sync import (
    queue_for_ipfs_sync,
    process_ipfs_sync,
    fetch_questions_from_ipfs
)
from services.security import update_system_chain_ipfs
from services.election_locker import lock_election_content


class DataManager:
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.data_dir = 'data'
        self.config_loader = ConfigLoader()

        # Alusta palvelut
        self.content_service = ContentService(data_dir=self.data_dir, debug=self.debug)
        self.meta_service = MetaService(data_dir=self.data_dir, debug=self.debug)
        self.election_policy = ElectionPolicy(data_dir=self.data_dir, debug=self.debug)

        self.ipfs_client = None

    def set_ipfs_client(self, ipfs_client):
        self.ipfs_client = ipfs_client
        if self.debug:
            print("✅ IPFS-asiakas asetettu DataManagerille")

    def ensure_directories(self):
        directories = ['data', 'templates', 'static', 'config', 'keys']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            if self.debug:
                print(f"📁 Kansio varmistettu: {directory}")

    # --- Sisältöpalvelut ---
    def get_questions(self, include_blocked: bool = False, include_ipfs: bool = True):
        return self.content_service.get_questions(include_blocked, include_ipfs)

    def get_candidates(self):
        return self.content_service.get_candidates()

    def get_comments(self):
        return self.content_service.get_comments()

    def add_question(self, question_data: Dict) -> Optional[str]:
        allowed = self.election_policy.is_content_editing_allowed()
        cid = self.content_service.add_question(question_data, allowed)
        if cid:
            self.get_meta()
            self.queue_for_ipfs_sync(question_data['id'])
        return cid

    def add_candidate(self, candidate_data: Dict) -> Optional[int]:
        allowed = self.election_policy.is_content_editing_allowed()
        candidate_id = self.content_service.add_candidate(candidate_data, allowed)
        if candidate_id:
            self.get_meta()
        return candidate_id

    def block_question(self, question_id: int, reason: Optional[str] = None) -> bool:
        allowed = self.election_policy.is_content_editing_allowed()
        success = self.content_service.block_question(question_id, reason, allowed)
        if success:
            self.get_meta()
        return success

    def apply_elo_delta(self, question_id: int, delta: float, user_id: str) -> bool:
        allowed = self.election_policy.is_content_editing_allowed()
        updated = self.content_service.apply_elo_delta(question_id, delta, user_id, allowed)
        if updated:
            self.queue_for_ipfs_sync(question_id)
        return updated

    # --- Metapalvelut ---
    def get_meta(self) -> Dict:
        return self.meta_service.get_meta(self.content_service)

    def update_meta(self, new_meta: Dict) -> bool:
        return self.meta_service.update_meta(new_meta)

    # --- IPFS-palvelut ---
    def queue_for_ipfs_sync(self, question_id: int) -> bool:
        if not self.ipfs_client:
            return False
        return queue_for_ipfs_sync(
            data_dir=self.data_dir,
            question_id=question_id,
            content_service=self.content_service,
            debug=self.debug
        )

    def process_ipfs_sync(self) -> bool:
        if not self.ipfs_client:
            return False
        return process_ipfs_sync(
            data_dir=self.data_dir,
            ipfs_client=self.ipfs_client,
            meta_service=self.meta_service,
            content_service=self.content_service,
            debug=self.debug
        )

    def fetch_questions_from_ipfs(self) -> bool:
        if not self.ipfs_client:
            return False
        return fetch_questions_from_ipfs(
            data_dir=self.data_dir,
            ipfs_client=self.ipfs_client,
            debug=self.debug
        )

    # --- Turvallisuuspalvelut ---
    def update_system_chain_ipfs(self, modified_files: List[str], ipfs_cids: Optional[Dict] = None) -> bool:
        return update_system_chain_ipfs(
            data_dir=self.data_dir,
            modified_files=modified_files,
            ipfs_cids=ipfs_cids or {},
            debug=self.debug
        )

    def lock_election_content(self) -> str:
        if not self.ipfs_client:
            raise RuntimeError("IPFS-asiakas vaaditaan")
        return lock_election_content(
            data_dir=self.data_dir,
            ipfs_client=self.ipfs_client,
            content_service=self.content_service,
            meta_service=self.meta_service,
            debug=self.debug
        )

    # --- Muita palveluita ---
    def get_admins(self) -> Dict:
        return self.config_loader.load_config('admins.json') or {}
