#!/usr/bin/env python3
"""Yksinkertainen testi list_questions metodille"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    from managers.unified_question_handler import UnifiedQuestionHandler
    
    handler = UnifiedQuestionHandler()
    result = handler.list_questions(limit=3)
    
    if result.get('success'):
        print("✅ list_questions metodi toimii!")
        print(f"Löytyi {len(result['questions'])} kysymystä")
        for q in result['questions']:
            print(f" - {q['local_id']}: {q['content']['question']['fi'][:50]}...")
    else:
        print(f"❌ list_questions epäonnistui: {result.get('error')}")
        
except Exception as e:
    print(f"❌ Poikkeus: {e}")
    import traceback
    traceback.print_exc()
