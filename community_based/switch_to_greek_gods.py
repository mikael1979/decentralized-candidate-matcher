#!/usr/bin/env python3
# switch_to_greek_gods.py
"""
Vaihda aktiiviseksi vaaliksi Jumaltenvaalit 2026
Käyttö: python switch_to_greek_gods.py
"""

import json
import shutil
from pathlib import Path
import sys

def switch_to_greek_gods():
    """Vaihda Jumaltenvaalit aktiiviseksi"""
    
    print("🏛️  VAIHDETAAN KREIKKALAISIIN JUMALIIN...")
    print("=" * 50)
    
    # 1. Tarkista että Jumaltenvaalit on elections_list:ssä
    print("🔍 TARKISTETAAN JUMALTENVAALIT...")
    
    greek_election_found = False
    elections_files = [
        Path("elections_list.json"),
        Path("config_output/elections_list.json")
    ]
    
    for elections_file in elections_files:
        if elections_file.exists():
            try:
                with open(elections_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for election in data.get('elections', []):
                    if election.get('election_id') == 'Jumaltenvaalit_2026':
                        greek_election_found = True
                        print(f"✅ Jumaltenvaalit löytyy: {elections_file}")
                        break
                        
            except Exception as e:
                print(f"⚠️  Ei voitu lukea {elections_file}: {e}")
    
    if not greek_election_found:
        print("❌ Jumaltenvaalit eivät ole elections_list.json:ssa")
        print("💡 Luo vaali ensin: python create_install_config.py")
        return False
    
    # 2. Tuo testidata uudelleen
    print("\n🔄 TUODAAN JUMALTENVAALIEN DATA...")
    try:
        from import_test_data import TestDataImporter
        importer = TestDataImporter()
        importer.import_all_data()
        print("✅ Jumaltenvaalien data tuotu")
    except ImportError as e:
        print(f"❌ Data-tuonti epäonnistui: {e}")
        return False
    except Exception as e:
        print(f"❌ Data-tuonti epäonnistui: {e}")
        return False
    
    # 3. Päivitä metadata
    print("\n🔧 PÄIVITETÄÄN METADATAA...")
    
    meta_updates = {
        'runtime/meta.json': {
            'section': 'election',
            'updates': {
                'id': 'Jumaltenvaalit_2026',
                'name': {
                    'fi': 'Kreikkalaisten Jumalien Vaalit 2026',
                    'en': 'Greek Gods Election 2026',
                    'sv': 'Grekiska Gudarnas Val 2026'
                },
                'date': '2026-01-15',
                'type': 'divine_council'
            }
        },
        'runtime/system_metadata.json': {
            'section': 'election_specific', 
            'updates': {
                'election_id': 'Jumaltenvaalit_2026'
            }
        }
    }
    
    for file_path, config in meta_updates.items():
        file = Path(file_path)
        if file.exists():
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if config['section'] in data:
                    data[config['section']].update(config['updates'])
                    
                    with open(file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    
                    print(f"✅ Päivitetty: {file_path}")
                else:
                    print(f"⚠️  Osa {config['section']} puuttuu: {file_path}")
                    
            except Exception as e:
                print(f"❌ Päivitys epäonnistui {file_path}: {e}")
        else:
            print(f"ℹ️  Tiedostoa ei löydy: {file_path}")
    
    # 4. Päivitä system_chain
    chain_file = Path("runtime/system_chain.json")
    if chain_file.exists():
        try:
            with open(chain_file, 'r', encoding='utf-8') as f:
                chain_data = json.load(f)
            
            chain_data['chain_id'] = 'Jumaltenvaalit_2026'
            chain_data['description'] = 'Kreikkalaisten Jumalien Vaalit 2026'
            
            # Lisää vaihtolohko
            if 'blocks' in chain_data:
                new_block = {
                    "block_id": len(chain_data['blocks']),
                    "timestamp": __import__('datetime').datetime.now().isoformat(),
                    "description": "Vaihdettu Kreikkalaisiin Jumaliin",
                    "action_type": "system_switch",
                    "user_id": "switch_script"
                }
                chain_data['blocks'].append(new_block)
            
            with open(chain_file, 'w', encoding='utf-8') as f:
                json.dump(chain_data, f, indent=2, ensure_ascii=False)
            
            print("✅ System chain päivitetty")
            
        except Exception as e:
            print(f"⚠️  System chain päivitys epäonnistui: {e}")
    
    # 5. Varmista asennus
    print("\n✅ VAIHTO VALMIS!")
    print("=" * 50)
    print("🏛️  KREIKKALAISET JUMALAT AKTIVOITU")
    print("")
    print("📊 DATA-TILA:")
    
    try:
        with open('runtime/questions.json', 'r') as f:
            questions = json.load(f)
        print(f"   ❓ Kysymyksiä: {len(questions.get('questions', []))}")
    except:
        print("   ❓ Kysymyksiä: Tuntematon")
    
    try:
        with open('runtime/candidates.json', 'r') as f:
            candidates = json.load(f)
        print(f"   👑 Ehdokkaita: {len(candidates.get('candidates', []))}")
    except:
        print("   👑 Ehdokkaita: Tuntematon")
    
    try:
        with open('runtime/parties.json', 'r') as f:
            parties = json.load(f)
        print(f"   📋 Puolueita: {len(parties.get('parties', []))}")
    except:
        print("   📋 Puolueita: Tuntematon")
    
    print("")
    print("💡 TESTAA TOIMINTA:")
    print("   python install.py --verify")
    print("   python demo_comparisons.py --user zeus_test --count 3")
    print("   python test_elo_with_greek_gods.py")
    
    return True

def main():
    """Pääohjelma"""
    print("🎯 VAIHDA KREIKKALAISIIN JUMALIIN")
    print("=" * 60)
    print("Tämä skripti vaihtaa aktiiviseksi vaaliksi:")
    print("   🏛️  Kreikkalaisten Jumalien Vaalit 2026")
    print("")
    print("📋 TOIMINNOT:")
    print("   ✅ Tuo kreikkalaisten jumalien testidatan")
    print("   ✅ Päivittää kaiken metadata")
    print("   ✅ Varmistaa että kaikki tiedostot ovat kunnossa")
    print("")
    
    # Kysy vahvistus
    response = input("Haluatko varmasti vaihtaa Kreikkalaisiin Jumaliin? (K/e): ").strip().lower()
    
    if response in ['', 'k', 'kyllä', 'y', 'yes']:
        success = switch_to_greek_gods()
        if success:
            print("\n🎉 VAIHTO ONNISTUI!")
            return True
        else:
            print("\n❌ VAIHTO EPÄONNISTUI!")
            return False
    else:
        print("\n🔓 Vaihto peruttu")
        print("Nykyinen vaali säilyy")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
