#!/usr/bin/env python3
# clean_test_election_complete.py
"""
Täydellinen testivaalien puhdistus
Käyttö: python clean_test_election_complete.py
"""

import json
import shutil
from pathlib import Path
import sys

def clean_completely():
    """Siivoa testivaalit kokonaan järjestelmästä"""
    
    print("🧹 SIIVOTAAN TESTIVAALIT KOKONAAN...")
    print("=" * 50)
    
    # 1. Poista config_output:sta
    config_file = Path("config_output/elections_list.json")
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            original_count = len(data.get('elections', []))
            data['elections'] = [e for e in data.get('elections', []) if e.get('election_id') != 'testivaalit_2026']
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Config output: {original_count} → {len(data['elections'])} vaalia")
            
        except Exception as e:
            print(f"❌ Config output puhdistus epäonnistui: {e}")
    else:
        print("ℹ️  Config output tiedostoa ei löydy")
    
    # 2. Päivitä metadata Jumaltenvaaleihin
    print("\n🔧 PÄIVITETÄÄN METADATAA...")
    
    meta_files = [
        ('runtime/meta.json', 'election'),
        ('runtime/system_metadata.json', 'election_specific')
    ]
    
    for meta_file, section in meta_files:
        file_path = Path(meta_file)
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    meta_data = json.load(f)
                
                # Päivitä election_id
                if section in meta_data:
                    meta_data[section]['id'] = 'Jumaltenvaalit_2026'
                    
                    # Päivitä myös nimi jos saatavilla
                    if section == 'election':
                        meta_data[section]['name'] = {
                            'fi': 'Kreikkalaisten Jumalien Vaalit 2026',
                            'en': 'Greek Gods Election 2026', 
                            'sv': 'Grekiska Gudarnas Val 2026'
                        }
                        meta_data[section]['date'] = '2026-01-15'
                        meta_data[section]['type'] = 'divine_council'
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(meta_data, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Päivitetty: {meta_file}")
                
            except Exception as e:
                print(f"⚠️  Ei voitu päivittää {meta_file}: {e}")
        else:
            print(f"ℹ️  {meta_file} ei löydy")
    
    # 3. Päivitä system_chain
    chain_file = Path("runtime/system_chain.json")
    if chain_file.exists():
        try:
            with open(chain_file, 'r', encoding='utf-8') as f:
                chain_data = json.load(f)
            
            chain_data['chain_id'] = 'Jumaltenvaalit_2026'
            chain_data['description'] = 'Kreikkalaisten Jumalien Vaalit 2026 - System Chain'
            
            with open(chain_file, 'w', encoding='utf-8') as f:
                json.dump(chain_data, f, indent=2, ensure_ascii=False)
            
            print("✅ System chain päivitetty Jumaltenvaaleihin")
            
        except Exception as e:
            print(f"⚠️  System chain päivitys epäonnistui: {e}")
    
    # 4. Tuo Jumaltenvaalien data uudelleen
    print("\n🔄 TUODAAN JUMALTENVAALIEN DATA...")
    try:
        from import_test_data import TestDataImporter
        importer = TestDataImporter()
        importer.import_all_data()
        print("✅ Jumaltenvaalien data tuotu")
    except ImportError as e:
        print(f"❌ Data-tuonti epäonnistui - import_test_data ei saatavilla: {e}")
    except Exception as e:
        print(f"❌ Data-tuonti epäonnistui: {e}")
    
    # 5. Varmista että tiedostot ovat olemassa
    print("\n📁 VARMISTETAAN TIEDOSTOT...")
    required_files = [
        'runtime/questions.json',
        'runtime/candidates.json', 
        'runtime/parties.json',
        'runtime/meta.json',
        'runtime/system_chain.json'
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            # Tarkista sisältö
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if 'questions' in data:
                    print(f"✅ {file_path}: {len(data['questions'])} kysymystä")
                elif 'candidates' in data:
                    print(f"✅ {file_path}: {len(data['candidates'])} ehdokasta")
                elif 'parties' in data:
                    print(f"✅ {file_path}: {len(data['parties'])} puoluetta")
                else:
                    print(f"✅ {file_path}: OK")
                    
            except Exception as e:
                print(f"⚠️  {file_path}: Virhe lukemisessa - {e}")
        else:
            print(f"❌ {file_path}: PUUTTUU")
    
    print("\n🎯 TESTIVAALIT POISTETTU ONNISTUNEESTI!")
    
    # 6. Näytä lopputila
    print("\n" + "=" * 50)
    print("📊 LOPPUTILA:")
    
    try:
        with open('runtime/meta.json', 'r', encoding='utf-8') as f:
            meta = json.load(f)
        print(f"🏛️  Aktiivinen vaali: {meta['election']['name']['fi']}")
        print(f"   ID: {meta['election']['id']}")
    except:
        print("🏛️  Aktiivinen vaali: Tuntematon")
    
    try:
        with open('runtime/questions.json', 'r', encoding='utf-8') as f:
            questions = json.load(f)
        print(f"❓ Kysymyksiä: {len(questions.get('questions', []))}")
    except:
        print("❓ Kysymyksiä: Tuntematon")
    
    try:
        with open('runtime/candidates.json', 'r', encoding='utf-8') as f:
            candidates = json.load(f)
        print(f"👑 Ehdokkaita: {len(candidates.get('candidates', []))}")
    except:
        print("👑 Ehdokkaita: Tuntematon")
    
    print("=" * 50)
    print("\n💡 TESTAA TOIMINTA:")
    print("   python install.py --verify")
    print("   python demo_comparisons.py --user testi --count 2")
    print("   python manage_questions.py status")

def main():
    """Pääohjelma"""
    print("🎯 TESTIVAALIEN TÄYDELLINEN PUHDISTUS")
    print("=" * 60)
    print("Tämä skripti poistaa testivaalit ja aktivoi Jumaltenvaalit")
    print("")
    
    # Kysy vahvistus
    response = input("Haluatko varmasti siivota testivaalit? (K/e): ").strip().lower()
    
    if response in ['', 'k', 'kyllä', 'y', 'yes']:
        clean_completely()
        return True
    else:
        print("\n🔓 Puhdistus peruttu")
        print("Testivaalit säilytetään")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
