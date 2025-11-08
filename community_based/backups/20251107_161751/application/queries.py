#!/usr/bin/env python3
"""
Application Queries - Request models for data queries
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

from domain.value_objects import UserId

@dataclass
class GetQuestionStatusQuery:
    """Query to get question pipeline status"""
    election_id: Optional[str] = None
    include_stats: bool = True

@dataclass
class GetActiveQuestionsQuery:
    """Query to get active questions"""
    election_id: str
    limit: Optional[int] = None
    min_rating: Optional[int] = None
    include_content: bool = True

@dataclass
class GetQuestionStatsQuery:
    """Query to get question statistics"""
    question_id: str
    include_rating_history: bool = False

@dataclass
class GetElectionInfoQuery:
    """Query to get election information"""
    election_id: str
    include_phases: bool = True
    include_config: bool = False

@dataclass
class GetSystemStatusQuery:
    """Query to get system status"""
    include_ipfs_status: bool = True
    include_recovery_status: bool = False
    include_node_info: bool = True

@dataclass
class FindQuestionsQuery:
    """Query to find questions based on criteria"""
    election_id: str
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    min_rating: Optional[int] = None
    max_rating: Optional[int] = None
    limit: Optional[int] = 50
    offset: Optional[int] = 0
