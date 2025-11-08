#!/usr/bin/env python3
"""Placeholder Question Entity"""

class Question:
    @staticmethod
    def create(content, category, scale, submitted_by, tags):
        # Placeholder implementation
        return type('QuestionObj', (), {
            'id': type('QuestionId', (), {'value': 'temp_id'})(),
            'metadata': {}
        })()
