#!/usr/bin/env python3
"""
Demo script for Decentralized Candidate Matcher - Python Version
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from json_editor import JSONEditor

def run_demo():
    print("🚀 Decentralized Candidate Matcher - Python Demo\n")
    
    # Initialize editor
    editor = JSONEditor()
    
    # Load all data
    if not editor.load_all_data():
        print("⚠️  Some files failed to load, but continuing with demo...")
    
    # Validate consistency
    editor.validate_data_consistency()
    
    # Display initial stats
    editor.display_stats()
    
    # Demo: Add a new user question
    print('\n' + '='*50)
    print("📝 DEMO: Adding User Questions")
    print('='*50)
    
    new_question = editor.add_user_question({
        'category': {
            'fi': 'Liikenne',
            'sv': 'Trafik', 
            'en': 'Transportation'
        },
        'question': {
            'fi': 'Pitäisikö kaupunkipyörien määrää lisätä kesäkaudella?',
            'sv': 'Bör antalet stadscyklar ökas under sommarsäsongen?',
            'en': 'Should the number of city bikes be increased during summer season?'
        },
        'scale': {
            'min': -5,
            'max': 5,
            'labels': {
                'fi': {
                    '-5': 'Täysin eri mieltä',
                    '0': 'Neutraali',
                    '5': 'Täysin samaa mieltä'
                }
            }
        },
        'tags': {
            'fi': ['liikenne', 'kaupunkipyörät', 'kesä', 'kestävä liikenne'],
            'sv': ['trafik', 'stadscyklar', 'sommar', 'hållbar transport'],
            'en': ['transportation', 'city_bikes', 'summer', 'sustainable_mobility']
        },
        'user_comment': 'Kesäkaudella pyöräily on suosittua, joten tarvitaan enemmän pyöriä'
    })
    
    if new_question:
        # Demo: Add community votes
        print('\n' + '='*50)
        print("🗳️ DEMO: Community Voting")
        print('='*50)
        
        editor.add_community_vote(new_question['id'], {
            'vote': 'appropriate',
            'confidence': 0.8,
            'reasons': ['relevant', 'constructive'],
            'comments': 'Hyvä kysymys, liittyy ajankohtaiseen aiheeseen'
        })
        
        editor.add_community_vote(new_question['id'], {
            'vote': 'appropriate', 
            'confidence': 0.9,
            'reasons': ['clear_question', 'factual'],
            'comments': 'Erittäin hyvin muotoiltu kysymys'
        })
        
        editor.add_community_vote(new_question['id'], {
            'vote': 'inappropriate',
            'confidence': 0.3,
            'reasons': ['off_topic'],
            'comments': 'Ei liity tarpeeksi kunnallispolitiikkaan'
        })
        
        # Demo: Elo rating update
        print('\n' + '='*50)
        print("🎯 DEMO: Elo Rating System")
        print('='*50)
        
        # Add a second question for comparison
        second_question = editor.add_user_question({
            'category': {'fi': 'Ympäristö', 'en': 'Environment'},
            'question': {
                'fi': 'Pitäisikö kaupungin lisätä viheralueita?',
                'en': 'Should the city increase green areas?'
            },
            'scale': {
                'min': -5, 'max': 5,
                'labels': {'fi': {'-5': 'Täysin eri mieltä', '0': 'Neutraali', '5': 'Täysin samaa mieltä'}}
            },
            'tags': {'fi': ['ympäristö', 'viheralueet', 'luonto']}
        })
        
        if second_question:
            editor.update_elo_rating(new_question['id'], second_question['id'], 'question_a')
        
        # Demo: Add more votes to trigger auto-moderation
        print('\n' + '='*50)
        print("🤖 DEMO: Auto-Moderation")
        print('='*50)
        
        for i in range(8):
            editor.add_community_vote(new_question['id'], {
                'vote': 'appropriate',
                'confidence': 0.7 + (i * 0.03),
                'reasons': ['relevant', 'constructive']
            })
    
    # Demo: Search functionality
    print('\n' + '='*50)
    print("🔍 DEMO: Search Functionality")
    print('='*50)
    
    search_results = editor.search_questions('kaupunkipyörät')
    print(f"Found {len(search_results)} questions about 'kaupunkipyörät':")
    for q in search_results:
        status = q.get('community_moderation', {}).get('status', 'pending')
        print(f"  - {q['question']['fi']} ({status})")
    
    # Demo: Generate report
    print('\n' + '='*50)
    print("📈 DEMO: System Report")
    print('='*50)
    
    report = editor.generate_report()
    print("System Report:")
    print(f"- Total questions: {report['summary']['total_official_questions'] + report['summary']['total_user_questions']}")
    print(f"- Total votes: {report['summary']['total_votes']}")
    print(f"- Question statuses: {report['user_questions_by_status']}")
    print(f"- Average Elo rating: {report['average_elo']}")
    
    if report['top_questions']:
        print("\nTop Rated Questions:")
        for i, q in enumerate(report['top_questions'], 1):
            print(f"  {i}. {q['question'][:40]}... (Elo: {q['rating']})")
    
    # Save all data
    print('\n' + '='*50)
    print("💾 DEMO: Saving Data")
    print('='*50)
    
    if editor.save_all_data():
        print("🎉 Demo completed successfully!")
        
        # Final validation
        print('\n' + '='*50)
        print("🔍 Final Data Validation")
        print('='*50)
        editor.validate_data_consistency()
        
        # Display final stats
        editor.display_stats()
    else:
        print("❌ Some files failed to save")

if __name__ == "__main__":
    run_demo()
