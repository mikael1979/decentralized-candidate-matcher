#!/usr/bin/env python3
"""
Submit Question Use Case - KORJATTU VERSIO
"""

import hashlib
from datetime import datetime
from datetime import timezone
from typing import Dict, Any

class SubmitQuestionCommand:
    def __init__(self, content: Dict, category: str, scale: str, 
                 submitted_by: str, tags: list, metadata: Dict):
        self.content = content
        self.category = category
        self.scale = scale
        self.submitted_by = submitted_by
        self.tags = tags
        self.metadata = metadata

class SubmitQuestionUseCase:
    def __init__(self, question_service):
        self.question_service = question_service
    
    def execute(self, command: SubmitQuestionCommand) -> Dict[str, Any]:
        """KORJATTU: Toteuta oikea logiikka"""
        try:
            # 1. Luo kysymys-ID
            timestamp = datetime.now(timezone.utc).isoformat()
            content_str = str(command.content)
            question_id = f"q{hashlib.sha256(f'{content_str}{timestamp}'.encode()).hexdigest()[:16]}"
            
            # 2. Luo kysymysdata
            question_data = {
                "local_id": question_id,
                "source": "local",
                "content": {
                    "category": {
                        "fi": command.category,
                        "en": command.category,
                        "sv": command.category
                    },
                    "question": command.content.get("question", {}),
                    "tags": command.tags or [],
                    "scale": {
                        "min": -5,
                        "max": 5,
                        "labels": {
                            "fi": {"min": "Täysin eri mieltä", "neutral": "Neutraali", "max": "Täysin samaa mieltä"},
                            "en": {"min": "Strongly disagree", "neutral": "Neutral", "max": "Strongly agree"},
                            "sv": {"min": "Helt avig", "neutral": "Neutral", "max": "Helt enig"}
                        }
                    }
                },
                "elo_rating": {
                    "base_rating": 1000,
                    "current_rating": 1000,
                    "comparison_delta": 0,
                    "vote_delta": 0,
                    "total_comparisons": 0,
                    "total_votes": 0,
                    "up_votes": 0,
                    "down_votes": 0
                },
                "timestamps": {
                    "created_local": timestamp,
                    "modified_local": timestamp
                },
                "metadata": {
                    "submitted_by": command.submitted_by,
                    "status": "pending",
                    **command.metadata
                }
            }
            
            # 3. Fallback: Kirjoita suoraan tmp_new_questions.json
            return self._fallback_submit(question_data, command.submitted_by)
            
        except Exception as e:
            return {"success": False, "error": f"Submit failed: {str(e)}"}
    
    def _fallback_submit(self, question_data: Dict, user_id: str) -> Dict[str, Any]:
        """Fallback: Kirjoita suoraan tmp_new_questions.json"""
        try:
            from pathlib import Path
            import json
            
            tmp_file = Path("runtime/tmp_new_questions.json")
            tmp_questions = []
            
            if tmp_file.exists():
                with open(tmp_file, 'r', encoding='utf-8') as f:
                    tmp_data = json.load(f)
                    tmp_questions = tmp_data.get('questions', [])
            
            # Lisää uusi kysymys
            tmp_questions.append(question_data)
            
            # Tallenna
            with open(tmp_file, 'w', encoding='utf-8') as f:
                json.dump({"questions": tmp_questions}, f, indent=2, ensure_ascii=False)
            
            # Kirjaa system chainiin
            try:
                from system_chain_manager import log_action
                log_action(
                    "question_submitted",
                    f"Kysymys lähetetty (fallback): {question_data['local_id']}",
                    question_ids=[question_data['local_id']],
                    user_id=user_id
                )
            except ImportError:
                pass
            
            return {
                "success": True,
                "question_id": question_data['local_id'],
                "queue_position": len(tmp_questions),
                "auto_synced": False,
                "message": "Question submitted (fallback mode)"
            }
            
        except Exception as e:
            return {"success": False, "error": f"Fallback submit failed: {str(e)}"}

class SubmitQuestionResult:
    def __init__(self, success, message, data=None):
        self.success = success
        self.message = message
        self.data = data or {}
    
    @classmethod
    def success_result(cls, message, data=None):
        return cls(True, message, data)
    
    @classmethod  
    def error_result(cls, message, data=None):
        return cls(False, message, data)
