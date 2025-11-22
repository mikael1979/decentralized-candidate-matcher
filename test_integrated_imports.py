# test_integrated_imports.py
#!/usr/bin/env python3
"""
Test script for verifying integrated multinode module imports work correctly
"""

import sys
import os

# Lisää src-hakemisto Python-polkuun
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_legacy_imports():
    """Test existing legacy module imports"""
    print("🧪 Testing legacy module imports...")
    
    try:
        from nodes import NodeManager, NetworkSyncManager, QuorumVoting, OLYMPIAN_NODES
        print("✅ Legacy modules imported successfully")
        print(f"   Olympian nodes: {len(OLYMPIAN_NODES)}")
        return True
    except ImportError as e:
        print(f"❌ Legacy import failed: {e}")
        return False

def test_new_architecture_imports():
    """Test new multinode architecture imports"""
    print("🧪 Testing new architecture imports...")
    
    try:
        from nodes import NodeIdentity, NetworkManager, ConsensusManager, PeerDiscovery
        print("✅ New architecture modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ New architecture import failed: {e}")
        return False

def test_mixed_imports():
    """Test mixing legacy and new imports"""
    print("🧪 Testing mixed imports (legacy + new)...")
    
    try:
        # Legacy
        from nodes import NodeManager, QuorumVoting
        # New
        from nodes import NodeIdentity, ConsensusManager
        
        print("✅ Mixed imports work successfully")
        print(f"   Legacy: NodeManager, QuorumVoting")
        print(f"   New: NodeIdentity, ConsensusManager")
        return True
    except ImportError as e:
        print(f"❌ Mixed import failed: {e}")
        return False

def test_module_metadata():
    """Test module metadata"""
    print("🧪 Testing module metadata...")
    
    try:
        import nodes
        print(f"✅ Module metadata:")
        print(f"   Version: {nodes.__version__}")
        print(f"   Author: {nodes.__author__}")
        print(f"   Docstring: {nodes.__doc__.strip()}")
        return True
    except Exception as e:
        print(f"❌ Metadata test failed: {e}")
        return False

def test_backward_compatibility():
    """Test that existing code still works"""
    print("🧪 Testing backward compatibility...")
    
    try:
        # Test existing functionality
        from nodes.node_manager import NodeManager
        from nodes.network_sync import NetworkSyncManager
        from nodes.quorum_voting import QuorumVoting
        
        # Create instances (minimal)
        node_mgr = NodeManager("TestElection")
        sync_mgr = NetworkSyncManager("TestElection") 
        quorum = QuorumVoting("TestElection")
        
        print("✅ Backward compatibility verified")
        print(f"   NodeManager: {type(node_mgr)}")
        print(f"   NetworkSyncManager: {type(sync_mgr)}")
        print(f"   QuorumVoting: {type(quorum)}")
        return True
    except Exception as e:
        print(f"❌ Backward compatibility failed: {e}")
        return False

def main():
    """Run all import tests"""
    print("🚀 STARTING INTEGRATED MULTINODE IMPORT TESTS")
    print("=" * 60)
    
    tests = [
        test_legacy_imports,
        test_new_architecture_imports,
        test_mixed_imports,
        test_module_metadata,
        test_backward_compatibility
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
        print()  # Tyhjä rivi testien väliin
    
    # Yhteenveto
    print("📊 INTEGRATED TEST RESULTS SUMMARY:")
    print("=" * 40)
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 ALL INTEGRATED IMPORT TESTS PASSED!")
        print("   Legacy and new architecture coexist successfully!")
        return 0
    else:
        print("💥 SOME INTEGRATED TESTS FAILED!")
        print("   Check module structure and imports.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
