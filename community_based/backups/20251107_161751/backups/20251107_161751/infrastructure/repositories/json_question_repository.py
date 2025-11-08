#!/usr/bin/env python3
"""
JSON Question Repository - File-based implementation of question repository
"""

import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from domain.repositories.question_repository import QuestionRepository
from domain.entities.question import Question
from domain.value_objects import QuestionId

class JSONQuestionRepository(QuestionRepository):
    """JSON file-based implementation of QuestionRepository"""
    
    def __init__(self, runtime_dir: str = "runtime"):
        self.runtime_dir = Path(runtime_dir)
        self.runtime_dir.mkdir(exist_ok=True)
        
        # Define file paths
        self.tmp_file = self.runtime_dir / "tmp_new_questions.json"
        self.new_file = self.runtime_dir / "new_questions.json"
        self.active_file = self.runtime_dir / "active_questions.json"
        self.questions_file = self.runtime_dir / "questions.json"
        
        # Initialize files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize JSON files with proper structure if they don't exist"""
        files_to_init = [
            (self.tmp_file, "temporary"),
            (self.new_file, "new"),
            (self.active_file, "active"),
            (self.questions_file, "main")
        ]
        
        for file_path, storage_type in files_to_init:
            if not file_path.exists():
                self._create_empty_structure(file_path, storage_type)
    
    def _create_empty_structure(self, file_path: Path, storage_type: str):
        """Create empty JSON structure for a storage file"""
        empty_data = {
            "metadata": {
                "storage_type": storage_type,
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_questions": 0,
                "version": "2.0.0"
            },
            "questions": []
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(empty_data, f, indent=2, ensure_ascii=False)
    
    def _load_questions_from_file(self, file_path: Path) -> List[Question]:
        """Load questions from a JSON file"""
        if not file_path.exists():
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            questions = []
            for question_data in data.get("questions", []):
                try:
                    question = Question.from_dict(question_data)
                    questions.append(question)
                except Exception as e:
                    print(f"Warning: Could not load question from {file_path}: {e}")
                    continue
            
            return questions
            
        except Exception as e:
            print(f"Error loading questions from {file_path}: {e}")
            return []
    
    def _save_questions_to_file(self, file_path: Path, questions: List[Question]):
        """Save questions to a JSON file"""
        try:
            data = {
                "metadata": {
                    "storage_type": file_path.stem,
                    "last_updated": datetime.now().isoformat(),
                    "total_questions": len(questions),
                    "version": "2.0.0"
                },
                "questions": [question.to_dict() for question in questions]
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error saving questions to {file_path}: {e}")
            raise
    
    def save_temporary(self, question: Question) -> None:
        """Save question to temporary storage"""
        questions = self._load_questions_from_file(self.tmp_file)
        questions.append(question)
        self._save_questions_to_file(self.tmp_file, questions)
    
    def save_new(self, question: Question) -> None:
        """Save question to new questions storage"""
        questions = self._load_questions_from_file(self.new_file)
        questions.append(question)
        self._save_questions_to_file(self.new_file, questions)
    
    def save_active(self, question: Question) -> None:
        """Save question to active questions storage"""
        questions = self._load_questions_from_file(self.active_file)
        
        # Remove existing question with same ID if present
        questions = [q for q in questions if q.id.value != question.id.value]
        questions.append(question)
        
        self._save_questions_to_file(self.active_file, questions)
    
    def find_by_id(self, question_id: QuestionId) -> Optional[Question]:
        """Find question by ID across all storage levels"""
        # Search in all storage files
        storage_files = [self.tmp_file, self.new_file, self.active_file, self.questions_file]
        
        for file_path in storage_files:
            questions = self._load_questions_from_file(file_path)
            for question in questions:
                if question.id.value == question_id.value:
                    return question
        
        return None
    
    def find_temporary_questions(self) -> List[Question]:
        """Get all temporary questions"""
        return self._load_questions_from_file(self.tmp_file)
    
    def find_new_questions(self) -> List[Question]:
        """Get all new questions"""
        return self._load_questions_from_file(self.new_file)
    
    def find_active_questions(self, limit: Optional[int] = None) -> List[Question]:
        """Get active questions, optionally limited"""
        questions = self._load_questions_from_file(self.active_file)
        
        # Sort by rating (descending)
        questions.sort(key=lambda q: q.rating.value, reverse=True)
        
        if limit:
            return questions[:limit]
        
        return questions
    
    def remove_temporary(self, question_id: QuestionId) -> bool:
        """Remove question from temporary storage"""
        questions = self._load_questions_from_file(self.tmp_file)
        original_count = len(questions)
        
        questions = [q for q in questions if q.id.value != question_id.value]
        
        if len(questions) < original_count:
            self._save_questions_to_file(self.tmp_file, questions)
            return True
        
        return False
    
    def remove_new(self, question_id: QuestionId) -> bool:
        """Remove question from new questions storage"""
        questions = self._load_questions_from_file(self.new_file)
        original_count = len(questions)
        
        questions = [q for q in questions if q.id.value != question_id.value]
        
        if len(questions) < original_count:
            self._save_questions_to_file(self.new_file, questions)
            return True
        
        return False
    
    def update_rating(self, question_id: QuestionId, new_rating: int) -> bool:
        """Update question rating across all storage levels"""
        updated = False
        
        # Update in all storage files where the question exists
        storage_files = [self.tmp_file, self.new_file, self.active_file, self.questions_file]
        
        for file_path in storage_files:
            questions = self._load_questions_from_file(file_path)
            
            for question in questions:
                if question.id.value == question_id.value:
                    # Calculate delta to maintain comparison/vote deltas
                    delta = new_rating - question.rating.value
                    question.update_rating(delta, "manual_update")
                    updated = True
            
            if any(q.id.value == question_id.value for q in questions):
                self._save_questions_to_file(file_path, questions)
        
        return updated
    
    def get_question_stats(self) -> dict:
        """Get repository statistics"""
        all_questions = []
        storage_files = [self.tmp_file, self.new_file, self.active_file, self.questions_file]
        
        for file_path in storage_files:
            all_questions.extend(self._load_questions_from_file(file_path))
        
        if not all_questions:
            return {
                "total_questions": 0,
                "average_rating": 0,
                "recent_activity": {}
            }
        
        total_rating = sum(q.rating.value for q in all_questions)
        average_rating = total_rating / len(all_questions)
        
        # Calculate recent activity (last 24 hours)
        one_day_ago = datetime.now().timestamp() - 86400
        recent_questions = [
            q for q in all_questions 
            if q.timestamps.modified.timestamp() > one_day_ago
        ]
        
        return {
            "total_questions": len(all_questions),
            "average_rating": round(average_rating, 2),
            "recent_activity": {
                "questions_modified_24h": len(recent_questions),
                "tmp_questions": len(self._load_questions_from_file(self.tmp_file)),
                "new_questions": len(self._load_questions_from_file(self.new_file)),
                "active_questions": len(self._load_questions_from_file(self.active_file))
            }
        }
