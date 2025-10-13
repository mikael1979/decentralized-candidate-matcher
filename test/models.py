from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import hashlib
import json

class Integrity(BaseModel):
    algorithm: str = "sha256"
    hash: str
    computed: str

class ElectionInfo(BaseModel):
    id: str
    country: str
    type: str
    name: Dict[str, str]
    date: str
    language: str
    available_languages: Optional[List[str]] = None

class Scale(BaseModel):
    min: int
    max: int
    labels: Dict[str, Dict[str, str]]

class EloRating(BaseModel):
    rating: int
    total_matches: int
    wins: int
    losses: int
    last_updated: str
    history: Optional[List[Dict]] = []

class Submission(BaseModel):
    user_public_key: str
    timestamp: str
    status: str
    upvotes: int = 0
    downvotes: int = 0
    user_comment: Optional[str] = None
    signature: Optional[str] = None

class Moderation(BaseModel):
    moderated: bool = False
    approved: Optional[bool] = None
    moderator_comment: Optional[str] = None
    moderator_id: Optional[str] = None
    moderated_at: Optional[str] = None
    blocked: bool = False
    block_reason: Optional[str] = None
    blocked_at: Optional[str] = None
    blocked_by: Optional[str] = None

class CommunityModeration(BaseModel):
    status: str = "pending"
    votes_received: int = 0
    inappropriate_ratio: float = 0.0
    confidence_score: float = 0.0
    community_approved: bool = False
    auto_moderated: bool = False
    requires_admin_review: bool = False
    last_vote_update: Optional[str] = None

class Question(BaseModel):
    id: Union[int, str]
    category: Dict[str, str]
    question: Dict[str, str]
    scale: Scale
    tags: Optional[Dict[str, List[str]]] = None
    elo_rating: Optional[EloRating] = None
    submission: Optional[Submission] = None
    moderation: Optional[Moderation] = None
    community_moderation: Optional[CommunityModeration] = None

class QuestionVote(BaseModel):
    question_id: str
    total_votes: int = 0
    appropriate_votes: int = 0
    inappropriate_votes: int = 0
    inappropriate_ratio: float = 0.0
    confidence_score: float = 0.0
    status: str = "pending"
    auto_moderated: bool = False
    last_updated: str

class UserVote(BaseModel):
    vote_id: str
    question_id: str
    voter_public_key: str
    vote: str  # 'appropriate' or 'inappropriate'
    confidence: float = 0.5
    reasons: List[str] = []
    comments: Optional[str] = None
    timestamp: str
    signature: Optional[str] = None
    voter_trust_score: float = 0.5

class Candidate(BaseModel):
    id: int
    name: str
    party: str
    district: str
    public_key: str
    key_fingerprint: str
    answer_cid: str

class QuestionFile(BaseModel):
    election_id: str
    language: str
    questions: List[Question]
    integrity: Optional[Integrity] = None

class NewQuestionsFile(BaseModel):
    election_id: str
    language: str
    question_type: str = "user_submitted"
    questions: List[Question]
    integrity: Optional[Integrity] = None

class CommunityVotesFile(BaseModel):
    election_id: str
    language: str
    question_votes: List[QuestionVote] = []
    user_votes: List[UserVote] = []
    integrity: Optional[Integrity] = None

class CandidatesFile(BaseModel):
    election_id: str
    language: str
    candidates: List[Candidate]
    integrity: Optional[Integrity] = None

class MetaFile(BaseModel):
    system: str
    version: str
    election: ElectionInfo
    community_moderation: Dict[str, Any]
    admins: List[Dict[str, Any]]
    content: Dict[str, Any]
    integrity: Optional[Integrity] = None
