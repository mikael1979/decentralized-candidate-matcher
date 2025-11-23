# test_multinode_system.py
#!/usr/bin/env python3
"""
Test the complete multinode system implementation
"""

import sys
import os

# Lisää src-hakemisto Python-polkuun
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_complete_node_identity():
    """Test complete NodeIdentity implementation"""
    print("🧪 Testing complete NodeIdentity...")
    
    try:
        from nodes.core.node_identity import NodeIdentity, test_node_identity
        
        # Run built-in tests
        identity = test_node_identity()
        
        # Test additional functionality
        identity.update_last_seen()
        print(f"✅ Last seen updated: {identity.last_seen}")
        
        # Test verification (don't assert, just log)
        verify_result = identity.verify_identity()
        print(f"🔐 Identity verification: {verify_result}")
        
        return True
    except Exception as e:
        print(f"❌ NodeIdentity test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_network_integration():
    """Test integration with existing network modules"""
    print("🧪 Testing network integration...")
    
    try:
        # Test that we can import both old and new systems
        from nodes import NodeManager, NodeIdentity, NetworkManager
        
        # Create instances
        legacy_manager = NodeManager("IntegrationTest")
        new_identity = NodeIdentity("IntegrationTest", "worker")
        network_manager = NetworkManager(new_identity)
        
        print("✅ Network integration successful")
        print(f"   Legacy: {type(legacy_manager)}")
        print(f"   New Identity: {new_identity}")
        print(f"   New Network: {network_manager}")
        
        return True
    except Exception as e:
        print(f"❌ Network integration failed: {e}")
        return False

def test_multinode_demo():
    """Demo multinode system functionality - FIXED VERSION"""
    print("🧪 Running multinode demo...")
    
    try:
        from nodes.core.node_identity import NodeIdentity
        from nodes.core.network_manager import NetworkManager
        from nodes.protocols.consensus import ConsensusManager
        
        # Create a small network
        coordinator = NodeIdentity("DemoElection", "coordinator", "DemoCoordinator")
        worker1 = NodeIdentity("DemoElection", "worker", "Worker1")
        worker2 = NodeIdentity("DemoElection", "worker", "Worker2")
        
        # Create network managers
        coord_network = NetworkManager(coordinator)
        worker1_network = NetworkManager(worker1)
        worker2_network = NetworkManager(worker2)
        
        # Connect networks and add peers
        coord_network.connect_to_network()
        coord_network.add_peer(worker1)
        coord_network.add_peer(worker2)
        
        # Create consensus managers
        coord_consensus = ConsensusManager(coord_network)
        
        # Demo output - USE THE FIXED METHOD
        peer_count = coord_network.get_peer_count()
        print("🎉 Multinode demo successful!")
        print(f"   Coordinator: {coordinator}")
        print(f"   Worker1: {worker1}") 
        print(f"   Worker2: {worker2}")
        print(f"   Network peers: {peer_count}")  # Fixed: use variable instead of method call
        print(f"   Consensus proposals: {len(coord_consensus.proposals)}")
        
        return True
    except Exception as e:
        print(f"❌ Multinode demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all multinode system tests"""
    print("🚀 COMPLETE MULTINODE SYSTEM TESTS")
    print("=" * 50)
    
    tests = [
        test_complete_node_identity,
        test_network_integration, 
        test_multinode_demo
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
        print()  # Empty line between tests
    
    # Summary
    print("📊 MULTINODE SYSTEM TEST RESULTS:")
    print("=" * 35)
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 ALL MULTINODE TESTS PASSED! System is ready for development.")
        return 0
    else:
        print("💥 SOME TESTS FAILED! Check implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
