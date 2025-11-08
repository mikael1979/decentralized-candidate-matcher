# simple_initialization.py
#!/usr/bin/env python3
"""
Simplified system initialization without recovery manager issues
"""

import json
from datetime import datetime
from pathlib import Path

def initialize_simple():
    print("🏗️ YKSINKERTAISTETTU JÄRJESTELMÄN ALUSTUS")
    print("=" * 50)
    
    # Create runtime directory
    runtime_dir = Path("runtime")
    runtime_dir.mkdir(exist_ok=True)
    
    # 1. Initialize basic files
    print("1. 📁 Alustetaan perustiedostot...")
    
    basic_files = {
        "questions.json": {
            "metadata": {
                "version": "2.0.0",
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_questions": 0,
                "source": "simple_initialization"
            },
            "questions": []
        },
        "meta.json": {
            "metadata": {
                "version": "1.0.0",
                "created": datetime.now().isoformat(),
                "system_initialized": True,
                "election_id": "Jumaltenvaalit_2026"
            },
            "election": {
                "id": "Jumaltenvaalit_2026",
                "name": {
                    "fi": "Kreikkalaisten Jumalten Vaalit 2026",
                    "en": "Greek Gods Election 2026", 
                    "sv": "Grekiska Gudarnas Val 2026"
                },
                "date": "2026-01-15",
                "type": "divine_council",
                "timelock_enabled": True
            }
        },
        "system_chain.json": {
            "chain_id": "system_chain_v2",
            "created_at": datetime.now().isoformat(),
            "description": "System event chain for vaalikone",
            "version": "2.0.0",
            "blocks": [],
            "current_state": {
                "last_updated": None,
                "total_blocks": 0
            }
        },
        "active_questions.json": {
            "metadata": {
                "election_id": "Jumaltenvaalit_2026",
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "question_limit": 15,
                "min_rating": 800,
                "sync_enabled": True,
                "submission_locked": False
            },
            "questions": []
        }
    }
    
    for filename, content in basic_files.items():
        filepath = runtime_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        print(f"   ✅ {filename}")
    
    # 2. Initialize IPFS blocks (simplified)
    print("2. 🌐 Alustetaan IPFS-lohkot...")
    try:
        from mock_ipfs import MockIPFS
        ipfs = MockIPFS()
        
        # Simple block initialization without recovery manager
        block_data = {
            "metadata": {
                "election_id": "Jumaltenvaalit_2026",
                "created": datetime.now().isoformat(),
                "node_id": "main_node",
                "purpose": "system_initialization"
            },
            "blocks_initialized": True,
            "initialization_timestamp": datetime.now().isoformat()
        }
        
        # Just upload one simple block to show IPFS is working
        cid = ipfs.upload(block_data)
        print(f"   ✅ IPFS testi: {cid}")
        
    except Exception as e:
        print(f"   ⚠️  IPFS alustus ei onnistunut: {e}")
        print("   💡 Jatketaan ilman IPFS:ää")
    
    # 3. Import test data if available
    print("3. 📥 Tuodaan testidata...")
    try:
        from import_test_data import TestDataImporter
        importer = TestDataImporter()
        importer.import_all_data()
        print("   ✅ Testidata tuotu")
    except Exception as e:
        print(f"   ⚠️  Testidatan tuonti epäonnistui: {e}")
        print("   💡 Luodaan tyhjä kysymyskanta")
    
    print("\n🎯 JÄRJESTELMÄ ALUSTETTU ONNISTUNEESTI!")
    print("💡 Nyt voit suorittaa: python enable_production.py")

if __name__ == "__main__":
    initialize_simple()
