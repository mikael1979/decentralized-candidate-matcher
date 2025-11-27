#!/usr/bin/env python3
"""
Parannettu kysymysten hallinta duplikaattitarkistuksella
"""
import sys
import json
import click
from pathlib import Path

# Lisää src hakemisto Python-polkuun
current_dir = Path(__file__).parent
src_dir = current_dir.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

try:
    from core.question_duplicate_checker import QuestionDuplicateChecker
except ImportError as e:
    print(f"❌ Import-virhe: {e}")
    sys.exit(1)

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

@click.group()
def cli():
    """Kysymysten hallinta duplikaattitarkistuksella"""
    pass

@cli.command()
@click.option('--category', required=True, help='Kysymyksen kategoria')
@click.option('--question-fi', required=True, help='Kysymys suomeksi')
@click.option('--question-en', required=True, help='Kysymys englanniksi')
@click.option('--force', is_flag=True, help='Ohita duplikaattitarkistus')
@click.option('--similarity-threshold', default=0.7, help='Samankaltaisuusraja (0.0-1.0)')
def add(category, question_fi, question_en, force, similarity_threshold):
    """Lisää uusi kysymys duplikaattitarkistuksen kautta"""
    
    print("🔍 LISÄTÄÄN UUSI KYSYMYS DUPLIKAATTITARKISTUKSEN KANSSA")
    print("=" * 60)
    
    # Hae nykyinen vaali
    current_election = get_current_election()
    
    if not current_election:
        print("❌ EI AKTIIVISTA VAAILIA - aseta current_election config.json tiedostoon")
        return
    
    checker = QuestionDuplicateChecker(current_election)
    
    print(f"🏛️  Vaali: {current_election}")
    print(f"📁 Kategoria: {category}")
    print(f"❓ Kysymys (FI): {question_fi}")
    print(f"❓ Kysymys (EN): {question_en}")
    print()
    
    if not force:
        # Suorita duplikaattitarkistus
        print("🔍 TARKISTETAAN DUPLIKAATIT...")
        duplicate_check = checker.check_duplicate(question_fi, question_en, category)
        
        # Näytä vertailu
        comparison = checker.format_comparison(question_fi, duplicate_check['similar_questions'])
        print(comparison)
        print()
        
        if duplicate_check['is_duplicate']:
            print(f"🚨 {duplicate_check['suggestion']}")
            print()
            print("💡 KÄYTTÖOHJEET:")
            print("   - Käytä --force ohittaaksesi tarkistus")
            print("   - Muokkaa kysymystä erilaiseksi")
            print("   - Tarkista olemassa olevat kysymykset: python src/cli/manage_questions.py --list")
            return
        
        if duplicate_check['similar_questions']:
            print(f"⚠️  {duplicate_check['suggestion']}")
            print()
            response = input("Haluatko jatkaa kysymyksen lisäystä? (k/e): ")
            if response.lower() not in ['k', 'kyllä', 'y', 'yes']:
                print("❌ Kysymyksen lisäys peruutettu")
                return
    
    # Lisää kysymys new_questions.json tiedostoon
    question_data = {
        'question_fi': question_fi,
        'question_en': question_en,
        'category': category,
        'status': 'pending_review'
    }
    
    if checker.save_to_new_questions(question_data, force=force):
        print("✅ KYSYMYS LISÄTTY NEW_QUESTIONS.JSON TIEDOSTOON!")
        print("   📁 Tiedosto: data/elections/{}/new_questions.json".format(current_election))
        print("   📋 Status: Odottaa tarkistusta")
        print()
        print("💡 SEURAAVAT VAIHEET:")
        print("   - Tarkista new_questions.json manuaalisesti")
        print("   - Siirrä hyväksytyt kysymykset questions.json tiedostoon")
        print("   - Käytä: python src/cli/manage_questions_enhanced.py list-new")
    else:
        print("❌ Kysymyksen tallentaminen epäonnistui")

@cli.command()
def list_new():
    """Listaa uudet kysymykset jotka odottavat tarkistusta"""
    
    current_election = get_current_election()
    
    if not current_election:
        print("❌ EI AKTIIVISTA VAAILIA")
        return
    
    data_path = Path("data/elections")
    new_questions_file = data_path / current_election / "new_questions.json"
    
    if not new_questions_file.exists():
        print("ℹ️  Ei uusia kysymyksiä odottamassa")
        return
    
    try:
        with open(new_questions_file, 'r', encoding='utf-8') as f:
            new_questions = json.load(f)
        
        print("📋 UUDET KYSYMYKSET (ODOTTAA TARKISTUSTA)")
        print("=" * 50)
        
        for i, question in enumerate(new_questions, 1):
            print(f"{i}. 📁 {question.get('category', 'Ei kategoriaa')}")
            print(f"   ❓ FI: {question.get('question_fi', '')}")
            print(f"   ❓ EN: {question.get('question_en', '')}")
            print(f"   📊 Tila: {question.get('status', 'unknown')}")
            if question.get('checked_for_duplicates'):
                print("   ✅ Duplikaattitarkistus suoritettu")
            print("   " + "-" * 40)
        
        print(f"📊 Yhteensä: {len(new_questions)} kysymystä odottamassa")
        
    except Exception as e:
        print(f"❌ Virhe ladattaessa new_questions.json: {e}")

@cli.command()
@click.option('--check-all', is_flag=True, help='Tarkista kaikki olemassa olevat kysymykset duplikaateista')
def check_duplicates(check_all):
    """Tarkista duplikaatit olemassa olevista kysymyksistä"""
    
    current_election = get_current_election()
    
    if not current_election:
        print("❌ EI AKTIIVISTA VAAILIA")
        return
    
    checker = QuestionDuplicateChecker(current_election)
    questions = checker.load_questions()
    
    print(f"🔍 TARKISTETAAN DUPLIKAATIT - {current_election}")
    print("=" * 60)
    
    if not questions:
        print("ℹ️  Ei kysymyksiä tarkistettavaksi")
        return
    
    all_questions = list(questions.items())
    duplicates_found = 0
    
    for i, (q_id, q_data) in enumerate(all_questions):
        if not isinstance(q_data, dict):
            continue
            
        fi_text = q_data.get('question_fi', '')
        if not fi_text:
            continue
        
        print(f"🔍 Tarkistetaan: {fi_text[:50]}...")
        
        # Vertaa kaikkiin muihin kysymyksiin
        for j, (other_id, other_data) in enumerate(all_questions):
            if i == j or not isinstance(other_data, dict):
                continue
                
            other_text = other_data.get('question_fi', '')
            if not other_text:
                continue
            
            similarity = checker.calculate_similarity(fi_text, other_text)
            
            if similarity > 0.8:  # Korkea samankaltaisuus
                duplicates_found += 1
                print(f"🚨 DUPLIKAATTI LÖYDETTY ({int(similarity*100)}% samankaltainen):")
                print(f"   📋 {q_id}: {fi_text}")
                print(f"   📋 {other_id}: {other_text}")
                print("   " + "-" * 40)
    
    if duplicates_found == 0:
        print("✅ EI DUPLIKAATTEJA LÖYDETTY!")
    else:
        print(f"🚨 LÖYDETTY {duplicates_found} DUPLIKAATTIA")

if __name__ == '__main__':
    cli()
