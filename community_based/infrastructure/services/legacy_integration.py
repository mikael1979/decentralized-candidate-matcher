#!/usr/bin/env python3
"""
Legacy Integration Service - Bridges between new architecture and legacy code
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from core.dependency_container import get_container
from domain.value_objects import MultilingualText, Category, Scale, UserId

class LegacyIntegrationService:
    """Service for integrating with legacy question manager"""
    
    def __init__(self, runtime_dir: str = "runtime"):
        self.runtime_dir = Path(runtime_dir)
        self.container = get_container(runtime_dir=runtime_dir)
        
        # Initialize container if not already done
        self.container.initialize()
    
    def migrate_legacy_questions(self) -> Dict[str, Any]:
        """Migrate questions from legacy JSON files to new repository"""
        try:
            legacy_files = [
                self.runtime_dir / "tmp_new_questions.json",
                self.runtime_dir / "new_questions.json", 
                self.runtime_dir / "questions.json",
                self.runtime_dir / "active_questions.json"
            ]
            
            migration_stats = {
                "total_migrated": 0,
                "files_processed": 0,
                "errors": []
            }
            
            for legacy_file in legacy_files:
                if legacy_file.exists():
                    migrated = self._migrate_legacy_file(legacy_file)
                    migration_stats["total_migrated"] += migrated
                    migration_stats["files_processed"] += 1
            
            # Log migration
            self.container.system_logger.log_action(
                "legacy_migration",
                f"Migrated {migration_stats['total_migrated']} questions from legacy files",
                metadata=migration_stats
            )
            
            return {
                "success": True,
                "message": f"Migrated {migration_stats['total_migrated']} questions",
                "stats": migration_stats
            }
            
        except Exception as e:
            error_msg = f"Legacy migration failed: {str(e)}"
            self.container.system_logger.log_action(
                "legacy_migration_error",
                error_msg,
                metadata={"error": str(e)}
            )
            
            return {
                "success": False,
                "error": error_msg
            }
    
    def _migrate_legacy_file(self, legacy_file: Path) -> int:
        """Migrate a single legacy file"""
        migrated_count = 0
        
        try:
            with open(legacy_file, 'r', encoding='utf-8') as f:
                legacy_data = json.load(f)
            
            questions_data = legacy_data.get("questions", [])
            
            for question_data in questions_data:
                try:
                    # Convert legacy format to new domain entity
                    question = self._convert_legacy_question(question_data)
                    
                    # Determine storage based on file type
                    if "tmp" in legacy_file.stem:
                        self.container.question_repository.save_temporary(question)
                    elif "active" in legacy_file.stem:
                        self.container.question_repository.save_active(question)
                    else:
                        self.container.question_repository.save_new(question)
                    
                    migrated_count += 1
                    
                except Exception as e:
                    print(f"Warning: Could not migrate question from {legacy_file}: {e}")
                    continue
            
            print(f"✅ Migrated {migrated_count} questions from {legacy_file.name}")
            
        except Exception as e:
            print(f"Error migrating {legacy_file}: {e}")
        
        return migrated_count
    
    def _convert_legacy_question(self, legacy_data: Dict[str, Any]):
        """Convert legacy question format to new domain entity"""
        from domain.entities.question import Question
        
        # Extract content
        content_data = legacy_data["content"]
        question_text = content_data["question"]
        
        content = MultilingualText(
            fi=question_text.get("fi", ""),
            en=question_text.get("en", ""),
            sv=question_text.get("sv", "")
        )
        
        # Extract category
        category_data = content_data["category"]
        category = Category(
            name=MultilingualText(
                fi=category_data.get("fi", ""),
                en=category_data.get("en", ""),
                sv=category_data.get("sv", "")
            )
        )
        
        # Extract scale
        scale_data = content_data["scale"]
        scale = Scale(
            min=scale_data["min"],
            max=scale_data["max"],
            labels=scale_data.get("labels", {})
        )
        
        # Create question using domain entity
        # Note: We preserve the original local_id
        question = Question.create(
            content=content,
            category=category,
            scale=scale,
            submitted_by=UserId(legacy_data.get("metadata", {}).get("submitted_by", "legacy_user")),
            tags=content_data.get("tags", [])
        )
        
        # Override ID to preserve original
        from domain.value_objects import QuestionId
        question.id = QuestionId(legacy_data["local_id"])
        
        # Preserve existing rating data
        rating_data = legacy_data["elo_rating"]
        question.rating = self._convert_legacy_rating(rating_data)
        
        # Preserve timestamps
        from domain.value_objects import CreationTimestamps
        from datetime import datetime
        timestamps_data = legacy_data["timestamps"]
        
        question.timestamps = CreationTimestamps(
            created=datetime.fromisoformat(timestamps_data["created_local"].replace('Z', '+00:00')),
            modified=datetime.fromisoformat(timestamps_data["modified_local"].replace('Z', '+00:00'))
        )
        
        # Preserve metadata
        question.metadata = legacy_data.get("metadata", {})
        question.ipfs_cid = legacy_data.get("ipfs_cid")
        question.source = legacy_data.get("source", "legacy")
        
        # Preserve counts
        question.comparison_count = rating_data.get("total_comparisons", 0)
        question.vote_count = rating_data.get("total_votes", 0)
        question.up_votes = rating_data.get("up_votes", 0)
        question.down_votes = rating_data.get("down_votes", 0)
        
        return question
    
    def _convert_legacy_rating(self, rating_data: Dict[str, Any]):
        """Convert legacy rating format to new value object"""
        from domain.value_objects import Rating
        
        return Rating(
            value=rating_data["current_rating"],
            comparison_delta=rating_data.get("comparison_delta", 0),
            vote_delta=rating_data.get("vote_delta", 0)
        )
    
    def sync_to_legacy_format(self) -> Dict[str, Any]:
        """Sync new repository data back to legacy JSON format (for compatibility)"""
        try:
            # Get all questions from new repository
            tmp_questions = self.container.question_repository.find_temporary_questions()
            new_questions = self.container.question_repository.find_new_questions()
            active_questions = self.container.question_repository.find_active_questions()
            
            # Convert to legacy format and save
            self._save_legacy_file(self.runtime_dir / "tmp_new_questions.json", tmp_questions)
            self._save_legacy_file(self.runtime_dir / "new_questions.json", new_questions)
            self._save_legacy_file(self.runtime_dir / "active_questions.json", active_questions)
            
            total_synced = len(tmp_questions) + len(new_questions) + len(active_questions)
            
            self.container.system_logger.log_action(
                "legacy_sync",
                f"Synced {total_synced} questions to legacy format",
                metadata={
                    "tmp_questions": len(tmp_questions),
                    "new_questions": len(new_questions),
                    "active_questions": len(active_questions)
                }
            )
            
            return {
                "success": True,
                "message": f"Synced {total_synced} questions to legacy format",
                "stats": {
                    "tmp_questions": len(tmp_questions),
                    "new_questions": len(new_questions),
                    "active_questions": len(active_questions)
                }
            }
            
        except Exception as e:
            error_msg = f"Legacy sync failed: {str(e)}"
            self.container.system_logger.log_action(
                "legacy_sync_error",
                error_msg,
                metadata={"error": str(e)}
            )
            
            return {
                "success": False,
                "error": error_msg
            }
    
    def _save_legacy_file(self, file_path: Path, questions: List):
        """Save questions in legacy JSON format"""
        legacy_data = {
            "metadata": {
                "created": "2024-01-01T00:00:00Z",  # Placeholder
                "last_updated": "2024-01-01T00:00:00Z",
                "total_questions": len(questions),
                "version": "2.0.0",
                "source": "new_architecture"
            },
            "questions": [question.to_dict() for question in questions]
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(legacy_data, f, indent=2, ensure_ascii=False)
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get integration status between new and legacy systems"""
        legacy_files = {
            "tmp_new_questions.json": self.runtime_dir / "tmp_new_questions.json",
            "new_questions.json": self.runtime_dir / "new_questions.json",
            "active_questions.json": self.runtime_dir / "active_questions.json",
            "questions.json": self.runtime_dir / "questions.json"
        }
        
        status = {
            "legacy_files": {},
            "new_repository": self.container.question_repository.get_question_stats(),
            "migration_recommended": False
        }
        
        # Check legacy files
        total_legacy_questions = 0
        for name, path in legacy_files.items():
            file_exists = path.exists()
            question_count = 0
            
            if file_exists:
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    question_count = len(data.get("questions", []))
                    total_legacy_questions += question_count
                except:
                    question_count = -1  # Error reading file
            
            status["legacy_files"][name] = {
                "exists": file_exists,
                "question_count": question_count
            }
        
        # Check if migration is recommended
        new_stats = status["new_repository"]
        status["migration_recommended"] = (
            total_legacy_questions > 0 and 
            new_stats.get("total_questions", 0) < total_legacy_questions
        )
        
        return status
