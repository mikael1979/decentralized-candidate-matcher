"""
Commands for use cases - TÄYDELLINEN VERSIO
"""

from application.commands.commands import (
    SubmitQuestionCommand,
    SyncQuestionsCommand,
    ProcessComparisonCommand,
    ProcessVoteCommand
)

# Jos jotain komentoja puuttuu, luo placeholderit
try:
    from application.commands.commands import ProcessComparisonCommand
except ImportError:
    class ProcessComparisonCommand:
        def __init__(self, question_a_id: str, question_b_id: str, result: str, user_id: str):
            self.question_a_id = question_a_id
            self.question_b_id = question_b_id
            self.result = result
            self.user_id = user_id

try:
    from application.commands.commands import ProcessVoteCommand
except ImportError:
    class ProcessVoteCommand:
        def __init__(self, question_id: str, vote_type: str, user_id: str, confidence: int = 1):
            self.question_id = question_id
            self.vote_type = vote_type
            self.user_id = user_id
            self.confidence = confidence

__all__ = [
    "SubmitQuestionCommand",
    "SyncQuestionsCommand", 
    "ProcessComparisonCommand",
    "ProcessVoteCommand"
]
