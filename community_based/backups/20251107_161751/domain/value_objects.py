#!/usr/bin/env python3
"""
Domain Value Objects - Immutable data structures
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
from datetime import timezone

# Enums
class VoteType(Enum):
    UPVOTE = "upvote"
    DOWNVOTE = "downvote"

class ComparisonResult(Enum):
    A_WINS = "a_wins"
    B_WINS = "b_wins"
    TIE = "tie"

class UserTrustLevel(Enum):
    NEW_USER = "new_user"
    REGULAR_USER = "regular_user"
    TRUSTED_USER = "trusted_user"
    VALIDATOR = "validator"

class ElectionStatus(Enum):
    DRAFT = "draft"
    UPCOMING = "upcoming"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# Value Objects
@dataclass(frozen=True)
class QuestionId:
    value: str
    
    @classmethod
    def generate(cls) -> 'QuestionId':
        import hashlib
        from datetime import datetime
        hash_input = f"question_{datetime.now().isoformat()}"
        hash_digest = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
        return cls(f"q{hash_digest}")

@dataclass(frozen=True)
class ElectionId:
    value: str

@dataclass(frozen=True)
class UserId:
    value: str

@dataclass(frozen=True)
class CID:
    value: str

@dataclass(frozen=True)
class MultilingualText:
    fi: str
    en: str
    sv: str
    
    def get_text(self, language: str = "fi") -> str:
        return getattr(self, language, self.fi)

@dataclass(frozen=True)
class Scale:
    min: int
    max: int
    labels: Dict[str, Dict[str, str]]  # language -> {min, neutral, max}
    
    def __post_init__(self):
        if self.min >= self.max:
            raise ValueError("Scale min must be less than max")

@dataclass(frozen=True)
class Category:
    name: MultilingualText
    description: Optional[MultilingualText] = None

@dataclass(frozen=True)
class Rating:
    value: int
    comparison_delta: int = 0
    vote_delta: int = 0
    
    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Rating value cannot be negative")
    
    def adjust(self, delta: int) -> 'Rating':
        return Rating(
            value=max(0, self.value + delta),
            comparison_delta=self.comparison_delta,
            vote_delta=self.vote_delta
        )
    
    @property
    def total_delta(self) -> int:
        return self.comparison_delta + self.vote_delta

@dataclass(frozen=True)
class CreationTimestamps:
    created: datetime
    modified: datetime
    
    @classmethod
    def now(cls) -> 'CreationTimestamps':
        now = datetime.now(timezone.utc)
        return cls(created=now, modified=now)
    
    def with_modified_update(self) -> 'CreationTimestamps':
        return CreationTimestamps(
            created=self.created,
            modified=datetime.now(timezone.utc)
        )

@dataclass(frozen=True)
class ActiveQuestionRules:
    min_rating: int
    min_comparisons: int
    min_votes: int
    max_questions: int
    
    def is_satisfied_by(self, question: 'Question') -> bool:
        return (
            question.rating.value >= self.min_rating and
            question.comparison_count >= self.min_comparisons and
            question.vote_count >= self.min_votes
        )
