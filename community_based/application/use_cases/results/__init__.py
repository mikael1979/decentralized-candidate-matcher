"""
Results for use cases
"""

class SyncQuestionsResult:
    def __init__(self, success: bool, synced_count: int, message: str, remaining_count: int = 0):
        self.success = success
        self.synced_count = synced_count
        self.message = message
        self.remaining_count = remaining_count

class ProcessRatingResult:
    def __init__(self, success: bool, changes: dict = None, message: str = ""):
        self.success = success
        self.changes = changes or {}
        self.message = message

__all__ = [
    "SyncQuestionsResult",
    "ProcessRatingResult"
]
