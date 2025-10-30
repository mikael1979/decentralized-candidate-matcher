#!/usr/bin/env python3
# initialization.py - PÄIVITETTY
"""
Päivitetty alustusskripti uusille base JSON -tiedostoille
"""

import json
import shutil
from datetime import datetime
from pathlib import Path

class EnhancedFileInitializer:
    def __init__(self, base_dir="base_templates", runtime_dir="runtime"):
        self.base_dir = Path(base_dir)
        self.runtime_dir = Path(runtime_dir)
        self.base_dir.mkdir(exist_ok=True)
        self.runtime_dir.mkdir(exist_ok=True)
        
    def initialize_all_base_templates(self):
        """Alusta kaikki uudet base template -tiedostot"""
        print("🔄 ALUSTETAAN UUDET BASE TEMPLATE -TIEDOSTOT...")
        
        base_templates = {
            # Olemassa olevat tiedostot
            'questions.base.json': self._get_questions_base(),
            'meta.base.json': self._get_meta_base(),
            'governance.base.json': self._get_governance_base(),
            'community.base.json': self._get_community_base(),
            'install_config.base.json': self._get_install_config_base(),
            'system_chain.base.json': self._get_system_chain_base(),
            'ipfs.base.json': self._get_ipfs_base(),
            'ipfs_conf.base.json': self._get_ipfs_conf_base(),
            'candidates.base.json': self._get_candidates_base(),
            'active_questions.base.json': self._get_active_questions_base(),
            
            # UUDET tiedostot
            'ipfs_blocks_metadata.base.json': self._get_ipfs_blocks_metadata_base(),
            'block_template.base.json': self._get_block_template_base(),
            'recovery_config.base.json': self._get_recovery_config_base(),
            'integrity_fingerprint.base.json': self._get_integrity_fingerprint_base(),
            'enhanced_system_chain.base.json': self._get_enhanced_system_chain_base(),
            'multi_node_sync.base.json': self._get_multi_node_sync_base()
        }
        
        for filename, template in base_templates.items():
            filepath = self.base_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2, ensure_ascii=False)
            print(f"✅ Luotu: {filename}")
        
        print("🎯 KAIKKI BASE TEMPLATE -TIEDOSTOT ALUSTETTU!")
    
    def initialize_runtime_files(self):
        """Kloonaa base-tiedostot runtime-kansioon"""
        print("🔄 KLOONATAAN BASE -> RUNTIME...")
        
        # Kloonaa perustiedostot
        base_files = [
            'questions.base.json', 'meta.base.json', 'governance.base.json',
            'community.base.json', 'install_config.base.json', 
            'system_chain.base.json', 'ipfs.base.json', 'ipfs_conf.base.json',
            'candidates.base.json', 'active_questions.base.json'
        ]
        
        for base_file in base_files:
            runtime_file = base_file.replace('.base.json', '.json')
            source_path = self.base_dir / base_file
            target_path = self.runtime_dir / runtime_file
            
            if source_path.exists():
                shutil.copy2(source_path, target_path)
                print(f"✅ Kloonattu: {base_file} -> {runtime_file}")
            else:
                print(f"⚠️  Lähdetiedostoa ei löydy: {base_file}")
        
        # Alusta uudet runtime-tiedostot
        self.initialize_enhanced_runtime_files()
        
    def initialize_enhanced_runtime_files(self):
        """Alusta uudet runtime-tiedostot"""
        print("🔄 ALUSTETAAN UUDET RUNTIME-TIEDOSTOT...")
        
        enhanced_files = {
            'recovery_config.json': self._get_recovery_config_base(),
            'integrity_fingerprint.json': self._get_integrity_fingerprint_base(),
            'multi_node_sync.json': self._get_multi_node_sync_base(),
            'ipfs_blocks_metadata.json': self._get_ipfs_blocks_metadata_base()
        }
        
        for filename, template in enhanced_files.items():
            filepath = self.runtime_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2, ensure_ascii=False)
            print(f"✅ Alustettu: {filename}")
        
        # Alusta tyhjät tiedostot
        self.initialize_empty_runtime_files()
    
    def initialize_empty_runtime_files(self):
        """Alusta tyhjät runtime-tiedostot"""
        empty_files = [
            'new_questions.json',
            'active_questions.json', 
            'ipfs_questions.json',
            'parties.json',
            'party_profiles.json',
            'candidates.json',
            'candidate_profiles.json',
            'tmp_new_questions.json',
            'emergency_backups.json'
        ]
        
        for file in empty_files:
            file_path = self.runtime_dir / file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "metadata": {
                        "created": datetime.now().isoformat(),
                        "version": "1.0.0",
                        "source": "empty_initialization"
                    },
                    "data": []
                }, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Tyhjä alustettu: {file}")
    
    # Template getter -metodit
    def _get_ipfs_blocks_metadata_base(self):
        return {
            "metadata": {
                "version": "1.0.0",
                "created": "{{TIMESTAMP}}",
                "last_updated": "{{TIMESTAMP}}",
                "election_id": "{{ELECTION_ID}}",
                "node_id": "{{NODE_ID}}",
                "description": {
                    "fi": "IPFS-lohkojen metatiedot",
                    "en": "IPFS blocks metadata", 
                    "sv": "IPFS-block metadata"
                }
            },
            "block_sequence": ["buffer1", "urgent", "sync", "active", "buffer2"],
            "current_rotation": 0,
            "total_rotations": 0,
            "blocks": {
                "buffer1": "{{BUFFER1_CID}}",
                "urgent": "{{URGENT_CID}}",
                "sync": "{{SYNC_CID}}",
                "active": "{{ACTIVE_CID}}",
                "buffer2": "{{BUFFER2_CID}}"
            },
            "rotation_history": [],
            "node_registry": ["{{NODE_ID}}"],
            "sync_config": {
                "auto_rotate": true,
                "max_block_size": {
                    "buffer1": 100,
                    "urgent": 50,
                    "sync": 200,
                    "active": 150,
                    "buffer2": 100
                }
            }
        }
    
    def _get_block_template_base(self):
        return {
            "metadata": {
                "block_name": "{{BLOCK_NAME}}",
                "purpose": "{{BLOCK_PURPOSE}}",
                "created": "{{TIMESTAMP}}",
                "max_size": {{MAX_SIZE}},
                "time_window": {{TIME_WINDOW}},
                "election_id": "{{ELECTION_ID}}",
                "node_id": "{{NODE_ID}}",
                "priority": "{{PRIORITY_LEVEL}}"
            },
            "entries": [],
            "current_index": 0,
            "total_entries": 0,
            "entry_hashes": []
        }
    
    def _get_recovery_config_base(self):
        return {
            "metadata": {
                "version": "1.0.0",
                "created": "{{TIMESTAMP}}",
                "election_id": "{{ELECTION_ID}}",
                "node_id": "{{NODE_ID}}",
                "description": {
                    "fi": "Palautusjärjestelmän konfiguraatio",
                    "en": "Recovery system configuration",
                    "sv": "Återställningssystem konfiguration"
                }
            },
            "recovery_config": {
                "auto_backup_interval": 3600,
                "emergency_threshold": 5,
                "max_recovery_attempts": 3,
                "data_retention_days": 30
            },
            "block_management": {
                "auto_rotation": true,
                "rotation_check_interval": 300
            }
        }
    
    def _get_integrity_fingerprint_base(self):
        return {
            "metadata": {
                "version": "2.0.0",
                "created": "{{TIMESTAMP}}",
                "system_locked": false,
                "mode": "development",
                "system_version": "2.0.0"
            },
            "modules": {},
            "verification_history": [],
            "security_settings": {
                "require_integrity_check": true,
                "lock_on_violation": true
            }
        }
    
    def _get_enhanced_system_chain_base(self):
        return {
            "chain_id": "enhanced_chain_{{ELECTION_ID}}",
            "created_at": "{{TIMESTAMP}}",
            "version": "2.0.0",
            "metadata": {
                "ipfs_integrated": true,
                "election_id": "{{ELECTION_ID}}",
                "node_id": "{{NODE_ID}}"
            },
            "blocks": [],
            "current_state": {
                "last_updated": "{{TIMESTAMP}}",
                "total_blocks": 0,
                "ipfs_backed": false
            }
        }
    
    def _get_multi_node_sync_base(self):
        return {
            "metadata": {
                "version": "1.0.0",
                "created": "{{TIMESTAMP}}",
                "election_id": "{{ELECTION_ID}}"
            },
            "sync_settings": {
                "enabled": true,
                "auto_sync_interval": 1800,
                "max_nodes_per_sync": 10
            },
            "node_discovery": {
                "auto_discovery": true,
                "known_nodes": ["{{NODE_ID}}"]
            }
        }
    
    # Olemassa olevat template-getterit
    def _get_questions_base(self):
        return {"metadata": {"version": "2.0.0"}, "questions": []}
    
    def _get_meta_base(self):
        return {"metadata": {"version": "1.0.0"}}
    
    def _get_governance_base(self):
        return {"metadata": {"version": "1.0.0"}}
    
    def _get_community_base(self):
        return {"metadata": {"version": "1.0.0"}}
    
    def _get_install_config_base(self):
        return {"metadata": {"version": "1.0.0"}}
    
    def _get_system_chain_base(self):
        return {"metadata": {"version": "1.0.0"}}
    
    def _get_ipfs_base(self):
        return {"metadata": {"version": "1.0.0"}}
    
    def _get_ipfs_conf_base(self):
        return {"metadata": {"version": "1.0.0"}}
    
    def _get_candidates_base(self):
        return {"metadata": {"version": "2.0.0"}, "candidates": []}
    
    def _get_active_questions_base(self):
        return {"metadata": {"version": "1.0.0"}, "questions": []}

# Käyttö
if __name__ == "__main__":
    initializer = EnhancedFileInitializer()
    initializer.initialize_all_base_templates()
    initializer.initialize_runtime_files()
