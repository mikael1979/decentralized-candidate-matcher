#!/usr/bin/env python3
# fix_worker_installation.py
"""
Korjaa työasema-asennuksen ongelmat
Käyttö: python fix_worker_installation.py
"""

import json
import shutil
from datetime import datetime
from pathlib import Path

def fix_worker_installation():
    """Korjaa työasema-asennuksen puuttuvat tiedostot"""
    
    print("🔧 KORJATAAN TYÖASEMA-ASENNUS...")
    print("=" * 50)
    
    runtime_dir = Path("runtime")
    
    # 1. Tarkista että elections_list on olemassa
    elections_file = Path("config_output/elections_list.json")
    if not elections_file.exists():
        print("❌ elections_list.json ei löydy config_output-hakemistosta")
        return False
    
    # 2. Lataa vaalin tiedot
    try:
        with open(elections_file, 'r', encoding='utf-8') as f:
            elections_data = json.load(f)
        
        # Etsi aktiivinen vaali
        active_election = None
        for election in elections_data.get('elections', []):
            if election.get('election_id') == 'Jumaltenvaalit_2026':
                active_election = election
                break
        
        if not active_election:
            print("❌ Jumaltenvaalit_2026 ei löydy elections_list.json:stä")
            return False
            
        print(f"✅ Löytyi vaali: {active_election['name']['fi']}")
        
    except Exception as e:
        print(f"❌ Virhe ladattaessa elections_list.json: {e}")
        return False
    
    # 3. Luo puuttuvat tiedostot
    print("\n📁 LUODAAN PUITTUVAT TIEDOSTOT...")
    
    # Luo meta.json
    meta_data = {
        "election": {
            "id": active_election["election_id"],
            "name": active_election["name"],
            "date": active_election["dates"][0]["date"],
            "type": active_election["type"],
            "timelock_enabled": active_election["timelock_enabled"],
            "edit_deadline": active_election["edit_deadline"],
            "grace_period_hours": active_election["grace_period_hours"],
            "governance_model": "community_driven"
        },
        "system_info": {
            "system_id": f"system_{active_election['election_id']}",
            "created": datetime.now().isoformat(),
            "machine_id": "worker_fixed_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        },
        "version": "1.0.0"
    }
    
    with open(runtime_dir / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta_data, f, indent=2, ensure_ascii=False)
    print("✅ Luotu: meta.json")
    
    # Luo system_metadata.json
    system_metadata = {
        "election_specific": {
            "election_id": active_election["election_id"],
            "election_name": active_election["name"]["fi"],
            "machine_id": "worker_fixed",
            "installed_at": datetime.now().isoformat(),
            "first_install": False
        },
        "node_info": {
            "node_id": "worker_node",
            "role": "worker",
            "capabilities": ["comparisons", "voting", "sync"]
        },
        "version": "1.0.0"
    }
    
    with open(runtime_dir / "system_metadata.json", "w", encoding="utf-8") as f:
        json.dump(system_metadata, f, indent=2, ensure_ascii=False)
    print("✅ Luotu: system_metadata.json")
    
    # 4. Päivitä system_chain
    system_chain_file = runtime_dir / "system_chain.json"
    if system_chain_file.exists():
        try:
            with open(system_chain_file, 'r', encoding='utf-8') as f:
                chain_data = json.load(f)
            
            chain_data['chain_id'] = active_election['election_id']
            chain_data['description'] = f"Vaalijärjestelmä: {active_election['name']['fi']} (korjattu)"
            
            with open(system_chain_file, 'w', encoding='utf-8') as f:
                json.dump(chain_data, f, indent=2, ensure_ascii=False)
            
            print("✅ Päivitetty: system_chain.json")
            
        except Exception as e:
            print(f"⚠️  System chain päivitys epäonnistui: {e}")
    else:
        # Luo system_chain jos se puuttuu
        system_chain = {
            "chain_id": active_election["election_id"],
            "created_at": datetime.now().isoformat(),
            "description": f"Vaalijärjestelmä: {active_election['name']['fi']} (korjattu työasema)",
            "version": "1.0.0",
            "blocks": [
                {
                    "block_id": 0,
                    "timestamp": datetime.now().isoformat(),
                    "description": "Työasema-asennus korjattu",
                    "fix_applied": True
                }
            ],
            "current_state": {
                "last_updated": datetime.now().isoformat(),
                "total_blocks": 1,
                "election_id": active_election["election_id"]
            }
        }
        
        with open(system_chain_file, 'w', encoding='utf-8') as f:
            json.dump(system_chain, f, indent=2, ensure_ascii=False)
        print("✅ Luotu: system_chain.json")
    
    # 5. Tarkista kaikki tiedostot
    print("\n🔍 TARKISTETAAN TIEDOSTOT...")
    required_files = [
        'meta.json',
        'system_metadata.json',
        'system_chain.json',
        'questions.json',
        'candidates.json',
        'new_questions.json',
        'active_questions.json'
    ]
    
    all_ok = True
    for file in required_files:
        if (runtime_dir / file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} (puuttuu)")
            all_ok = False
    
    if all_ok:
        print("\n🎯 TYÖASEMA-ASENNUS KORJATTU ONNISTUNEESTI!")
        print("💡 Testaa järjestelmä:")
        print("   python system_bootstrap.py")
        print("   python manage_questions.py status")
        print("   python demo_comparisons.py --user testi --count 2")
        return True
    else:
        print("\n⚠️  Jotkin tiedostot puuttuvat - käytä import_test_data.py")
        return False

def main():
    """Pääohjelma"""
    print("🔧 TYÖASEMA-ASENNUKSEN KORJAUS")
    print("=" * 60)
    print("Tämä skripti korjaa työasema-asennuksen puuttuvat tiedostot.")
    print("Suorita tämä, jos työasema-asennus ei luonut kaikkia tarvittavia tiedostoja.")
    print("")
    
    # Tarkista runtime-hakemisto
    if not Path("runtime").exists():
        print("❌ Runtime-hakemisto puuttuu - suorita asennus ensin")
        return False
    
    # Kysy vahvistus
    response = input("Haluatko korjata työasema-asennuksen? (K/e): ").strip().lower()
    
    if response in ['', 'k', 'kyllä', 'y', 'yes']:
        success = fix_worker_installation()
        return success
    else:
        print("\n🔧 Korjaus peruttu")
        return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
