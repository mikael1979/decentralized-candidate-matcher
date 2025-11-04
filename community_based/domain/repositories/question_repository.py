#!/usr/bin/env python3
"""
Question Repository Interface - Abstraction for question persistence
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.question import Question
from ..value_objects import QuestionId

class QuestionRepository(ABC):
    """Abstract base class for question repositories"""
    
    @abstractmethod
    def save_temporary(self, question: Question) -> None:
        """Save question to temporary storage"""
        pass
    
    @abstractmethod
    def save_new(self, question: Question) -> None:
        """Save question to new questions storage"""
        pass
    
    @abstractmethod
    def save_active(self, question: Question) -> None:
        """Save question to active questions storage"""
        pass
    
    @abstractmethod
    def find_by_id(self, question_id: QuestionId) -> Optional[Question]:
        """Find question by ID"""
        pass
    
    @abstractmethod
    def find_temporary_questions(self) -> List[Question]:
        """Get all temporary questions"""
        pass
    
    @abstractmethod
    def find_new_questions(self) -> List[Question]:
        """Get all new questions"""
        pass
    
    @abstractmethod
    def find_active_questions(self, limit: Optional[int] = None) -> List[Question]:
        """Get active questions, optionally limited"""
        pass
    
    @abstractmethod
    def remove_temporary(self, question_id: QuestionId) -> bool:
        """Remove question from temporary storage"""
        pass
    
    @abstractmethod
    def remove_new(self, question_id: QuestionId) -> bool:
        """Remove question from new questions storage"""
        pass
    
    @abstractmethod
    def update_rating(self, question_id: QuestionId, new_rating: int) -> bool:
        """Update question rating"""
        pass
    
    @abstractmethod
    def get_question_stats(self) -> dict:
        """Get repository statistics"""
        pass
