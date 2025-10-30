# manage_questions.py
#!/usr/bin/env python3
"""
Kysymysten synkronointityökalu
"""

import argparse
from question_manager import get_question_manager

def main():
    parser = argparse.ArgumentParser(description="Kysymysten synkronointityökalu")
    parser.add_argument('action', choices=['sync', 'status', 'submit', 'rules', 'force-sync'],
                       help='Toiminto')
    parser.add_argument('--question-file', help='Kysymystiedosto (submit-toimintoa varten)')
    parser.add_argument('--batch-size', type=int, help='Aseta erän koko')
    parser.add_argument('--interval', type=int, help='Aseta aikaväli tunteina')
    
    args = parser.parse_args()
    manager = get_question_manager()
    
    if args.action == 'sync':
        result = manager.sync_tmp_to_new()
        if result['success']:
            print(f"✅ Synkronoitu {result['synced_count']} kysymystä")
        else:
            print(f"❌ Synkronointi epäonnistui: {result['error']}")
    
    elif args.action == 'status':
        status = manager.get_sync_status()
        print(f"📊 SYNKRONOINTITILA:")
        print(f"   Tmp-jonossa: {status['tmp_questions_count']} kysymystä")
        print(f"   Moderointijonossa: {status['new_questions_count']} kysymystä")
        print(f"   Edistyminen: {status['batch_size_progress']}")
        print(f"   Seuraava synkronointi: {status['next_sync_time']}")
        print(f"   Aikaa synkronointiin: {status['time_until_sync']}")
    
    elif args.action == 'force-sync':
        result = manager.sync_tmp_to_new(force=True)
        print(f"🚀 PAKOTETTU SYNKRONOINTI:")
        print(f"   Synkronoitu: {result['synced_count']} kysymystä")
        print(f"   Jäljellä tmp:ssä: {result['remaining_in_tmp']}")
    
    elif args.action == 'rules':
        if args.batch_size or args.interval:
            new_rules = {}
            if args.batch_size:
                new_rules['batch_size'] = args.batch_size
            if args.interval:
                new_rules['time_interval_hours'] = args.interval
            
            manager.update_sync_rules(new_rules)
            print("✅ Synkronointisäännöt päivitetty")
        
        status = manager.get_sync_status()
        print("📋 NYKYISET SÄÄNNÖT:")
        for rule, value in status['sync_rules'].items():
            print(f"   {rule}: {value}")

if __name__ == "__main__":
    main()
