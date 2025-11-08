#!/usr/bin/env python3
# copy_questions_from_mock.py
"""
Kopioi kysymykset mock-IPFS:stä työasemaan
Käyttö: python copy_questions_from_mock.py
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

def copy_questions_from_mock():
    """Kopioi kysymykset mock-IPFS:stä työasemaan"""
    
    print("📥 KOPIOIDAAN KYSYMYKSIÄ MOCK-IPFS:STÄ...")
    print("=" * 50)
    
    # 1. Tarkista mock-IPFS data
    mock_file = Path("mock_ipfs_data.json")
    if not mock_file.exists():
        print("❌ mock_ipfs_data.json ei löydy")
        return False
    
    # 2. Lataa mock-data
    try:
        with open(mock_file, 'r', encoding='utf-8') as f:
            mock_data = json.load(f)
        
        print(f"✅ Mock-IPFS data ladattu: {len(mock_data)} CID:ä")
        
    except Exception as e:
        print(f"❌ Virhe ladattaessa mock-dataa: {e}")
        return False
    
    # 3. Etsi kysymysdata mock-datasta
    questions_data = None
    questions_cid = None
    
    for cid, data in mock_data.items():
        if "data" in data and "questions" in data["data"]:
            questions_data = data["data"]
            questions_cid = cid
            print(f"✅ Löytyi kysymysdata: {cid}")
            break
    
    if not questions_data:
        print("❌ Kysymysdataa ei löytynyt mock-IPFS:stä")
        return False
    
    # 4. Päivitä kysymysten aikaleimat (jotta suojaus ei estä vertailuja)
    current_time = datetime.now().isoformat()
    for question in questions_data.get("questions", []):
        if "timestamps" in question:
            question["timestamps"]["created_local"] = current_time
            question["timestamps"]["modified_local"] = current_time
    
    # 5. Tallenna kysymykset runtime/questions.json:ään
    runtime_questions_file = Path("runtime/questions.json")
    
    # Lataa nykyiset kysymykset (jos on)
    existing_questions = []
    if runtime_questions_file.exists():
        try:
            with open(runtime_questions_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                existing_questions = existing_data.get("questions", [])
            print(f"✅ Nykyiset kysymykset ladattu: {len(existing_questions)} kpl")
        except Exception as e:
            print(f"⚠️  Virhe ladattaessa nykyisiä kysymyksiä: {e}")
    
    # Yhdistä kysymykset
    all_questions = existing_questions.copy()
    new_questions = questions_data.get("questions", [])
    
    # Estä duplikaatit
    existing_ids = {q["local_id"] for q in existing_questions}
    added_count = 0
    
    for question in new_questions:
        if question["local_id"] not in existing_ids:
            all_questions.append(question)
            existing_ids.add(question["local_id"])
            added_count += 1
    
    # 6. Tallenna päivitetty questions.json
    questions_data_to_save = {
        "metadata": {
            "version": "2.0.0",
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "total_questions": len(all_questions),
            "source": f"mock_ipfs_{questions_cid}",
            "added_from_mock": added_count
        },
        "questions": all_questions
    }
    
    try:
        with open(runtime_questions_file, 'w', encoding='utf-8') as f:
            json.dump(questions_data_to_save, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Kysymykset tallennettu: {len(all_questions)} kysymystä")
        print(f"✅ Uusia kysymyksiä lisätty: {added_count} kpl")
        
    except Exception as e:
        print(f"❌ Virhe tallentaessa kysymyksiä: {e}")
        return False
    
    # 7. Päivitä myös new_questions.json synkronointia varten
    new_questions_file = Path("runtime/new_questions.json")
    try:
        new_questions_data = {
            "metadata": {
                "election_id": "Jumaltenvaalit_2026",
                "created": datetime.now().isoformat(),
                "source": "mock_ipfs_import"
            },
            "questions": new_questions[:10]  # Lisää vain osa moderointijonoon
        }
        
        with open(new_questions_file, 'w', encoding='utf-8') as f:
            json.dump(new_questions_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ New questions päivitetty: {len(new_questions_data['questions'])} kysymystä moderointijonoon")
        
    except Exception as e:
        print(f"⚠️  Virhe päivittäessä new_questions.json: {e}")
    
    # 8. Kirjaa system_chainiin
    try:
        from system_chain_manager import log_action
        log_action(
            "mock_questions_import",
            f"Kopioitu {added_count} kysymystä mock-IPFS:stä",
            question_ids=[q["local_id"] for q in new_questions[:5]],
            user_id="mock_importer",
            metadata={
                "mock_cid": questions_cid,
                "total_questions": len(all_questions),
                "added_count": added_count,
                "existing_count": len(existing_questions)
            }
        )
        print("✅ Import kirjattu system_chainiin")
    except ImportError:
        print("⚠️  System chain ei saatavilla - skipataan kirjaus")
    
    print(f"\n🎯 KYSYMYKSIÄ KOPIOITU ONNISTUNEESTI!")
    print("=" * 50)
    print(f"📊 YHTEENVETO:")
    print(f"   📥 Mock-IPFS CID: {questions_cid}")
    print(f"   📋 Kysymyksiä yhteensä: {len(all_questions)}")
    print(f"   🆕 Uusia lisätty: {added_count}")
    print(f"   📁 Tiedosto: {runtime_questions_file}")
    
    return True

def main():
    """Pääohjelma"""
    print("🔄 KYSYMYSTEN KOPIOINTI MOCK-IPFS:STÄ")
    print("=" * 60)
    print("Tämä skripti kopioi kysymykset mock-IPFS:stä työasemaan.")
    print("")
    
    # Tarkista että mock-data on olemassa
    if not Path("mock_ipfs_data.json").exists():
        print("❌ mock_ipfs_data.json ei löydy")
        print("💡 Varmista että mock-IPFS on käytössä ja sisältää dataa")
        return False
    
    # Kysy vahvistus
    response = input("Haluatko kopioida kysymykset mock-IPFS:stä? (K/e): ").strip().lower()
    
    if response in ['', 'k', 'kyllä', 'y', 'yes']:
        success = copy_questions_from_mock()
        if success:
            print(f"\n💡 TESTAA KYSYMYKSET:")
            print("python demo_comparisons.py --user testi --count 5")
            print("python manage_questions.py status")
        return success
    else:
        print("\n🔧 Kopiointi peruttu")
        return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
