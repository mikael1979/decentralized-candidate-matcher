# application/results.py
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class CommandResult:
    """Base class for command results"""
    success: bool
    message: Optional[str] = None

@dataclass
class SubmitQuestionResult(CommandResult):
    """Result for submitting a question"""
    question_id: Optional[str] = None
    queue_position: Optional[int] = None

@dataclass
class SyncQuestionsResult(CommandResult):
    """Result for syncing questions"""
    synced_count: int = 0
    remaining_count: int = 0

@dataclass
class RatingChangeResult(CommandResult):
    """Result for rating changes in ELO comparisons"""
    question_a_change: Optional[int] = None
    question_b_change: Optional[int] = None
    new_rating_a: Optional[int] = None
    new_rating_b: Optional[int] = None

@dataclass
class ProcessRatingResult(CommandResult):
    """Result for processing a rating"""
    change: Optional[int] = None
    new_rating: Optional[int] = None
