#!/usr/bin/env python3
"""
Domain Events - Events that represent business occurrences
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from .value_objects import QuestionId, UserId

@dataclass
class DomainEvent:
    """Base class for all domain events"""
    occurred_on: datetime
    event_id: str
    
    def __init__(self):
        self.occurred_on = datetime.now()
        self.event_id = f"event_{self.occurred_on.timestamp()}"

@dataclass
class QuestionSubmitted(DomainEvent):
    """Event raised when a new question is submitted"""
    question_id: QuestionId
    submitted_by: UserId
    content_preview: str

@dataclass
class QuestionRated(DomainEvent):
    """Event raised when a question rating changes"""
    question_id: QuestionId
    old_rating: int
    new_rating: int
    change_type: str  # "comparison" or "vote"
    change_amount: int

@dataclass
class QuestionsCompared(DomainEvent):
    """Event raised when two questions are compared"""
    question_a_id: QuestionId
    question_b_id: QuestionId
    result: str
    user_id: UserId
    rating_changes: dict

@dataclass
class VoteCast(DomainEvent):
    """Event raised when a vote is cast"""
    question_id: QuestionId
    user_id: UserId
    vote_type: str
    confidence: int
    rating_change: int

@dataclass
class QuestionSynced(DomainEvent):
    """Event raised when questions are synced between storage levels"""
    sync_type: str  # "tmp_to_new", "new_to_main", "main_to_ipfs"
    question_count: int
    source: str
    destination: str

@dataclass
class ElectionActivated(DomainEvent):
    """Event raised when an election is activated"""
    election_id: str
    activated_by: UserId
    activation_time: datetime

@dataclass
class SystemLocked(DomainEvent):
    """Event raised when system is locked for production"""
    locked_by: UserId
    fingerprint_entry_id: str
    total_modules: int
