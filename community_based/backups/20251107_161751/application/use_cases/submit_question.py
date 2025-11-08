#!/usr/bin/env python3
"""
Submit Question Use Case - Handles new question submission
"""

from typing import Optional
from datetime import datetime

from domain.entities.question import Question
from domain.repositories.question_repository import QuestionRepository
from domain.services.rating_calculation import RatingCalculationService
from ..commands import SubmitQuestionCommand
from ..results import SubmitQuestionResult

class SubmitQuestionUseCase:
    """Handles the submission of new questions"""
    
    def __init__(
        self,
        question_repository: QuestionRepository,
        rating_service: RatingCalculationService,
        config: Optional[dict] = None
    ):
        self.question_repo = question_repository
        self.rating_service = rating_service
        self.config = config or {
            "auto_sync_enabled": True,
            "batch_size": 5,
            "max_batch_size": 20
        }
    
    def execute(self, command: SubmitQuestionCommand) -> SubmitQuestionResult:
        """Execute the submit question use case"""
        try:
            # 1. Create new question entity
            question = Question.create(
                content=command.content,
                category=command.category,
                scale=command.scale,
                submitted_by=command.submitted_by.value,
                tags=command.tags
            )
            
            # 2. Add metadata if provided
            if command.metadata:
                question.metadata.update(command.metadata)
            
            # 3. Save to temporary storage
            self.question_repo.save_temporary(question)
            
            # 4. Check if auto-sync should be triggered
            auto_synced = False
            sync_details = None
            
            if self.config["auto_sync_enabled"]:
                tmp_questions = self.question_repo.find_temporary_questions()
                if len(tmp_questions) >= self.config["batch_size"]:
                    # In real implementation, this would trigger sync
                    auto_synced = True
                    sync_details = {
                        "triggered_by": "auto_sync",
                        "batch_size": len(tmp_questions),
                        "threshold": self.config["batch_size"]
                    }
            
            # 5. Prepare result
            queue_position = len(self.question_repo.find_temporary_questions())
            
            return SubmitQuestionResult.success_result(
                message="Question submitted successfully",
                data={
                    "question_id": question.id.value,
                    "queue_position": queue_position,
                    "auto_synced": auto_synced,
                    "sync_details": sync_details,
                    "estimated_sync_time": self._estimate_sync_time(queue_position)
                }
            )
            
        except Exception as e:
            return SubmitQuestionResult.error_result(
                message=f"Failed to submit question: {str(e)}",
                data={"error_details": str(e)}
            )
    
    def _estimate_sync_time(self, queue_position: int) -> Optional[datetime]:
        """Estimate when sync might occur"""
        if queue_position < self.config["batch_size"]:
            return None
        
        batches_needed = (queue_position + 1) // self.config["batch_size"]
        # Simple estimation: 1 hour per batch (could be configurable)
        estimated_hours = batches_needed * 1
        
        from datetime import timedelta
        return datetime.now() + timedelta(hours=estimated_hours)
