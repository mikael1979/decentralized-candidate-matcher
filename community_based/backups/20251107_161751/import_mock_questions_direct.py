#!/usr/bin/env python3
# import_mock_questions_direct.py
"""
Tuo kysymyksiä suoraan mock-IPFS:stä käyttäen olemassa olevaa testidataa
"""

import json
from datetime import datetime
from pathlib import Path

def import_mock_questions_direct():
    """Tuo kysymyksiä suoraan mock-IPFS:stä"""
    
    print("📥 TUODAAN KYSYMYKSIÄ MOCK-IPFS:STÄ...")
    print("=" * 50)
    
    # 1. Tarkista että questions.test.json on olemassa
    test_file = Path("questions.test.json")
    if not test_file.exists():
        print("❌ questions.test.json ei löydy")
        print("💡 Tiedosto pitää olla samassa hakemistossa")
        return False
    
    # 2. Lataa testidata
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            test_data = json.load(f)
        
        questions = test_data.get("questions", [])
        print(f"✅ Testidata ladattu: {len(questions)} kysymystä")
        
    except Exception as e:
        print(f"❌ Virhe ladattaessa testidataa: {e}")
        return False
    
    # 3. Päivitä aikaleimat
    current_time = datetime.now().isoformat()
    for question in questions:
        if "timestamps" not in question:
            question["timestamps"] = {}
        question["timestamps"]["created_local"] = current_time
        question["timestamps"]["modified_local"] = current_time
    
    # 4. Tallenna runtime/questions.json:ään
    runtime_file = Path("runtime/questions.json")
    
    # Lataa nykyiset kysymykset
    existing_questions = []
    if runtime_file.exists():
        try:
            with open(runtime_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                existing_questions = existing_data.get("questions", [])
            print(f"✅ Nykyiset kysymykset ladattu: {len(existing_questions)} kpl")
        except Exception as e:
            print(f"⚠️  Virhe ladattaessa nykyisiä kysymyksiä: {e}")
    
    # Yhdistä kysymykset (estä duplikaatit)
    existing_ids = {q["local_id"] for q in existing_questions}
    added_count = 0
    all_questions = existing_questions.copy()
    
    for question in questions:
        if question["local_id"] not in existing_ids:
            all_questions.append(question)
            existing_ids.add(question["local_id"])
            added_count += 1
    
    # 5. Tallenna päivitetty tiedosto
    output_data = {
        "metadata": {
            "version": "2.0.0",
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "total_questions": len(all_questions),
            "source": "mock_ipfs_direct_import",
            "added_from_mock": added_count
        },
        "questions": all_questions
    }
    
    try:
        with open(runtime_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Kysymykset tallennettu: {len(all_questions)} kysymystä")
        print(f"✅ Uusia kysymyksiä lisätty: {added_count} kpl")
        
    except Exception as e:
        print(f"❌ Virhe tallentaessa kysymyksiä: {e}")
        return False
    
    # 6. Kirjaa system_chainiin
    try:
        from system_chain_manager import log_action
        log_action(
            "direct_mock_import",
            f"Tuotu {added_count} kysymystä suoraan mock-IPFS:stä",
            question_ids=[q["local_id"] for q in questions[:5]],
            user_id="direct_importer",
            metadata={
                "source_file": "questions.test.json",
                "total_questions": len(all_questions),
                "added_count": added_count
            }
        )
        print("✅ Import kirjattu system_chainiin")
    except ImportError:
        print("⚠️  System chain ei saatavilla - skipataan kirjaus")
    
    print(f"\n🎯 KYSYMYKSIÄ TUOTU ONNISTUNEESTI!")
    print("=" * 50)
    print(f"📊 YHTEENVETO:")
    print(f"   📁 Lähdetiedosto: {test_file}")
    print(f"   📋 Kysymyksiä yhteensä: {len(all_questions)}")
    print(f"   🆕 Uusia lisätty: {added_count}")
    
    return True

def main():
    """Pääohjelma"""
    print("🔄 SUORA MOCK-KYSYMYSTEN TUONTI")
    print("=" * 60)
    
    if not Path("questions.test.json").exists():
        print("❌ questions.test.json ei löydy")
        print("💡 Tarvitset testidata-tiedoston toimiaksesi")
        return False
    
    response = input("Haluatko tuoda kysymyksiä questions.test.json:sta? (K/e): ").strip().lower()
    
    if response in ['', 'k', 'kyllä', 'y', 'yes']:
        success = import_mock_questions_direct()
        if success:
            print(f"\n💡 TESTAA KYSYMYKSET:")
            print("python demo_comparisons.py --user testi --count 10")
            print("python manage_questions.py status")
        return success
    else:
        print("\n🔧 Tuonti peruttu")
        return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
