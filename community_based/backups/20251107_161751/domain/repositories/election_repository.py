#!/usr/bin/env python3
"""
Election Repository Interface - Abstraction for election persistence
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.election import Election
from ..value_objects import ElectionId

class ElectionRepository(ABC):
    """Abstract base class for election repositories"""
    
    @abstractmethod
    def save(self, election: Election) -> None:
        """Save election"""
        pass
    
    @abstractmethod
    def find_by_id(self, election_id: ElectionId) -> Optional[Election]:
        """Find election by ID"""
        pass
    
    @abstractmethod
    def find_all(self) -> List[Election]:
        """Get all elections"""
        pass
    
    @abstractmethod
    def find_active(self) -> List[Election]:
        """Get active elections"""
        pass
    
    @abstractmethod
    def update_status(self, election_id: ElectionId, status: str) -> bool:
        """Update election status"""
        pass
    
    @abstractmethod
    def election_exists(self, election_id: ElectionId) -> bool:
        """Check if election exists"""
        pass
