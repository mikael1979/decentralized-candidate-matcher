# test_imports.py
#!/usr/bin/env python3
"""
Test script for verifying all multinode module imports work correctly
"""

import sys
import os

# Lisää src-hakemisto Python-polkuun
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_core_imports():
    """Test core module imports"""
    print("🧪 Testing core module imports...")
    
    try:
        from nodes.core import NodeIdentity, NetworkManager
        print("✅ Core modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Core import failed: {e}")
        return False

def test_protocol_imports():
    """Test protocol module imports"""
    print("🧪 Testing protocol module imports...")
    
    try:
        from nodes.protocols import ConsensusManager, MessageProtocol
        print("✅ Protocol modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Protocol import failed: {e}")
        return False

def test_discovery_imports():
    """Test discovery module imports"""
    print("🧪 Testing discovery module imports...")
    
    try:
        from nodes.discovery import PeerDiscovery
        print("✅ Discovery modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Discovery import failed: {e}")
        return False

def test_top_level_imports():
    """Test top-level module imports"""
    print("🧪 Testing top-level module imports...")
    
    try:
        import nodes
        from nodes import NodeIdentity, NetworkManager, ConsensusManager, PeerDiscovery
        print("✅ Top-level modules imported successfully")
        print(f"   Version: {nodes.__version__}")
        print(f"   Author: {nodes.__author__}")
        return True
    except ImportError as e:
        print(f"❌ Top-level import failed: {e}")
        return False

def test_dependency_imports():
    """Test dependency imports from existing modules"""
    print("🧪 Testing dependency imports...")
    
    try:
        # Testaa riippuvuuksia olemassa olevista moduuleista
        from core.config_manager import ConfigManager
        from core.ipfs_client import IPFSClient
        from managers.crypto_manager import CryptoManager
        print("✅ Dependency modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Dependency import failed: {e}")
        return False

def main():
    """Run all import tests"""
    print("🚀 STARTING MULTINODE IMPORT TESTS")
    print("=" * 50)
    
    tests = [
        test_core_imports,
        test_protocol_imports, 
        test_discovery_imports,
        test_top_level_imports,
        test_dependency_imports
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
        print()  # Tyhjä rivi testien väliin
    
    # Yhteenveto
    print("📊 TEST RESULTS SUMMARY:")
    print("=" * 30)
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 ALL IMPORT TESTS PASSED! Ready for implementation.")
        return 0
    else:
        print("💥 SOME IMPORT TESTS FAILED! Check module structure.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
