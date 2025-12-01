"""
Answers CLI package - modulaarinen versio.
"""
import sys
from pathlib import Path

# Yritä importata suhteellisesti
try:
    from .managers import AnswerManager
    from .models import Answer, AnswerCollection
    
    __all__ = [
        'AnswerManager',
        'Answer',
        'AnswerCollection'
    ]
    
except ImportError as e:
    # Fallback: yritä absoluuttisesti
    try:
        from src.cli.answers.managers import AnswerManager
        from src.cli.answers.models import Answer, AnswerCollection
        
        __all__ = [
            'AnswerManager',
            'Answer',
            'AnswerCollection'
        ]
    except ImportError:
        __all__ = []
