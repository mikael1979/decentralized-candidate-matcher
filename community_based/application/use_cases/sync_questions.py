#!/usr/bin/env python3
"""
Sync Questions Use Case - Handles question synchronization between storage levels
"""

from typing import List
from datetime import datetime

from domain.entities.question import Question
from domain.repositories.question_repository import QuestionRepository
from domain.value_objects import ActiveQuestionRules
from ..commands import SyncQuestionsCommand
from ..results import SyncQuestionsResult

class SyncQuestionsUseCase:
    """Handles synchronization of questions between storage levels"""
    
    def __init__(
        self,
        question_repository: QuestionRepository,
        config: Optional[dict] = None
    ):
        self.question_repo = question_repository
        self.config = config or {
            "batch_size": 5,
            "max_batch_size": 20,
            "active_question_rules": {
                "min_rating": 800,
                "min_comparisons": 5,
                "min_votes": 3,
                "max_questions": 15
            }
        }
    
    def execute(self, command: SyncQuestionsCommand) -> SyncQuestionsResult:
        """Execute the sync questions use case"""
        try:
            if command.sync_type == "tmp_to_new":
                return self._sync_tmp_to_new(command)
            elif command.sync_type == "new_to_main":
                return self._sync_new_to_main(command)
            elif command.sync_type == "update_active":
                return self._update_active_questions(command)
            else:
                return SyncQuestionsResult.error_result(
                    f"Unknown sync type: {command.sync_type}"
                )
                
        except Exception as e:
            return SyncQuestionsResult.error_result(
                f"Sync failed: {str(e)}",
                data={"error_details": str(e)}
            )
    
    def _sync_tmp_to_new(self, command: SyncQuestionsCommand) -> SyncQuestionsResult:
        """Sync from temporary to new questions"""
        # 1. Get temporary questions
        tmp_questions = self.question_repo.find_temporary_questions()
        
        if not tmp_questions:
            return SyncQuestionsResult.success_result(
                "No questions to sync",
                data={"synced_count": 0, "remaining_count": 0}
            )
        
        # 2. Determine batch size
        batch_size = self._determine_batch_size(command, len(tmp_questions))
        
        # 3. Process batch
        questions_to_sync = tmp_questions[:batch_size]
        
        for question in questions_to_sync:
            # Update question status
            question.metadata["status"] = "approved"
            question.metadata["approved_at"] = datetime.now().isoformat()
            
            # Save to new questions storage
            self.question_repo.save_new(question)
            
            # Remove from temporary storage
            self.question_repo.remove_temporary(question.id)
        
        # 4. Return result
        remaining = len(tmp_questions) - batch_size
        
        return SyncQuestionsResult.success_result(
            f"Synced {batch_size} questions from temporary to new storage",
            data={
                "synced_count": batch_size,
                "remaining_count": remaining,
                "sync_type": "tmp_to_new",
                "batch_id": f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
        )
    
    def _sync_new_to_main(self, command: SyncQuestionsCommand) -> SyncQuestionsResult:
        """Sync from new to main questions storage"""
        new_questions = self.question_repo.find_new_questions()
        
        if not new_questions:
            return SyncQuestionsResult.success_result(
                "No questions to sync",
                data={"synced_count": 0}
            )
        
        # Move all new questions to main storage
        for question in new_questions:
            # In real implementation, this would involve IPFS integration
            # For now, we'll just update the storage location
            self.question_repo.remove_new(question.id)
            # Note: In full implementation, we'd have a separate main storage
        
        return SyncQuestionsResult.success_result(
            f"Synced {len(new_questions)} questions from new to main storage",
            data={
                "synced_count": len(new_questions),
                "sync_type": "new_to_main"
            }
        )
    
    def _update_active_questions(self, command: SyncQuestionsCommand) -> SyncQuestionsResult:
        """Update active questions based on current ratings"""
        # 1. Get all questions (simplified - in real impl, from main storage)
        all_questions = self.question_repo.find_new_questions()  # Temporary source
        
        # 2. Create active question rules
        rules_config = self.config["active_question_rules"]
        rules = ActiveQuestionRules(
            min_rating=rules_config["min_rating"],
            min_comparisons=rules_config["min_comparisons"],
            min_votes=rules_config["min_votes"],
            max_questions=rules_config["max_questions"]
        )
        
        # 3. Filter and sort questions
        eligible_questions = [
            q for q in all_questions 
            if q.is_eligible_for_active(rules)
        ]
        
        # Sort by rating (descending)
        sorted_questions = sorted(
            eligible_questions,
            key=lambda q: q.rating.value,
            reverse=True
        )
        
        # 4. Take top questions
        active_questions = sorted_questions[:rules.max_questions]
        
        # 5. Update active questions storage
        for question in active_questions:
            self.question_repo.save_active(question)
        
        return SyncQuestionsResult.success_result(
            f"Updated active questions: {len(active_questions)} questions",
            data={
                "synced_count": len(active_questions),
                "total_eligible": len(eligible_questions),
                "sync_type": "update_active",
                "active_rules": {
                    "min_rating": rules.min_rating,
                    "min_comparisons": rules.min_comparisons,
                    "min_votes": rules.min_votes,
                    "max_questions": rules.max_questions
                }
            }
        )
    
    def _determine_batch_size(self, command: SyncQuestionsCommand, available_count: int) -> int:
        """Determine appropriate batch size for sync"""
        if command.force:
            return available_count
        
        if command.batch_size:
            return min(command.batch_size, available_count)
        
        return min(self.config["batch_size"], available_count)
