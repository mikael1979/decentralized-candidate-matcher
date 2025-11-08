"""
Commands for application - LOPULLINEN VERSIO
"""

# Kaikki command-luokat
class SubmitQuestionCommand:
    def __init__(self, content=None, category="general", scale="agree_disagree", 
                 submitted_by=None, tags=None, metadata=None):
        self.content = content or {}
        self.category = category
        self.scale = scale
        self.submitted_by = submitted_by
        self.tags = tags or []
        self.metadata = metadata or {}

class SyncQuestionsCommand:
    def __init__(self, sync_type="tmp_to_new", force=False, batch_size=None):
        self.sync_type = sync_type
        self.force = force
        self.batch_size = batch_size

class ProcessRatingCommand:
    def __init__(self, question_id=None, rating_data=None, user_id=None):
        self.question_id = question_id
        self.rating_data = rating_data or {}
        self.user_id = user_id

class UpdateQuestionCommand:
    def __init__(self, question_id=None, updates=None, user_id=None):
        self.question_id = question_id
        self.updates = updates or {}
        self.user_id = user_id

class DeleteQuestionCommand:
    def __init__(self, question_id=None, user_id=None):
        self.question_id = question_id
        self.user_id = user_id

class ImportQuestionsCommand:
    def __init__(self, source=None, questions_data=None, user_id=None):
        self.source = source
        self.questions_data = questions_data or []
        self.user_id = user_id

class ExportQuestionsCommand:
    def __init__(self, format="json", include_metadata=True, user_id=None):
        self.format = format
        self.include_metadata = include_metadata
        self.user_id = user_id

__all__ = [
    "SubmitQuestionCommand",
    "SyncQuestionsCommand", 
    "ProcessRatingCommand",
    "UpdateQuestionCommand",
    "DeleteQuestionCommand",
    "ImportQuestionsCommand",
    "ExportQuestionsCommand"
]

class ProcessComparisonCommand:
    def __init__(self, question_a_id=None, question_b_id=None, result=None, 
                 user_id=None, confidence=1.0):
        self.question_a_id = question_a_id
        self.question_b_id = question_b_id
        self.result = result  # 'a_wins', 'b_wins', 'tie'
        self.user_id = user_id
        self.confidence = confidence

class ProcessVoteCommand:
    def __init__(self, question_id=None, vote_type=None, user_id=None, confidence=1.0):
        self.question_id = question_id
        self.vote_type = vote_type  # 'upvote', 'downvote'
        self.user_id = user_id
        self.confidence = confidence

__all__ = [
    "SubmitQuestionCommand",
    "SyncQuestionsCommand", 
    "ProcessRatingCommand",
    "UpdateQuestionCommand",
    "DeleteQuestionCommand",
    "ImportQuestionsCommand",
    "ExportQuestionsCommand",
    "ProcessComparisonCommand",  # LISÄTTY
    "ProcessVoteCommand"         # LISÄTTY
]
