import os
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Config:
    DATA_DIR: str = "test_data"
    BACKUP_ENABLED: bool = True
    DEFAULT_ELO_RATING: int = 1500
    K_FACTOR: int = 32
    AUTO_BLOCK_THRESHOLD: float = 0.7
    AUTO_BLOCK_MIN_VOTES: int = 10
    COMMUNITY_APPROVAL_THRESHOLD: float = 0.8
    
    DEFAULT_FILES: Dict[str, Any] = None
    
    def __post_init__(self):
        self.DEFAULT_FILES = {
            'meta.json': {
                "system": "Decentralized Candidate Matcher",
                "version": "1.0.0",
                "election": {
                    "id": "test_election_2024",
                    "country": "FI",
                    "type": "test",
                    "name": {"fi": "Test Vaalit 2024", "en": "Test Election 2024"},
                    "date": "2024-01-01",
                    "language": "fi"
                },
                "community_moderation": {
                    "enabled": True,
                    "thresholds": {
                        "auto_block_inappropriate": self.AUTO_BLOCK_THRESHOLD,
                        "auto_block_min_votes": self.AUTO_BLOCK_MIN_VOTES,
                        "community_approval": self.COMMUNITY_APPROVAL_THRESHOLD
                    }
                },
                "admins": [
                    {
                        "admin_id": "admin_1",
                        "public_key": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIadmin1",
                        "name": "Test Admin",
                        "role": "super_admin"
                    }
                ],
                "content": {}
            },
            'questions.json': {
                "election_id": "test_election_2024",
                "language": "fi",
                "questions": []
            },
            'newquestions.json': {
                "election_id": "test_election_2024",
                "language": "fi",
                "question_type": "user_submitted",
                "questions": []
            },
            'candidates.json': {
                "election_id": "test_election_2024",
                "language": "fi",
                "candidates": []
            },
            'community_votes.json': {
                "election_id": "test_election_2024",
                "language": "fi",
                "question_votes": [],
                "user_votes": []
            }
        }

config = Config()
