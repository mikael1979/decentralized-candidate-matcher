#!/usr/bin/env python3
"""
System Logger - Unified logging for system events
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

from domain.value_objects import UserId

class SystemLogger:
    """Unified system logging service"""
    
    def __init__(self, runtime_dir: str = "runtime", enable_chain_logging: bool = True):
        self.runtime_dir = Path(runtime_dir)
        self.enable_chain_logging = enable_chain_logging
        
        # Chain file for system_chain.json integration
        self.chain_file = self.runtime_dir / "system_chain.json"
        
        # Simple log file for quick debugging
        self.log_file = self.runtime_dir / "system_log.json"
        
        self._initialize_logging()
    
    def _initialize_logging(self):
        """Initialize logging files"""
        if not self.chain_file.exists():
            self._create_initial_chain()
        
        if not self.log_file.exists():
            self._create_initial_log()
    
    def _create_initial_chain(self):
        """Create initial system_chain.json"""
        initial_chain = {
            "chain_id": "system_chain_v2",
            "created_at": datetime.now().isoformat(),
            "description": "System event chain for vaalikone",
            "version": "2.0.0",
            "blocks": [],
            "current_state": {
                "last_updated": None,
                "total_blocks": 0
            },
            "metadata": {
                "logging_system": "SystemLogger",
                "initialized": True
            }
        }
        
        self._save_chain(initial_chain)
    
    def _create_initial_log(self):
        """Create initial system log"""
        initial_log = {
            "metadata": {
                "created": datetime.now().isoformat(),
                "log_type": "system_events",
                "version": "1.0.0"
            },
            "events": []
        }
        
        self._save_log(initial_log)
    
    def log_action(
        self, 
        action_type: str, 
        description: str,
        user_id: Optional[UserId] = None,
        question_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Log a system action"""
        try:
            # Create log entry
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "action_type": action_type,
                "description": description,
                "user_id": user_id.value if user_id else None,
                "question_ids": question_ids or [],
                "metadata": metadata or {}
            }
            
            # Add to system chain if enabled
            if self.enable_chain_logging:
                self._add_to_chain(log_entry)
            
            # Add to simple log
            self._add_to_log(log_entry)
            
            print(f"📝 [{action_type}] {description}")
            return True
            
        except Exception as e:
            print(f"❌ Logging failed: {e}")
            return False
    
    def _add_to_chain(self, log_entry: Dict[str, Any]):
        """Add entry to system_chain.json"""
        try:
            chain_data = self._load_chain()
            
            # Create new block
            new_block = {
                "block_id": len(chain_data["blocks"]),
                "timestamp": log_entry["timestamp"],
                "action_type": log_entry["action_type"],
                "description": log_entry["description"],
                "user_id": log_entry["user_id"],
                "question_ids": log_entry["question_ids"],
                "metadata": log_entry["metadata"],
                "previous_hash": self._get_previous_hash(chain_data),
                "block_hash": None  # Will be calculated after adding
            }
            
            # Add to chain
            chain_data["blocks"].append(new_block)
            
            # Update current state
            chain_data["current_state"]["last_updated"] = log_entry["timestamp"]
            chain_data["current_state"]["total_blocks"] = len(chain_data["blocks"])
            
            # Calculate block hash
            new_block["block_hash"] = self._calculate_block_hash(new_block)
            
            self._save_chain(chain_data)
            
        except Exception as e:
            print(f"⚠️  Failed to add to chain: {e}")
    
    def _add_to_log(self, log_entry: Dict[str, Any]):
        """Add entry to simple log file"""
        try:
            log_data = self._load_log()
            log_data["events"].append(log_entry)
            
            # Keep only last 1000 events to prevent file from growing too large
            if len(log_data["events"]) > 1000:
                log_data["events"] = log_data["events"][-1000:]
            
            log_data["metadata"]["last_updated"] = datetime.now().isoformat()
            log_data["metadata"]["total_events"] = len(log_data["events"])
            
            self._save_log(log_data)
            
        except Exception as e:
            print(f"⚠️  Failed to add to log: {e}")
    
    def _load_chain(self) -> Dict[str, Any]:
        """Load system chain data"""
        with open(self.chain_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_chain(self, chain_data: Dict[str, Any]):
        """Save system chain data"""
        with open(self.chain_file, 'w', encoding='utf-8') as f:
            json.dump(chain_data, f, indent=2, ensure_ascii=False)
    
    def _load_log(self) -> Dict[str, Any]:
        """Load system log data"""
        with open(self.log_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_log(self, log_data: Dict[str, Any]):
        """Save system log data"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
    
    def _get_previous_hash(self, chain_data: Dict[str, Any]) -> Optional[str]:
        """Get hash of previous block"""
        if not chain_data["blocks"]:
            return None
        
        last_block = chain_data["blocks"][-1]
        return last_block.get("block_hash")
    
    def _calculate_block_hash(self, block: Dict[str, Any]) -> str:
        """Calculate hash for a block"""
        import hashlib
        
        # Create copy without hash fields for calculation
        block_copy = block.copy()
        block_copy.pop("previous_hash", None)
        block_copy.pop("block_hash", None)
        
        block_string = json.dumps(block_copy, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(block_string.encode('utf-8')).hexdigest()
    
    def get_chain_status(self) -> Dict[str, Any]:
        """Get system chain status"""
        try:
            chain_data = self._load_chain()
            
            return {
                "chain_id": chain_data.get("chain_id"),
                "total_blocks": len(chain_data.get("blocks", [])),
                "last_updated": chain_data.get("current_state", {}).get("last_updated"),
                "created_at": chain_data.get("created_at"),
                "integrity_verified": self._verify_chain_integrity(chain_data)
            }
        except Exception as e:
            return {
                "error": str(e),
                "chain_file_exists": self.chain_file.exists()
            }
    
    def _verify_chain_integrity(self, chain_data: Dict[str, Any]) -> bool:
        """Verify system chain integrity"""
        try:
            blocks = chain_data.get("blocks", [])
            
            for i, block in enumerate(blocks):
                # Verify block hash
                calculated_hash = self._calculate_block_hash(block)
                if block.get("block_hash") != calculated_hash:
                    return False
                
                # Verify previous hash chain (except first block)
                if i > 0:
                    previous_block = blocks[i-1]
                    if block.get("previous_hash") != previous_block.get("block_hash"):
                        return False
            
            return True
            
        except Exception:
            return False
    
    def get_recent_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent system events"""
        try:
            log_data = self._load_log()
            events = log_data.get("events", [])
            
            # Return most recent events
            return events[-limit:]
            
        except Exception as e:
            print(f"⚠️  Failed to get recent events: {e}")
            return []
