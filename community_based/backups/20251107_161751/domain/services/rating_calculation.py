#!/usr/bin/env python3
"""
Rating Calculation Service - Pure domain logic for ELO calculations
"""

from dataclasses import dataclass
from typing import Tuple
from ..value_objects import Rating, ComparisonResult, UserTrustLevel
from ..entities.question import Question

@dataclass
class RatingChange:
    question_a_change: int
    question_b_change: int
    details: dict

class RatingCalculationService:
    """Domain service for calculating rating changes"""
    
    def __init__(self, config: dict = None):
        self.config = config or {
            "base_k_factor": 32,
            "trust_multipliers": {
                "new_user": 0.5,
                "regular_user": 1.0,
                "trusted_user": 1.2,
                "validator": 1.5
            },
            "protection_hours": 1,
            "min_comparisons": 0
        }
    
    def calculate_comparison_rating(
        self,
        question_a: Question,
        question_b: Question,
        result: ComparisonResult,
        user_trust: UserTrustLevel
    ) -> RatingChange:
        """Calculate rating changes for a comparison"""
        
        # Get K-factor based on user trust
        k_factor = self._get_k_factor(user_trust)
        
        # Calculate expected scores
        expected_a = self._calculate_expected_score(
            question_a.rating.value, 
            question_b.rating.value
        )
        expected_b = self._calculate_expected_score(
            question_b.rating.value, 
            question_a.rating.value
        )
        
        # Get actual scores based on result
        actual_a, actual_b = self._get_actual_scores(result)
        
        # Calculate changes
        change_a = int(k_factor * (actual_a - expected_a))
        change_b = int(k_factor * (actual_b - expected_b))
        
        # Apply protection for new questions
        change_a = self._apply_protection(question_a, change_a)
        change_b = self._apply_protection(question_b, change_b)
        
        return RatingChange(
            question_a_change=change_a,
            question_b_change=change_b,
            details={
                "expected_a": expected_a,
                "expected_b": expected_b,
                "actual_a": actual_a,
                "actual_b": actual_b,
                "k_factor": k_factor,
                "user_trust": user_trust.value
            }
        )
    
    def calculate_vote_impact(
        self,
        question: Question,
        vote_type: str,
        confidence: int,
        user_trust: UserTrustLevel
    ) -> int:
        """Calculate rating impact for a vote"""
        
        if vote_type not in ["upvote", "downvote"]:
            raise ValueError("Vote type must be 'upvote' or 'downvote'")
        
        if not 1 <= confidence <= 5:
            raise ValueError("Confidence must be between 1 and 5")
        
        # Base impact
        base_impact = 1 if vote_type == "upvote" else -1
        
        # Confidence multiplier
        confidence_multipliers = {1: 0.5, 2: 0.75, 3: 1.0, 4: 1.25, 5: 1.5}
        confidence_multiplier = confidence_multipliers.get(confidence, 1.0)
        
        # Trust multiplier
        trust_multiplier = self.config["trust_multipliers"][user_trust.value]
        
        # Calculate total impact
        total_impact = base_impact * confidence_multiplier * trust_multiplier
        
        # Apply protection and round
        protected_impact = self._apply_protection(question, total_impact)
        
        return int(protected_impact)
    
    def _calculate_expected_score(self, rating_a: float, rating_b: float) -> float:
        """Calculate expected score using ELO formula"""
        return 1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / 400.0))
    
    def _get_actual_scores(self, result: ComparisonResult) -> Tuple[float, float]:
        """Get actual scores based on comparison result"""
        if result == ComparisonResult.A_WINS:
            return 1.0, 0.0
        elif result == ComparisonResult.B_WINS:
            return 0.0, 1.0
        else:  # TIE
            return 0.5, 0.5
    
    def _get_k_factor(self, user_trust: UserTrustLevel) -> float:
        """Get K-factor based on user trust level"""
        base_k = self.config["base_k_factor"]
        trust_multiplier = self.config["trust_multipliers"][user_trust.value]
        return base_k * trust_multiplier
    
    def _apply_protection(self, question: Question, change: float) -> int:
        """Apply protection mechanisms for new questions"""
        # Simplified protection - in real implementation, check question age
        # For now, just ensure change is not too large
        max_change = 50
        constrained_change = max(min(change, max_change), -max_change)
        
        return int(constrained_change)
