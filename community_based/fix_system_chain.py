#!/usr/bin/env python3
"""
Korjaa system_chain integraation ELO-järjestelmään
"""

import json
import sys
from datetime import datetime
from datetime import timezone
from pathlib import Path

def update_system_chain(action_type: str, details: str, question_ids=None, user_id=None):
    """Päivitä system_chain uudella toimintalohkolla"""
    
    chain_file = "runtime/system_chain.json"
    
    try:
        with open(chain_file, 'r', encoding='utf-8') as f:
            chain_data = json.load(f)
    except FileNotFoundError:
        print("❌ system_chain.json ei löydy")
        return False
    
    # Luo uusi lohko
    new_block = {
        "block_id": len(chain_data["blocks"]),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "description": f"{action_type}: {details}",
        "action_type": action_type,
        "details": details,
        "user_id": user_id,
        "question_ids": question_ids or [],
        "machine_id": chain_data.get("machine_id", "unknown")
    }
    
    # Lisää lohko
    chain_data["blocks"].append(new_block)
    
    # Päivitä current_state
    chain_data["current_state"]["last_updated"] = new_block["timestamp"]
    chain_data["current_state"]["total_blocks"] = len(chain_data["blocks"])
    
    # Tallenna
    try:
        with open(chain_file, 'w', encoding='utf-8') as f:
            json.dump(chain_data, f, indent=2, ensure_ascii=False)
        print(f"✅ System_chain päivitetty: {action_type}")
        return True
    except Exception as e:
        print(f"❌ Virhe tallennettaessa: {e}")
        return False

def add_missing_blocks():
    """Lisää puuttuvat lohkot testitoiminnallisuuksista"""
    
    print("🔧 LISÄTÄÄN PUUTTUVAT LOHKOT SYSTEM_CHAINIIN...")
    
    # Testivertailut
    comparisons = [
        ("comparison", "A voittaa: Salama vs Merimatkat", ["q1", "q2"], "test_user"),
        ("comparison", "B voittaa: Merimatkat vs Manala", ["q2", "q3"], "test_user"), 
        ("comparison", "Tasapeli: Manala vs Rakkaus", ["q3", "q4"], "test_user"),
        ("comparison", "A voittaa: Salama vs Rakkaus", ["q1", "q4"], "test_user"),
        ("comparison", "B voittaa: Merimatkat vs Rakkaus", ["q2", "q4"], "test_user")
    ]
    
    # Testiäänestykset
    votes = [
        ("vote", "Upvote: Salama (luottamus 5)", ["q1"], "demo_voter_1"),
        ("vote", "Downvote: Merimatkat (luottamus 4)", ["q2"], "demo_voter_2"),
        ("vote", "Upvote: Manala (luottamus 3)", ["q3"], "demo_voter_3"),
        ("vote", "Downvote: Rakkaus (luottamus 2)", ["q4"], "demo_voter_4"),
        ("vote", "Upvote: Salama (luottamus 1)", ["q1"], "demo_voter_5")
    ]
    
    # Lisää kaikki lohkot
    all_actions = comparisons + votes
    
    for action_type, details, question_ids, user_id in all_actions:
        success = update_system_chain(action_type, details, question_ids, user_id)
        if not success:
            print(f"❌ Epäonnistui: {details}")
            return False
    
    return True

def show_chain_status():
    """Näytä system_chainin nykytila"""
    
    try:
        with open('runtime/system_chain.json', 'r', encoding='utf-8') as f:
            chain = json.load(f)
        
        print("\n🔗 SYSTEM_CHAIN NYKYTILA:")
        print("=" * 50)
        print(f"Ketju ID: {chain['chain_id']}")
        print(f"Kone ID: {chain.get('machine_id', 'Ei määritelty')}")
        print(f"Lohkoja yhteensä: {len(chain['blocks'])}")
        print(f"Viimeisin päivitys: {chain['current_state'].get('last_updated', 'Ei tietoa')}")
        
        print(f"\n📊 LOHKOT:")
        for block in chain['blocks']:
            action_icon = "🔄" if block['action_type'] == 'comparison' else "🗳️" if block['action_type'] == 'vote' else "⚙️"
            print(f"  {action_icon} {block['block_id']}: {block['description']}")
            
    except FileNotFoundError:
        print("❌ system_chain.json ei löydy")
    except Exception as e:
        print(f"❌ Virhe: {e}")

def main():
    """Pääohjelma"""
    print("🔄 KORJATAAN SYSTEM_CHAIN INTEGRAATIO")
    print("=" * 50)
    
    # 1. Näytä nykytila
    show_chain_status()
    
    # 2. Lisää puuttuvat lohkot
    print(f"\n📝 LISÄTÄÄN TESTILOHKOT...")
    success = add_missing_blocks()
    
    # 3. Näytä päivitetty tila
    show_chain_status()
    
    if success:
        print(f"\n🎉 SYSTEM_CHAIN KORJATTU ONNISTUNEESTI!")
        print("Nyt kaikki vertailut ja äänestykset tallennetaan ketjuun.")
    else:
        print(f"\n⚠️  SYSTEM_CHAIN KORJAUS EPÄONNISTUI")

if __name__ == "__main__":
    main()
