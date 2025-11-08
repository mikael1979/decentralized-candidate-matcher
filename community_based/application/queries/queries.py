"""
Query classes for application - LOPULLINEN VERSIO
"""

class GetQuestionStatusQuery:
    """Query to get question status"""
    
    def __init__(self, question_id: str = None, user_id: str = None):
        self.question_id = question_id
        self.user_id = user_id

class ListQuestionsQuery:
    """Query to list questions"""
    
    def __init__(self, limit: int = 10, category: str = None, user_id: str = None):
        self.limit = limit
        self.category = category
        self.user_id = user_id

class GetSyncStatusQuery:
    """Query to get sync status"""
    
    def __init__(self, detailed: bool = False):
        self.detailed = detailed

class GetActiveQuestionsQuery:
    """Query to get active questions"""
    
    def __init__(self, limit: int = 15, user_id: str = None):
        self.limit = limit
        self.user_id = user_id

class GetQuestionStatsQuery:
    """Query to get question statistics"""
    
    def __init__(self, question_id: str = None, user_id: str = None):
        self.question_id = question_id
        self.user_id = user_id

class FindQuestionsQuery:
    """Query to find questions by search term"""
    
    def __init__(self, search_term: str = None, category: str = None, user_id: str = None):
        self.search_term = search_term
        self.category = category
        self.user_id = user_id
