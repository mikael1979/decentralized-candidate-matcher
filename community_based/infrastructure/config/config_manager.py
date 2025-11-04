#!/usr/bin/env python3
"""
Configuration Manager - Centralized configuration management
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    """Centralized configuration management for the application"""
    
    def __init__(self, config_dir: str = "config", runtime_dir: str = "runtime"):
        self.config_dir = Path(config_dir)
        self.runtime_dir = Path(runtime_dir)
        
        # Ensure directories exist
        self.config_dir.mkdir(exist_ok=True)
        self.runtime_dir.mkdir(exist_ok=True)
        
        # Load configuration
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from files"""
        config = {
            "system": self._load_system_config(),
            "questions": self._load_questions_config(),
            "elections": self._load_elections_config(),
            "ipfs": self._load_ipfs_config(),
            "sync": self._load_sync_config()
        }
        
        # Load runtime-specific config if exists
        runtime_config_file = self.runtime_dir / "runtime_config.json"
        if runtime_config_file.exists():
            try:
                with open(runtime_config_file, 'r', encoding='utf-8') as f:
                    runtime_config = json.load(f)
                config["runtime"] = runtime_config
            except Exception as e:
                print(f"Warning: Could not load runtime config: {e}")
        
        return config
    
    def _load_system_config(self) -> Dict[str, Any]:
        """Load system configuration"""
        system_config_file = self.config_dir / "system_config.json"
        
        if system_config_file.exists():
            try:
                with open(system_config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load system config: {e}")
        
        # Default system configuration
        return {
            "mode": "development",
            "logging_level": "INFO",
            "enable_integrity_checks": True,
            "auto_backup": True,
            "backup_interval_hours": 24
        }
    
    def _load_questions_config(self) -> Dict[str, Any]:
        """Load questions configuration"""
        questions_config_file = self.config_dir / "questions_config.json"
        
        if questions_config_file.exists():
            try:
                with open(questions_config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load questions config: {e}")
        
        # Default questions configuration
        return {
            "auto_sync_enabled": True,
            "batch_size": 5,
            "max_batch_size": 20,
            "time_interval_hours": 24,
            "active_question_rules": {
                "min_rating": 800,
                "min_comparisons": 5,
                "min_votes": 3,
                "max_questions": 15
            },
            "rating_calculation": {
                "base_k_factor": 32,
                "trust_multipliers": {
                    "new_user": 0.5,
                    "regular_user": 1.0,
                    "trusted_user": 1.2,
                    "validator": 1.5
                }
            }
        }
    
    def _load_elections_config(self) -> Dict[str, Any]:
        """Load elections configuration"""
        elections_config_file = self.config_dir / "elections_config.json"
        
        if elections_config_file.exists():
            try:
                with open(elections_config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load elections config: {e}")
        
        # Default elections configuration
        return {
            "default_election_type": "municipal",
            "supported_election_types": ["presidential", "municipal", "test"],
            "default_phases": [
                {
                    "name": {"fi": "Kysymysten lähetys", "en": "Question submission", "sv": "Frågeinsändning"},
                    "duration_days": 30
                },
                {
                    "name": {"fi": "Äänestys", "en": "Voting", "sv": "Röstning"},
                    "duration_days": 14
                }
            ]
        }
    
    def _load_ipfs_config(self) -> Dict[str, Any]:
        """Load IPFS configuration"""
        ipfs_config_file = self.config_dir / "ipfs_config.json"
        
        if ipfs_config_file.exists():
            try:
                with open(ipfs_config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load IPFS config: {e}")
        
        # Default IPFS configuration
        return {
            "use_mock": True,
            "real_ipfs_host": "localhost",
            "real_ipfs_port": 5001,
            "block_config": {
                "buffer1": {"max_size": 100},
                "urgent": {"max_size": 50},
                "sync": {"max_size": 200},
                "active": {"max_size": 150},
                "buffer2": {"max_size": 100}
            }
        }
    
    def _load_sync_config(self) -> Dict[str, Any]:
        """Load sync configuration"""
        sync_config_file = self.config_dir / "sync_config.json"
        
        if sync_config_file.exists():
            try:
                with open(sync_config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load sync config: {e}")
        
        # Default sync configuration
        return {
            "use_schedule": True,
            "schedule_priority_mapping": {
                "emergency": "critical",
                "high": "high",
                "normal": "normal",
                "low": "low"
            },
            "max_retries": 3,
            "retry_delay_seconds": 60
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (dot notation supported)"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_module_config(self, module: str) -> Dict[str, Any]:
        """Get configuration for a specific module"""
        return self._config.get(module, {})
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update configuration with new values"""
        self._deep_update(self._config, updates)
        
        # Save updated configuration to runtime
        self._save_runtime_config()
    
    def _deep_update(self, original: Dict, updates: Dict) -> None:
        """Deep update a dictionary"""
        for key, value in updates.items():
            if isinstance(value, dict) and key in original and isinstance(original[key], dict):
                self._deep_update(original[key], value)
            else:
                original[key] = value
    
    def _save_runtime_config(self) -> None:
        """Save current configuration to runtime file"""
        runtime_config_file = self.runtime_dir / "runtime_config.json"
        
        try:
            with open(runtime_config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save runtime config: {e}")
    
    def verify_config_integrity(self) -> bool:
        """Verify that all required configuration is present"""
        required_sections = ["system", "questions", "elections", "ipfs"]
        
        for section in required_sections:
            if section not in self._config:
                print(f"Missing configuration section: {section}")
                return False
        
        # Check specific required values
        required_values = [
            "system.mode",
            "questions.batch_size", 
            "questions.auto_sync_enabled",
            "ipfs.use_mock"
        ]
        
        for key in required_values:
            if self.get(key) is None:
                print(f"Missing configuration value: {key}")
                return False
        
        return True
    
    def get_election_config(self, election_id: str) -> Dict[str, Any]:
        """Get configuration for a specific election"""
        election_config = self._config.get("elections", {}).copy()
        
        # Add election-specific overrides if they exist
        election_specific_key = f"elections.{election_id}"
        election_specific_config = self.get(election_specific_key)
        
        if election_specific_config:
            election_config.update(election_specific_config)
        
        return election_config
