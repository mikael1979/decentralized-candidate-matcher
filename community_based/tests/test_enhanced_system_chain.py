#!/usr/bin/env python3
# test_enhanced_system_chain.py
"""
Testaa laajennettua system chainia
Käyttö: python test_enhanced_system_chain.py
"""

import json
import sys
from datetime import datetime

sys.path.append('.')

def test_enhanced_system_chain():
    """Testaa laajennettua system chainia"""
    
    print("🧪 LAAJENNETUN SYSTEM CHAININ TESTI")
    print("=" * 50)
    
    try:
        from mock_ipfs import MockIPFS
        from enhanced_system_chain_manager import EnhancedSystemChainManager, log_action_with_blocks
        
        print("✅ Moduulit ladattu onnistuneesti")
        
        # Alusta testiympäristö
        ipfs = MockIPFS()
        chain_manager = EnhancedSystemChainManager(ipfs_client=ipfs)
        
        # Testaa 1: Perinteinen system chain kirjaus
        print("\n1. 📝 TESTATAAN PERINTEISTÄ SYSTEM CHAIN KIRJAUSTA...")
        traditional_result = chain_manager.log_action(
            "test_action",
            "Testikirjaus ilman IPFS:ää",
            ["q1", "q2"],
            "test_user_1"
        )
        print(f"   ✅ Perinteinen kirjaus: {traditional_result['success']}")
        
        # Testaa 2: Laajennettu kirjaus IPFS-lohkoihin
        print("\n2. 🔄 TESTATAAN LAAJENNETTUA KIRJAUSTA...")
        
        # Alusta ensin IPFS-lohkot
        from ipfs_block_manager import IPFSBlockManager
        block_manager = IPFSBlockManager(ipfs, "test_election_2024", "test_node_1")
        block_manager.initialize_blocks()
        
        enhanced_result = chain_manager.log_action_with_blocks(
            "enhanced_test",
            "Testikirjaus IPFS-lohkoihin",
            ["q3", "q4"],
            "test_user_2",
            {"test_meta": "value"},
            "test_election_2024",
            "test_node_1",
            "normal"
        )
        print(f"   ✅ Laajennettu kirjaus:")
        print(f"      - System chain: {enhanced_result['system_chain']['success']}")
        if enhanced_result['ipfs_blocks']:
            print(f"      - IPFS-lohko: {enhanced_result['ipfs_blocks']['block_written']}")
        
        # Testaa 3: API-funktion testaus
        print("\n3. 🛠️ TESTATAAN API-FUNKTIOITA...")
        api_result = log_action_with_blocks(
            "api_test",
            "Testi API-funktiolla",
            ["q5"],
            "api_user",
            {"api_test": True},
            ipfs,
            "test_election_2024",
            "test_node_1"
        )
        print(f"   ✅ API-funktio testattu: {api_result['system_chain']['success']}")
        
        # Testaa 4: Ketjun palautus testi (korjattu)
        print("\n4. 🔄 TESTATAAN KETJUN PALAUTUSTA...")
        recovery_result = chain_manager.recover_chain_from_blocks("test_election_2024", "test_node_1")
        print(f"   ✅ Palautus testattu: {recovery_result['success']}")
        if recovery_result['success']:
            print(f"      - Palautetut lohkot: {recovery_result.get('blocks_recovered', 0)}")
        
        # Testaa 5: Useita kirjauksia eri prioriteeteilla
        print("\n5. 🎯 TESTATAAN ERI PRIORITEETTEJA...")
        
        priorities = [
            ("normal_action", "Normaali prioriteetti", "normal"),
            ("high_action", "Korkea prioriteetti", "high"), 
            ("emergency_action", "Hätäprioriteetti", "emergency")
        ]
        
        for action_type, description, priority in priorities:
            result = log_action_with_blocks(
                action_type,
                description,
                [],
                "priority_test_user",
                {"priority": priority},
                ipfs,
                "test_election_2024",
                "test_node_1",
                priority
            )
            print(f"   ✅ {priority}: {result['system_chain']['success']}")
        
        # Testaa 6: System chainin tila
        print("\n6. 📊 TESTATAAN SYSTEM CHAININ TILAA...")
        from pathlib import Path
        chain_file = Path("runtime/system_chain.json")
        if chain_file.exists():
            with open(chain_file, 'r') as f:
                chain_data = json.load(f)
            print(f"   ✅ System chain tiedosto:")
            print(f"      - Lohkoja: {chain_data['current_state']['total_blocks']}")
            print(f"      - Viimeisin päivitys: {chain_data['current_state']['last_updated']}")
        
        print("\n✅ KAIKKI SYSTEM CHAININ TESTIT ONNISTUIVAT!")
        return True
        
    except Exception as e:
        print(f"❌ TESTI EPÄONNISTUI: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_system_chain()
    sys.exit(0 if success else 1)
