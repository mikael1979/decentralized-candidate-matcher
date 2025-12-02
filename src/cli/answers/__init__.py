"""
Answers management module for the decentralized candidate matcher.
"""
__version__ = "1.0.0"
__author__ = "Decentralized Candidate Matcher Team"

from .commands import *
from .managers import *
from .models import *

# Re-export common classes/functions for easier access
__all__ = [
    "AnswerManager",
    "add_answer",
    "list_answers",
    "update_answer",
    "remove_answer",
]
