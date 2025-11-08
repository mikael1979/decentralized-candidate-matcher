"""
Queries for application - LOPULLINEN VERSIO
"""

# Kaikki queryt
class GetQuestionStatusQuery:
    def __init__(self, question_id: str = None, user_id: str = None):
        self.question_id = question_id
        self.user_id = user_id

class ListQuestionsQuery:
    def __init__(self, limit: int = 10, category: str = None, user_id: str = None):
        self.limit = limit
        self.category = category
        self.user_id = user_id

class GetSyncStatusQuery:
    def __init__(self, detailed: bool = False):
        self.detailed = detailed

class GetActiveQuestionsQuery:
    def __init__(self, limit: int = 15, user_id: str = None):
        self.limit = limit
        self.user_id = user_id

class GetQuestionStatsQuery:
    def __init__(self, question_id: str = None, user_id: str = None):
        self.question_id = question_id
        self.user_id = user_id

class FindQuestionsQuery:
    def __init__(self, search_term: str = None, category: str = None, user_id: str = None):
        self.search_term = search_term
        self.category = category
        self.user_id = user_id

class GetSystemStatusQuery:
    def __init__(self, detailed: bool = False):
        self.detailed = detailed

# Kaikki result-luokat
class QuestionListResult:
    def __init__(self, questions=None, total_count=0, sources=None):
        self.questions = questions or []
        self.total_count = total_count
        self.sources = sources or {}

class QuestionStatusResult:
    def __init__(self, question_id=None, status=None, details=None):
        self.question_id = question_id
        self.status = status
        self.details = details or {}

class SyncStatusResult:
    def __init__(self, tmp_questions_count=0, new_questions_count=0, main_questions_count=0):
        self.tmp_questions_count = tmp_questions_count
        self.new_questions_count = new_questions_count
        self.main_questions_count = main_questions_count

class SystemStatusResult:
    def __init__(self, status=None, details=None):
        self.status = status
        self.details = details or {}

class QuestionStatsResult:
    def __init__(self, question_id=None, stats=None):
        self.question_id = question_id
        self.stats = stats or {}

class ActiveQuestionsResult:
    def __init__(self, questions=None, total_count=0):
        self.questions = questions or []
        self.total_count = total_count

__all__ = [
    "GetQuestionStatusQuery",
    "ListQuestionsQuery", 
    "GetSyncStatusQuery",
    "GetActiveQuestionsQuery",
    "GetQuestionStatsQuery",
    "FindQuestionsQuery",
    "GetSystemStatusQuery",
    "QuestionListResult",
    "QuestionStatusResult", 
    "SyncStatusResult",
    "SystemStatusResult",
    "QuestionStatsResult",
    "ActiveQuestionsResult"
]

# Yleinen QueryResult -luokka
class QueryResult:
    def __init__(self, success=True, data=None, error=None, message=None):
        self.success = success
        self.data = data
        self.error = error
        self.message = message

    def to_dict(self):
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "message": self.message
        }

__all__ = [
    "GetQuestionStatusQuery",
    "ListQuestionsQuery", 
    "GetSyncStatusQuery",
    "GetActiveQuestionsQuery",
    "GetQuestionStatsQuery",
    "FindQuestionsQuery",
    "GetSystemStatusQuery",
    "QuestionListResult",
    "QuestionStatusResult", 
    "SyncStatusResult",
    "SystemStatusResult",
    "QuestionStatsResult",
    "ActiveQuestionsResult",
    "QueryResult"  # LISÄTTY
]
