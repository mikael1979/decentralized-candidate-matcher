#!/usr/bin/env python3
# sync_questions_from_master.py
"""
Synkronoi kysymykset master-koneen mock-IPFS:stä työasemalle
Käyttö: python sync_questions_from_master.py
"""

import json
import shutil
from datetime import datetime
from pathlib import Path

def sync_questions_from_master():
    """Synkronoi kysymykset master-koneelta"""
    
    print("🔄 SYNKRONOIDAAN KYSYMYKSIÄ MASTER-KONEELTA...")
    print("=" * 50)
    
    # 1. Tarkista että masterin mock-data on saatavilla
    master_mock_file = Path("mock_ipfs_data.master.json")
    if not master_mock_file.exists():
        print("❌ mock_ipfs_data.master.json ei löydy")
        print("💡 Kopioi master-koneelta: mock_ipfs_data.json -> mock_ipfs_data.master.json")
        return False
    
    # 2. Korvaa paikallinen mock-data masterin datalla
    try:
        shutil.copy2(master_mock_file, "mock_ipfs_data.json")
        print("✅ Masterin mock-IPFS data kopioitu työasemalle")
    except Exception as e:
        print(f"❌ Virhe kopioidessa mock-dataa: {e}")
        return False
    
    # 3. Lataa masterin data
    try:
        with open("mock_ipfs_data.json", 'r', encoding='utf-8') as f:
            mock_data = json.load(f)
        
        print(f"✅ Masterin mock-data ladattu: {len(mock_data)} CID:ä")
        
    except Exception as e:
        print(f"❌ Virhe ladattaessa mock-dataa: {e}")
        return False
    
    # 4. Etsi kysymysdata
    questions_data = None
    questions_cid = None
    
    for cid, data in mock_data.items():
        content = data.get('data', {})
        if 'questions' in content:
            questions_data = content
            questions_cid = cid
            questions_count = len(content.get('questions', []))
            print(f"✅ Löytyi kysymysdata: {cid} - {questions_count} kysymystä")
            break
    
    if not questions_data:
        print("❌ Kysymysdataa ei löytynyt masterin mock-IPFS:stä")
        print("💡 Varmista että master-koneella on suoritettu: python manage_questions.py sync")
        return False
    
    # 5. Päivitä kysymysten aikaleimat
    current_time = datetime.now().isoformat()
    for question in questions_data.get("questions", []):
        if "timestamps" in question:
            question["timestamps"]["created_local"] = current_time
            question["timestamps"]["modified_local"] = current_time
    
    # 6. Tallenna kysymykset työaseman runtime/questions.json:ään
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
    master_questions = questions_data.get("questions", [])
    added_count = 0
    all_questions = existing_questions.copy()
    
    for question in master_questions:
        if question["local_id"] not in existing_ids:
            all_questions.append(question)
            existing_ids.add(question["local_id"])
            added_count += 1
    
    # 7. Tallenna päivitetty tiedosto
    output_data = {
        "metadata": {
            "version": "2.0.0",
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "total_questions": len(all_questions),
            "source": "master_sync",
            "master_cid": questions_cid,
            "added_from_master": added_count,
            "existing_count": len(existing_questions)
        },
        "questions": all_questions
    }
    
    try:
        with open(runtime_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Kysymykset synkronoitu master-koneelta!")
        print(f"📊 YHTEENVETO:")
        print(f"   📥 Master-CID: {questions_cid}")
        print(f"   📋 Kysymyksiä yhteensä: {len(all_questions)}")
        print(f"   🆕 Uusia lisätty: {added_count}")
        print(f"   📁 Tiedosto: {runtime_file}")
        
    except Exception as e:
        print(f"❌ Virhe tallentaessa kysymyksiä: {e}")
        return False
    
    # 8. Kirjaa system_chainiin
    try:
        from system_chain_manager import log_action
        log_action(
            "master_sync",
            f"Synkronoitu {added_count} kysymystä master-koneelta",
            question_ids=[q["local_id"] for q in master_questions[:5]],
            user_id="sync_worker",
            metadata={
                "master_cid": questions_cid,
                "total_questions": len(all_questions),
                "added_count": added_count,
                "master_questions_count": len(master_questions)
            }
        )
        print("✅ Synkronointi kirjattu system_chainiin")
    except ImportError:
        print("⚠️  System chain ei saatavilla - skipataan kirjaus")
    
    return True

def main():
    """Pääohjelma"""
    print("🔄 MASTER-KONEEN SYNKRONOINTI TYÖASEMALLE")
    print("=" * 60)
    print("Tämä skripti synkronoi kysymykset master-koneen mock-IPFS:stä työasemalle.")
    print("")
    print("📋 EDELTYYS:")
    print("1. Master-koneella: python manage_questions.py sync")
    print("2. Kopioi master-koneelta: mock_ipfs_data.json -> mock_ipfs_data.master.json") 
    print("3. Siirrä mock_ipfs_data.master.json työasemalle")
    print("4. Työasemalla: python sync_questions_from_master.py")
    print("")
    
    if not Path("mock_ipfs_data.master.json").exists():
        print("❌ mock_ipfs_data.master.json ei löydy")
        print("💡 Tarvitset master-koneen mock-IPFS datan toimiaksesi")
        return False
    
    response = input("Haluatko synkronoida kysymykset master-koneelta? (K/e): ").strip().lower()
    
    if response in ['', 'k', 'kyllä', 'y', 'yes']:
        success = sync_questions_from_master()
        if success:
            print(f"\n💡 TESTAA SYNKRONOIDUT KYSYMYKSET:")
            print("python demo_comparisons.py --user worker --count 3")
            print("python manage_questions.py status")
        return success
    else:
        print("\n🔧 Synkronointi peruttu")
        return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
