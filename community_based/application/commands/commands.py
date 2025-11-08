#!/usr/bin/env python3
"""
Application Commands - Input models for use cases
"""

from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime

from domain.value_objects import MultilingualText, Category, Scale, UserId

@dataclass
class SubmitQuestionCommand:
    """Command to submit a new question"""
    content: MultilingualText
    category: Category
    scale: Scale
    submitted_by: UserId
    tags: Optional[List[str]] = None
    metadata: Optional[Dict] = None

@dataclass
class SyncQuestionsCommand:
    """Command to sync questions between storage levels"""
    sync_type: str  # "tmp_to_new", "new_to_main", "main_to_ipfs"
    batch_size: Optional[int] = None
    force: bool = False
    requested_by: Optional[UserId] = None

@dataclass
class ProcessComparisonCommand:
    """Command to process a question comparison"""
    question_a_id: str
    question_b_id: str
    result: str  # "a_wins", "b_wins", "tie"
    user_id: UserId
    user_trust: str  # "new_user", "regular_user", etc.
    metadata: Optional[Dict] = None

@dataclass
class ProcessVoteCommand:
    """Command to process a vote"""
    question_id: str
    vote_type: str  # "upvote", "downvote"
    user_id: UserId
    confidence: int = 3
    user_trust: str = "regular_user"
    metadata: Optional[Dict] = None
