#!/usr/bin/env python3
"""
Question Service - Facade for question-related operations
"""

from typing import Optional
from domain.repositories.question_repository import QuestionRepository
from domain.services.rating_calculation import RatingCalculationService
from .use_cases.submit_question import SubmitQuestionUseCase
from .use_cases.sync_questions import SyncQuestionsUseCase
from .use_cases.process_rating import ProcessRatingUseCase
from .query_handlers.question_queries import QuestionQueryHandlers
from ..commands import (
    SubmitQuestionCommand, SyncQuestionsCommand, 
    ProcessComparisonCommand, ProcessVoteCommand
)
from application.queries import import import import import  (
    GetQuestionStatusQuery, GetActiveQuestionsQuery,
    GetQuestionStatsQuery, FindQuestionsQuery
)

class QuestionService:
    """Facade service for question-related operations"""
    
    def __init__(
        self,
        question_repository: QuestionRepository,
        rating_service: RatingCalculationService,
        config: Optional[dict] = None
    ):
        self.question_repo = question_repository
        self.rating_service = rating_service
        
        # Initialize use cases
        self.submit_use_case = SubmitQuestionUseCase(question_repository, rating_service, config)
        self.sync_use_case = SyncQuestionsUseCase(question_repository, config)
        self.rating_use_case = ProcessRatingUseCase(question_repository, rating_service)
        self.query_handlers = QuestionQueryHandlers(question_repository)
    
    def submit_question(self, command: SubmitQuestionCommand):
        """Submit a new question"""
        return self.submit_use_case.execute(command)
    
    def sync_questions(self, command: SyncQuestionsCommand):
        """Sync questions between storage levels"""
        return self.sync_use_case.execute(command)
    
    def process_comparison(self, command: ProcessComparisonCommand):
        """Process a question comparison"""
        return self.rating_use_case.process_comparison(command)
    
    def process_vote(self, command: ProcessVoteCommand):
        """Process a vote on a question"""
        return self.rating_use_case.process_vote(command)
    
    def get_question_status(self, query: GetQuestionStatusQuery):
        """Get question pipeline status"""
        return self.query_handlers.get_question_status(query)
    
    def get_active_questions(self, query: GetActiveQuestionsQuery):
        """Get active questions"""
        return self.query_handlers.get_active_questions(query)
    
    def get_question_stats(self, query: GetQuestionStatsQuery):
        """Get question statistics"""
        return self.query_handlers.get_question_stats(query)
    
    def find_questions(self, query: FindQuestionsQuery):
        """Find questions based on criteria"""
        return self.query_handlers.find_questions(query)
    
    def get_system_status(self) -> dict:
        """Get comprehensive system status"""
        status_query = GetQuestionStatusQuery(include_stats=True)
        status_result = self.get_question_status(status_query)
        
        return {
            "question_system": status_result.data if status_result.success else {},
            "repository_stats": self.question_repo.get_question_stats(),
            "timestamp": status_result.timestamp.isoformat()
        }
