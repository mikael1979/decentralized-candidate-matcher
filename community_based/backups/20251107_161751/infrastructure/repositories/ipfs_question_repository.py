#!/usr/bin/env python3
"""
IPFS Question Repository - IPFS-based implementation of question repository
"""

from typing import List, Optional
from domain.repositories.question_repository import QuestionRepository
from domain.entities.question import Question
from domain.value_objects import QuestionId, CID

class IPFSQuestionRepository(QuestionRepository):
    """IPFS-based implementation of QuestionRepository"""
    
    def __init__(self, ipfs_client, block_manager, namespace: str = "default"):
        self.ipfs = ipfs_client
        self.block_manager = block_manager
        self.namespace = namespace
        
        # Define block names for different storage levels
        self.tmp_block = "active"  # Temporary storage uses active block
        self.new_block = "sync"    # New questions use sync block
        self.active_block = "urgent"  # Active questions use urgent block
    
    def save_temporary(self, question: Question) -> None:
        """Save question to temporary storage in IPFS"""
        question_data = question.to_dict()
        entry_id = self.block_manager.write_to_block(
            self.tmp_block, question_data, "question_temporary", "normal"
        )
        
        # Store entry ID in question metadata for later retrieval
        question.metadata["ipfs_entry_id"] = entry_id
    
    def save_new(self, question: Question) -> None:
        """Save question to new questions storage in IPFS"""
        question_data = question.to_dict()
        entry_id = self.block_manager.write_to_block(
            self.new_block, question_data, "question_new", "normal"
        )
        
        question.metadata["ipfs_entry_id"] = entry_id
    
    def save_active(self, question: Question) -> None:
        """Save question to active questions storage in IPFS"""
        question_data = question.to_dict()
        entry_id = self.block_manager.write_to_block(
            self.active_block, question_data, "question_active", "high"
        )
        
        question.metadata["ipfs_entry_id"] = entry_id
    
    def find_by_id(self, question_id: QuestionId) -> Optional[Question]:
        """Find question by ID in IPFS blocks"""
        # Search in all blocks
        blocks_to_search = [self.tmp_block, self.new_block, self.active_block]
        
        for block_name in blocks_to_search:
            entries = self.block_manager.read_from_block(block_name)
            
            for entry in entries:
                if entry.get("data_type", "").startswith("question_"):
                    question_data = entry["data"]
                    if question_data.get("local_id") == question_id.value:
                        return Question.from_dict(question_data)
        
        return None
    
    def find_temporary_questions(self) -> List[Question]:
        """Get all temporary questions from IPFS"""
        return self._load_questions_from_block(self.tmp_block, "question_temporary")
    
    def find_new_questions(self) -> List[Question]:
        """Get all new questions from IPFS"""
        return self._load_questions_from_block(self.new_block, "question_new")
    
    def find_active_questions(self, limit: Optional[int] = None) -> List[Question]:
        """Get active questions from IPFS, optionally limited"""
        questions = self._load_questions_from_block(self.active_block, "question_active")
        
        # Sort by rating (descending)
        questions.sort(key=lambda q: q.rating.value, reverse=True)
        
        if limit:
            return questions[:limit]
        
        return questions
    
    def _load_questions_from_block(self, block_name: str, data_type_filter: str) -> List[Question]:
        """Load questions from a specific IPFS block"""
        entries = self.block_manager.read_from_block(block_name)
        questions = []
        
        for entry in entries:
            if entry.get("data_type") == data_type_filter:
                try:
                    question_data = entry["data"]
                    question = Question.from_dict(question_data)
                    questions.append(question)
                except Exception as e:
                    print(f"Warning: Could not load question from IPFS block {block_name}: {e}")
                    continue
        
        return questions
    
    def remove_temporary(self, question_id: QuestionId) -> bool:
        """Remove question from temporary storage in IPFS"""
        # Note: IPFS is immutable, so we can't actually remove entries
        # Instead, we mark them as removed in metadata
        question = self.find_by_id(question_id)
        if question and question.metadata.get("ipfs_entry_id"):
            question.metadata["removed"] = True
            question.metadata["removed_at"] = datetime.now().isoformat()
            
            # Save updated question (this creates a new IPFS entry)
            self.save_temporary(question)
            return True
        
        return False
    
    def remove_new(self, question_id: QuestionId) -> bool:
        """Remove question from new questions storage in IPFS"""
        question = self.find_by_id(question_id)
        if question and question.metadata.get("ipfs_entry_id"):
            question.metadata["removed"] = True
            question.metadata["removed_at"] = datetime.now().isoformat()
            
            self.save_new(question)
            return True
        
        return False
    
    def update_rating(self, question_id: QuestionId, new_rating: int) -> bool:
        """Update question rating in IPFS"""
        question = self.find_by_id(question_id)
        if not question:
            return False
        
        # Calculate delta and update
        delta = new_rating - question.rating.value
        question.update_rating(delta, "manual_update")
        
        # Save updated question based on current storage
        if self._question_in_block(question_id, self.tmp_block):
            self.save_temporary(question)
        elif self._question_in_block(question_id, self.new_block):
            self.save_new(question)
        elif self._question_in_block(question_id, self.active_block):
            self.save_active(question)
        
        return True
    
    def _question_in_block(self, question_id: QuestionId, block_name: str) -> bool:
        """Check if question exists in specific block"""
        questions = self._load_questions_from_block(block_name, f"question_{block_name}")
        return any(q.id.value == question_id.value for q in questions)
    
    def get_question_stats(self) -> dict:
        """Get repository statistics from IPFS"""
        tmp_questions = self.find_temporary_questions()
        new_questions = self.find_new_questions()
        active_questions = self.find_active_questions()
        
        all_questions = tmp_questions + new_questions + active_questions
        
        if not all_questions:
            return {
                "total_questions": 0,
                "average_rating": 0,
                "storage_type": "ipfs"
            }
        
        total_rating = sum(q.rating.value for q in all_questions)
        average_rating = total_rating / len(all_questions)
        
        return {
            "total_questions": len(all_questions),
            "average_rating": round(average_rating, 2),
            "storage_type": "ipfs",
            "tmp_questions": len(tmp_questions),
            "new_questions": len(new_questions),
            "active_questions": len(active_questions),
            "namespace": self.namespace
        }
