#!/usr/bin/env python3
"""
Apuskripti new_questions.json tarkistamiseen ja hyväksymiseen
"""
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime

# Lisää src hakemisto Python-polkuun
current_dir = Path(__file__).parent
src_dir = current_dir.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

def get_current_election():
    """Hae nykyinen vaali config tiedostosta"""
    config_file = Path("config.json")
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config.get('current_election')
        except:
            pass
    return "Jumaltenvaalit2026"  # Fallback

def review_new_questions():
    """Tarkista ja hyväksy uudet kysymykset"""
    
    current_election = get_current_election()
    
    if not current_election:
        print("❌ EI AKTIIVISTA VAAILIA")
        return
    
    data_path = Path("data/elections")
    election_path = data_path / current_election
    new_questions_file = election_path / "new_questions.json"
    questions_file = election_path / "questions.json"
    
    if not new_questions_file.exists():
        print("ℹ️  Ei uusia kysymyksiä odottamassa")
        return
    
    # Lataa uudet kysymykset
    try:
        with open(new_questions_file, 'r', encoding='utf-8') as f:
            new_questions = json.load(f)
    except Exception as e:
        print(f"❌ Virhe ladattaessa new_questions.json: {e}")
        return
    
    if not new_questions:
        print("ℹ️  Ei uusia kysymyksiä odottamassa")
        return
    
    print("📋 UUSIEN KYSYMYSTEN TARKISTUS")
    print("=" * 50)
    print(f"🏛️  Vaali: {current_election}")
    print(f"📊 Kysymyksiä tarkistettavana: {len(new_questions)}")
    print()
    
    approved_questions = []
    rejected_questions = []
    
    for i, question in enumerate(new_questions, 1):
        print(f"{i}. 📁 {question.get('category', 'Ei kategoriaa')}")
        print(f"   ❓ FI: {question.get('question_fi', '')}")
        print(f"   ❓ EN: {question.get('question_en', '')}")
        print(f"   ✅ Tarkistettu: {'Kyllä' if question.get('checked_for_duplicates') else 'Ei'}")
        
        response = input("   Hyväksytäänkö? (k/e/s = kyllä/ei/skip): ").lower()
        
        if response == 'k':
            question['status'] = 'approved'
            approved_questions.append(question)
            print("   ✅ HYVÄKSYTTY")
        elif response == 'e':
            question['status'] = 'rejected'
            rejected_questions.append(question)
            print("   ❌ HYLÄTTY")
        else:
            print("   ⏭️  OHITETTU")
        
        print("   " + "-" * 40)
    
    # Päivitä new_questions.json
    remaining_questions = [q for q in new_questions if q.get('status') not in ['approved', 'rejected']]
    
    with open(new_questions_file, 'w', encoding='utf-8') as f:
        json.dump(remaining_questions, f, ensure_ascii=False, indent=2)
    
    # Lisää hyväksytyt kysymykset questions.json tiedostoon
    if approved_questions:
        # Lataa nykyiset kysymykset
        existing_questions = {}
        questions_data = {}
        
        if questions_file.exists():
            try:
                with open(questions_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        data = json.loads(content)
                        
                        # Käsittele eri formaatteja
                        if isinstance(data, dict) and 'questions' in data:
                            # Dictionary jossa 'questions' kenttä
                            questions_list = data['questions']
                            if isinstance(questions_list, list):
                                for item in questions_list:
                                    if isinstance(item, dict) and 'id' in item:
                                        existing_questions[item['id']] = item
                        elif isinstance(data, list):
                            # Suora lista
                            for item in data:
                                if isinstance(item, dict) and 'id' in item:
                                    existing_questions[item['id']] = item
                        elif isinstance(data, dict):
                            # Suora dictionary
                            existing_questions = data
            except Exception as e:
                print(f"⚠️  Virhe ladattaessa olemassa olevia kysymyksiä: {e}")
                existing_questions = {}
        
        # Lisää uudet kysymykset
        for question in approved_questions:
            # Luo uniikki ID
            timestamp = datetime.now().isoformat()
            text_to_hash = f"{question['question_fi']}{timestamp}"
            question_id = f"q_{hashlib.md5(text_to_hash.encode()).hexdigest()[:8]}"
            
            # Lisää kysymys
            existing_questions[question_id] = {
                'id': question_id,
                'question_fi': question['question_fi'],
                'question_en': question['question_en'],
                'category': question['category'],
                'elo_rating': 1000,
                'created_at': timestamp,
                'updated_at': timestamp,
                'source': 'manual_review'
            }
        
        # Tallenna oikeassa formaatissa (dictionary jossa 'questions' kenttä)
        questions_data = {
            'questions': list(existing_questions.values())
        }
        
        # Tallenna
        with open(questions_file, 'w', encoding='utf-8') as f:
            json.dump(questions_data, f, ensure_ascii=False, indent=2)
        
        print(f"\\n✅ {len(approved_questions)} KYSYMYSTÄ HYVÄKSYTTY JA LISÄTTY QUESTIONS.JSON TIEDOSTOON!")
    
    if rejected_questions:
        print(f"\\n❌ {len(rejected_questions)} KYSYMYSTÄ HYLÄTTY")
    
    if remaining_questions:
        print(f"\\n⏳ {len(remaining_questions)} KYSYMYSTÄ JÄI ODOTTAMAAN")
    
    print(f"\\n📊 YHTEENVETO:")
    print(f"   ✅ Hyväksytyt: {len(approved_questions)}")
    print(f"   ❌ Hylätyt: {len(rejected_questions)}")
    print(f"   ⏳ Odottavat: {len(remaining_questions)}")

if __name__ == '__main__':
    review_new_questions()
