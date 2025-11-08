#!/usr/bin/env python3
"""
Test Utilities - Helper functions for testing the new architecture
"""

import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

from core.dependency_container import DependencyContainer, reset_container
from domain.value_objects import MultilingualText, Category, Scale, UserId

class TestUtils:
    """Utility functions for testing"""
    
    @staticmethod
    def create_test_container() -> tuple[DependencyContainer, tempfile.TemporaryDirectory]:
        """Create a test container with temporary directories"""
        temp_dir = tempfile.TemporaryDirectory()
        temp_path = Path(temp_dir.name)
        
        # Create necessary subdirectories
        config_dir = temp_path / "config"
        runtime_dir = temp_path / "runtime"
        config_dir.mkdir()
        runtime_dir.mkdir()
        
        # Create basic config files
        TestUtils._create_test_configs(config_dir)
        
        # Reset any existing container and create new one
        reset_container()
        container = DependencyContainer(
            config_dir=str(config_dir),
            runtime_dir=str(runtime_dir)
        )
        
        return container, temp_dir
    
    @staticmethod
    def _create_test_configs(config_dir: Path):
        """Create test configuration files"""
        # System config
        system_config = {
            "mode": "development",
            "logging_level": "DEBUG",
            "enable_integrity_checks": False,
            "auto_backup": False
        }
        
        with open(config_dir / "system_config.json", 'w') as f:
            import json
            json.dump(system_config, f, indent=2)
        
        # Questions config
        questions_config = {
            "auto_sync_enabled": True,
            "batch_size": 2,  # Small for testing
            "max_batch_size": 5,
            "time_interval_hours": 24,
            "active_question_rules": {
                "min_rating": 500,  # Low for testing
                "min_comparisons": 1,
                "min_votes": 1,
                "max_questions": 5
            }
        }
        
        with open(config_dir / "questions_config.json", 'w') as f:
            import json
            json.dump(questions_config, f, indent=2)
        
        # IPFS config
        ipfs_config = {
            "use_mock": True,
            "use_ipfs_storage": False  # Use JSON for simpler testing
        }
        
        with open(config_dir / "ipfs_config.json", 'w') as f:
            import json
            json.dump(ipfs_config, f, indent=2)
    
    @staticmethod
    def create_test_question_content() -> tuple[MultilingualText, Category, Scale]:
        """Create test question content"""
        content = MultilingualText(
            fi="Testikysymys suomeksi",
            en="Test question in English", 
            sv="Testfråga på svenska"
        )
        
        category = Category(
            name=MultilingualText(
                fi="Testikategoria",
                en="Test category",
                sv="Testkategori"
            )
        )
        
        scale = Scale(
            min=-5,
            max=5,
            labels={
                "fi": {"min": "Eri mieltä", "neutral": "Neutraali", "max": "Samaa mieltä"},
                "en": {"min": "Disagree", "neutral": "Neutral", "max": "Agree"},
                "sv": {"min": "Oenig", "neutral": "Neutral", "max": "Enig"}
            }
        )
        
        return content, category, scale
    
    @staticmethod
    def create_test_user() -> UserId:
        """Create test user ID"""
        return UserId("test_user_123")
