# demo_auto_sync.py
#!/usr/bin/env python3
"""
Demo: Automaattinen synkronointi
"""

import time
import json
from datetime import datetime
from question_manager import get_question_manager

def demo_auto_sync():
    """Näytä automaattisen synkronoinnin toiminta"""
    
    manager = get_question_manager()
    
    print("🚀 AUTOMAATTINEN SYNKRONOINTI - DEMO")
    print("=" * 50)
    
    # 1. Näytä alkuperäinen tila
    status = manager.get_sync_status()
    print(f"Aloitustila: {status['tmp_questions_count']} kysymystä tmp-jonossa")
    
    # 2. Lisää testikysymyksiä
    test_questions = [
        {
            "content": {
                "category": {"fi": "Testi", "en": "Test", "sv": "Test"},
                "question": {"fi": f"Testikysymys {i}", "en": f"Test question {i}", "sv": f"Testfråga {i}"},
                "tags": ["test", "demo"]
            }
        }
        for i in range(8)  # Lisää 8 kysymystä (yli batch_size 5)
    ]
    
    print(f"\n📝 Lisätään {len(test_questions)} testikysymystä...")
    
    for i, question_data in enumerate(test_questions):
        result = manager.submit_question(question_data, f"demo_user_{i}")
        if result['auto_synced']:
            print(f"  {i+1}. ✅ AUTO-SYNCRONOITU! (Erä: {result['sync_result']['batch_id']})")
        else:
            print(f"  {i+1}. ⏳ Jonossa (sijainti: {result['queue_position']})")
        
        time.sleep(0.5)  # Pieni viive visualisoinnille
    
    # 3. Näytä lopputila
    final_status = manager.get_sync_status()
    print(f"\n🎯 LOPPUTILA:")
    print(f"   Tmp-jonossa: {final_status['tmp_questions_count']} kysymystä")
    print(f"   Moderointijonossa: {final_status['new_questions_count']} kysymystä")
    print(f"   Seuraava synkronointi: {final_status['next_sync_time']}")

if __name__ == "__main__":
    demo_auto_sync()
