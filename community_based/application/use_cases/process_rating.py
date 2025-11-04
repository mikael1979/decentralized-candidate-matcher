#!/usr/bin/env python3
"""
Process Rating Use Case - Handles question comparisons and votes
"""

from domain.repositories.question_repository import QuestionRepository
from domain.services.rating_calculation import RatingCalculationService
from domain.value_objects import QuestionId, ComparisonResult, UserTrustLevel
from ..commands import ProcessComparisonCommand, ProcessVoteCommand
from ..results import RatingChangeResult, CommandResult

class ProcessRatingUseCase:
    """Handles rating operations (comparisons and votes)"""
    
    def __init__(
        self,
        question_repository: QuestionRepository,
        rating_service: RatingCalculationService
    ):
        self.question_repo = question_repository
        self.rating_service = rating_service
    
    def process_comparison(self, command: ProcessComparisonCommand) -> RatingChangeResult:
        """Process a question comparison"""
        try:
            # 1. Find questions
            question_a = self.question_repo.find_by_id(QuestionId(command.question_a_id))
            question_b = self.question_repo.find_by_id(QuestionId(command.question_b_id))
            
            if not question_a or not question_b:
                return RatingChangeResult.error_result(
                    "One or both questions not found",
                    data={
                        "question_a_found": question_a is not None,
                        "question_b_found": question_b is not None
                    }
                )
            
            # 2. Convert inputs to domain types
            comparison_result = ComparisonResult(command.result)
            user_trust = UserTrustLevel(command.user_trust)
            
            # 3. Calculate rating changes
            rating_change = self.rating_service.calculate_comparison_rating(
                question_a, question_b, comparison_result, user_trust
            )
            
            # 4. Apply changes to questions
            question_a.update_rating(rating_change.question_a_change, "comparison")
            question_b.update_rating(rating_change.question_b_change, "comparison")
            
            # 5. Save updated questions
            self.question_repo.update_rating(question_a.id, question_a.rating.value)
            self.question_repo.update_rating(question_b.id, question_b.rating.value)
            
            # 6. Return result
            return RatingChangeResult.success_result(
                "Comparison processed successfully",
                data={
                    "question_a_change": rating_change.question_a_change,
                    "question_b_change": rating_change.question_b_change,
                    "new_rating_a": question_a.rating.value,
                    "new_rating_b": question_b.rating.value,
                    "calculation_details": rating_change.details
                }
            )
            
        except Exception as e:
            return RatingChangeResult.error_result(
                f"Comparison processing failed: {str(e)}",
                data={"error_details": str(e)}
            )
    
    def process_vote(self, command: ProcessVoteCommand) -> CommandResult:
        """Process a vote on a question"""
        try:
            # 1. Find question
            question = self.question_repo.find_by_id(QuestionId(command.question_id))
            
            if not question:
                return CommandResult.error_result("Question not found")
            
            # 2. Convert user trust
            user_trust = UserTrustLevel(command.user_trust)
            
            # 3. Calculate vote impact
            impact = self.rating_service.calculate_vote_impact(
                question, command.vote_type, command.confidence, user_trust
            )
            
            # 4. Apply vote to question
            old_rating = question.rating.value
            question.add_vote(command.vote_type, command.confidence)
            
            # 5. Save updated question
            self.question_repo.update_rating(question.id, question.rating.value)
            
            # 6. Return result
            return CommandResult.success_result(
                "Vote processed successfully",
                data={
                    "question_id": command.question_id,
                    "vote_type": command.vote_type,
                    "confidence": command.confidence,
                    "rating_impact": impact,
                    "old_rating": old_rating,
                    "new_rating": question.rating.value,
                    "total_votes": question.vote_count,
                    "up_votes": question.up_votes,
                    "down_votes": question.down_votes
                }
            )
            
        except Exception as e:
            return CommandResult.error_result(
                f"Vote processing failed: {str(e)}",
                data={"error_details": str(e)}
            )
