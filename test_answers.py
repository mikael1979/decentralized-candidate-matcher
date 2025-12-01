#!/usr/bin/env python3
"""
Testaa vastausten importit.
"""
import sys

# Lisää projektin juuri Python-polkuun
project_root = '/home/toni/Ohjelmointi/HajautettuVaalikone/decentralized-candidate-matcher'
sys.path.insert(0, project_root)

try:
    # Testaa importit
    from cli.answers.managers import AnswerManager
    from cli.answers.models import Answer
    
    print("✅ Imports work!")
    
    # Testaa Answer-luokka
    answer = Answer.create_new(
        candidate_id='test_candidate',
        question_id='test_question',
        value=3,
        confidence=0.8,
        explanation_fi='Testi selitys'
    )
    print(f"✅ Answer created: {answer.id}")
    
    # Testaa AnswerManager
    manager = AnswerManager('Jumaltenvaalit2026')
    print(f"✅ Manager created: {manager.election_id}")
    
    # Listaa vastaukset
    answers = manager.list_answers()
    print(f"✅ Found {len(answers)} answers")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
