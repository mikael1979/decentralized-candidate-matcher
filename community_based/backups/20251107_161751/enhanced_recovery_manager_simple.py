# enhanced_recovery_manager_simple.py
#!/usr/bin/env python3
"""
Simple Recovery Manager - Without schedule manager dependency
"""

import json
from datetime import datetime
from pathlib import Path

class SimpleRecoveryManager:
    """Simplified recovery manager without IPFS schedule dependency"""
    
    def __init__(self, runtime_dir: str = "runtime", ipfs_client=None, 
                 election_id: str = None, node_id: str = None):
        self.runtime_dir = Path(runtime_dir)
        self.ipfs_client = ipfs_client
        self.election_id = election_id or "default_election"
        self.node_id = node_id or "unknown_node"
        
        self.namespace = f"election_{self.election_id}_{datetime.now().strftime('%Y%m%d')}"
        self.recovery_file = self.runtime_dir / "recovery_config.json"
    
    def initialize_recovery_system(self):
        """Initialize simple recovery system"""
        print(f"   🛡️  Alustetaan palautus: {self.namespace}")
        
        # Create recovery config
        recovery_config = {
            "metadata": {
                "version": "1.0.0",
                "created": datetime.now().isoformat(),
                "election_id": self.election_id,
                "node_id": self.node_id,
                "namespace": self.namespace,
                "description": "Simple recovery system"
            },
            "recovery_config": {
                "auto_backup_interval": 3600,
                "emergency_threshold": 5,
                "max_recovery_attempts": 3,
                "data_retention_days": 30
            },
            "backup_history": [],
            "last_successful_backup": None
        }
        
        # Save locally
        with open(self.recovery_file, 'w', encoding='utf-8') as f:
            json.dump(recovery_config, f, indent=2, ensure_ascii=False)
        
        # Upload to IPFS if available
        if self.ipfs_client:
            try:
                cid = self.ipfs_client.upload(recovery_config)
                print(f"   ✅ Palautuskonfiguraatio tallennettu IPFS:ään: {cid}")
                return cid
            except Exception as e:
                print(f"   ⚠️  IPFS-tallennus epäonnistui: {e}")
        
        return "local_only"
    
    def create_backup(self, backup_data: dict, backup_type: str = "manual"):
        """Create simple backup"""
        backup = {
            "timestamp": datetime.now().isoformat(),
            "type": backup_type,
            "data": backup_data,
            "election_id": self.election_id,
            "node_id": self.node_id
        }
        
        # Load existing config
        if self.recovery_file.exists():
            with open(self.recovery_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {"backup_history": []}
        
        # Add backup to history
        config["backup_history"].append(backup)
        config["last_successful_backup"] = datetime.now().isoformat()
        
        # Keep only last 10 backups
        if len(config["backup_history"]) > 10:
            config["backup_history"] = config["backup_history"][-10:]
        
        # Save updated config
        with open(self.recovery_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Varmuuskopio luotu: {backup_type}")
        return True
