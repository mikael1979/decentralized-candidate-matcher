#!/usr/bin/env python3
"""
Question Query Handlers - Handle data queries for questions
"""

from typing import List
from domain.repositories.question_repository import QuestionRepository
from application.queries import import import import import  (
    GetQuestionStatusQuery, GetActiveQuestionsQuery, 
    GetQuestionStatsQuery, FindQuestionsQuery,
    QuestionListResult, SystemStatusResult, QueryResult
)

class QuestionQueryHandlers:
    """Handlers for question-related queries"""
    
    def __init__(self, question_repository: QuestionRepository):
        self.question_repo = question_repository
    
    def get_question_status(self, query: GetQuestionStatusQuery) -> SystemStatusResult:
        """Get question pipeline status"""
        try:
            stats = self.question_repo.get_question_stats()
            
            status_data = {
                "temporary_questions": len(self.question_repo.find_temporary_questions()),
                "new_questions": len(self.question_repo.find_new_questions()),
                "active_questions": len(self.question_repo.find_active_questions()),
                "total_questions": stats.get("total_questions", 0),
                "average_rating": stats.get("average_rating", 0),
                "recent_activity": stats.get("recent_activity", {})
            }
            
            return SystemStatusResult(
                success=True,
                data=status_data
            )
            
        except Exception as e:
            return SystemStatusResult(
                success=False,
                error=str(e)
            )
    
    def get_active_questions(self, query: GetActiveQuestionsQuery) -> QuestionListResult:
        """Get active questions for an election"""
        try:
            active_questions = self.question_repo.find_active_questions(query.limit)
            
            # Apply rating filter if specified
            if query.min_rating is not None:
                active_questions = [
                    q for q in active_questions 
                    if q.rating.value >= query.min_rating
                ]
            
            # Convert to dictionary format
            questions_data = []
            for question in active_questions:
                question_data = question.to_dict()
                
                if not query.include_content:
                    # Remove content to reduce payload size
                    if "content" in question_data:
                        del question_data["content"]
                
                questions_data.append(question_data)
            
            return QuestionListResult(
                success=True,
                data={
                    "questions": questions_data,
                    "total_count": len(questions_data),
                    "filtered_count": len(questions_data),
                    "election_id": query.election_id
                }
            )
            
        except Exception as e:
            return QuestionListResult(
                success=False,
                error=str(e)
            )
    
    def get_question_stats(self, query: GetQuestionStatsQuery) -> QueryResult:
        """Get detailed statistics for a specific question"""
        try:
            question = self.question_repo.find_by_id(query.question_id)
            
            if not question:
                return QueryResult(
                    success=False,
                    error="Question not found"
                )
            
            stats_data = {
                "question_id": question.id.value,
                "current_rating": question.rating.value,
                "comparison_delta": question.rating.comparison_delta,
                "vote_delta": question.rating.vote_delta,
                "total_comparisons": question.comparison_count,
                "total_votes": question.vote_count,
                "up_votes": question.up_votes,
                "down_votes": question.down_votes,
                "content_preview": question.content.fi[:50] + "..." if question.content.fi else "",
                "category": question.category.name.fi,
                "created": question.timestamps.created.isoformat(),
                "last_modified": question.timestamps.modified.isoformat()
            }
            
            if query.include_rating_history:
                # In real implementation, this would fetch from rating history storage
                stats_data["rating_history"] = {
                    "recent_changes": [],
                    "trend": "stable"  # Simplified
                }
            
            return QueryResult(
                success=True,
                data=stats_data
            )
            
        except Exception as e:
            return QueryResult(
                success=False,
                error=str(e)
            )
    
    def find_questions(self, query: FindQuestionsQuery) -> QuestionListResult:
        """Find questions based on search criteria"""
        try:
            # Get all questions (simplified - in real impl, would use proper search)
            all_questions = self.question_repo.find_new_questions()
            
            # Apply filters
            filtered_questions = all_questions
            
            # Filter by categories
            if query.categories:
                filtered_questions = [
                    q for q in filtered_questions
                    if q.category.name.fi in query.categories or 
                       q.category.name.en in query.categories
                ]
            
            # Filter by tags
            if query.tags:
                filtered_questions = [
                    q for q in filtered_questions
                    if any(tag in q.tags for tag in query.tags)
                ]
            
            # Filter by rating range
            if query.min_rating is not None:
                filtered_questions = [
                    q for q in filtered_questions
                    if q.rating.value >= query.min_rating
                ]
            
            if query.max_rating is not None:
                filtered_questions = [
                    q for q in filtered_questions
                    if q.rating.value <= query.max_rating
                ]
            
            # Apply pagination
            start_idx = query.offset or 0
            end_idx = start_idx + (query.limit or 50)
            paginated_questions = filtered_questions[start_idx:end_idx]
            
            # Convert to dictionary
            questions_data = [q.to_dict() for q in paginated_questions]
            
            return QuestionListResult(
                success=True,
                data={
                    "questions": questions_data,
                    "total_count": len(filtered_questions),
                    "filtered_count": len(paginated_questions),
                    "pagination": {
                        "limit": query.limit,
                        "offset": query.offset,
                        "has_more": end_idx < len(filtered_questions)
                    }
                }
            )
            
        except Exception as e:
            return QuestionListResult(
                success=False,
                error=str(e)
            )
