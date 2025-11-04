#!/usr/bin/env python3
"""
Application Results - Output models for use cases
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime

@dataclass
class CommandResult:
    """Base result for commands"""
    success: bool
    message: str
    timestamp: datetime
    data: Optional[Dict[str, Any]] = None
    
    @classmethod
    def success_result(cls, message: str, data: Optional[Dict] = None) -> 'CommandResult':
        return cls(
            success=True,
            message=message,
            timestamp=datetime.now(),
            data=data
        )
    
    @classmethod
    def error_result(cls, message: str, data: Optional[Dict] = None) -> 'CommandResult':
        return cls(
            success=False,
            message=message,
            timestamp=datetime.now(),
            data=data
        )

@dataclass
class QueryResult:
    """Base result for queries"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class SubmitQuestionResult(CommandResult):
    """Result for question submission"""
    question_id: Optional[str] = None
    queue_position: Optional[int] = None
    estimated_sync_time: Optional[datetime] = None
    auto_synced: bool = False

@dataclass
class SyncQuestionsResult(CommandResult):
    """Result for question sync"""
    synced_count: int = 0
    remaining_count: int = 0
    sync_type: Optional[str] = None
    batch_id: Optional[str] = None
    reservation_id: Optional[str] = None

@dataclass
class RatingChangeResult(CommandResult):
    """Result for rating changes"""
    question_a_change: Optional[int] = None
    question_b_change: Optional[int] = None
    new_rating_a: Optional[int] = None
    new_rating_b: Optional[int] = None

@dataclass
class SystemStatusResult(QueryResult):
    """Result for system status query"""
    election_status: Optional[Dict] = None
    question_stats: Optional[Dict] = None
    ipfs_status: Optional[Dict] = None
    node_info: Optional[Dict] = None
    integrity_status: Optional[Dict] = None

@dataclass
class QuestionListResult(QueryResult):
    """Result for question list queries"""
    questions: List[Dict] = None
    total_count: int = 0
    filtered_count: int = 0
    pagination: Optional[Dict] = None

@dataclass
class ElectionResult(QueryResult):
    """Result for election queries"""
    election: Optional[Dict] = None
    current_phase: Optional[Dict] = None
    question_count: Optional[int] = None
    candidate_count: Optional[int] = None
