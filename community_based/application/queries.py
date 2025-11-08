# community_based/application/queries.py
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class QuestionListQuery:
    """Query for listing questions"""
    limit: Optional[int] = None
    category: Optional[str] = None

@dataclass
class QuestionListResult:
    """Result for question list query"""
    questions: List[Dict[str, Any]]
    total_count: int
    sources: Dict[str, int]
    success: bool = True

@dataclass
class SyncStatusQuery:
    """Query for sync status"""
    pass

@dataclass
class SyncStatusResult:
    """Result for sync status query"""
    tmp_questions_count: int
    new_questions_count: int
    main_questions_count: int
    auto_sync_enabled: bool
    next_sync_time: Optional[str] = None
    time_until_sync: Optional[str] = None
    batch_size_progress: Optional[str] = None
    success: bool = True

@dataclass
class QuestionByIdQuery:
    """Query for getting a question by ID"""
    question_id: str

@dataclass
class QuestionByIdResult:
    """Result for question by ID query"""
    question: Optional[Dict[str, Any]] = None
    success: bool = True

@dataclass
class GetQuestionStatusQuery:
    """Query for getting question status"""
    question_id: str

@dataclass
class GetQuestionStatusResult:
    """Result for question status query"""
    question_id: str
    current_rating: int
    base_rating: int
    comparison_delta: int
    vote_delta: int
    total_comparisons: int
    total_votes: int
    up_votes: int
    down_votes: int
    content_preview: str
    success: bool = True
