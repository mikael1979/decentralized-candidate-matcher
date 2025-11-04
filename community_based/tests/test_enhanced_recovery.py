#!/usr/bin/env python3
# test_enhanced_recovery.py
"""
Testaa laajennettua palautusjärjestelmää
Käyttö: python test_enhanced_recovery.py
"""

import json
import sys
from datetime import datetime

sys.path.append('.')

def test_enhanced_recovery():
    """Testaa laajennettua palautusjärjestelmää"""
    
    print("🧪 LAAJENNETUN PALAUTUSJÄRJESTELMÄN TESTI")
    print("=" * 50)
    
    try:
        from mock_ipfs import MockIPFS
        from enhanced_recovery_manager import EnhancedRecoveryManager
        
        print("✅ Moduulit ladattu onnistuneesti")
        
        # Alusta testiympäristö
        ipfs = MockIPFS()
        recovery = EnhancedRecoveryManager(
            runtime_dir="runtime_test",
            ipfs_client=ipfs,
            election_id="test_election_2024", 
            node_id="test_node_1"
        )
        
        # Testaa 1: Palautusjärjestelmän alustus
        print("\n1. 🔄 TESTATAAN PALAUTUSJÄRJESTELMÄN ALUSTUSTA...")
        metadata_cid = recovery.initialize_recovery_system()
        print(f"   ✅ Palautusjärjestelmä alustettu: {metadata_cid}")
        
        # Testaa 2: Normaalit varaukset
        print("\n2. 📝 TESTATAAN NORMAALEJA VARAUKSIA...")
        test_data = {
            "questions": ["q1", "q2", "q3"],
            "candidates": ["c1", "c2"],
            "timestamp": datetime.now().isoformat()
        }
        
        entry_id = recovery.perform_intelligent_backup(test_data, "normal_backup", "normal")
        print(f"   ✅ Normaali varaus: {entry_id}")
        
        # Testaa 3: Kiireelliset varaukset
        print("\n3. 🚨 TESTATAAN KIIREELLISIÄ VARAUKSIA...")
        emergency_data = {
            "emergency": True,
            "reason": "test_emergency",
            "timestamp": datetime.now().isoformat()
        }
        
        emergency_id = recovery.perform_intelligent_backup(emergency_data, "emergency_backup", "emergency")
        print(f"   ✅ Kiireellinen varaus: {emergency_id}")
        
        # Testaa 4: Korkean prioriteetin varaukset
        print("\n4. 🔼 TESTATAAN KORKEAN PRIORITEETIN VARAUKSIA...")
        high_priority_data = {
            "sync_operation": "test_sync",
            "timestamp": datetime.now().isoformat()
        }
        
        high_priority_id = recovery.perform_intelligent_backup(high_priority_data, "sync_backup", "high")
        print(f"   ✅ Korkean prioriteetin varaus: {high_priority_id}")
        
        # Testaa 5: Palautusjärjestelmän status
        print("\n5. 📊 TESTATAAN PALAUTUSJÄRJESTELMÄN STATUSTA...")
        status = recovery.get_recovery_status()
        print(f"   ✅ Status haettu:")
        print(f"      - Varauksia: {status['total_backup_entries']}")
        print(f"      - Hätävarauksia: {status['emergency_backups']}")
        print(f"      - Tunnetut nodet: {len(status['known_nodes'])}")
        
        # Testaa 6: Moninodisynkronointi (simuloitu)
        print("\n6. 🔗 TESTATAAN MONINODISYNKRONOINTIA...")
        sync_result = recovery.multi_node_synchronization(["node_1", "node_2", "node_3"])
        print(f"   ✅ Synkronointi suoritettu:")
        print(f"      - Nodet: {sync_result['nodes_processed']}")
        print(f"      - Merkinnät: {sync_result['entries_processed']}")
        
        print("\n✅ KAIKKI PALAUTUSJÄRJESTELMÄN TESTIT ONNISTUIVAT!")
        return True
        
    except Exception as e:
        print(f"❌ TESTI EPÄONNISTUI: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_recovery()
    sys.exit(0 if success else 1)
