# complete_elo_calculator.py
#!/usr/bin/env python3
"""
Complete ELO Calculator - Yksinkertainen versio demoja varten
"""

from enum import Enum

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

class CompleteELOCalculator:
    """Yksinkertainen ELO-laskin demoja varten"""
    
    def process_comparison(self, question_a, question_b, result, user_trust):
        """Käsittele kysymysvertailu"""
        print(f"🔀 Vertailu: {question_a.get('local_id', 'A')} vs {question_b.get('local_id', 'B')} - {result.value}")
        
        # Yksinkertainen ELO-laskenta
        rating_a = question_a.get('elo_rating', {}).get('current_rating', 1000)
        rating_b = question_b.get('elo_rating', {}).get('current_rating', 1000)
        
        if result == ComparisonResult.A_WINS:
            change = 16
            new_rating_a = rating_a + change
            new_rating_b = rating_b - change
        elif result == ComparisonResult.B_WINS:
            change = 16
            new_rating_a = rating_a - change
            new_rating_b = rating_b + change
        else:  # TIE
            change = 8
            new_rating_a = rating_a + change
            new_rating_b = rating_b + change
        
        return {
            "success": True,
            "changes": {
                "question_a": {"change": change, "new_rating": new_rating_a},
                "question_b": {"change": -change if result == ComparisonResult.B_WINS else change, "new_rating": new_rating_b}
            }
        }
    
    def process_vote(self, question, vote_type, confidence, user_trust):
        """Käsittele ääni"""
        print(f"🗳️ Ääni: {vote_type.value} kysymykselle {question.get('local_id', 'unknown')}")
        
        current_rating = question.get('elo_rating', {}).get('current_rating', 1000)
        
        if vote_type == VoteType.UPVOTE:
            change = 5 * confidence
            new_rating = current_rating + change
        else:  # DOWNVOTE
            change = -5 * confidence
            new_rating = current_rating + change
        
        return {
            "success": True,
            "change": {"change": change, "new_rating": new_rating}
        }
