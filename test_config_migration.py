#!/usr/bin/env python3
"""
Testaa config-manager migraation onnistumisen
"""
import sys
import os

# Lisää src hakemisto Python-polkuun
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

def test_imports():
    """Testaa että kaikki importit toimivat"""
    print("🧪 TESTATAAN IMPORTIT...")
    
    try:
        from core.config import ConfigManager
        print("✅ from core.config import ConfigManager")
    except ImportError as e:
        print(f"❌ from core.config import ConfigManager: {e}")
        return False
    
    try:
        from core import ConfigManager
        print("✅ from core import ConfigManager") 
    except ImportError as e:
        print(f"❌ from core import ConfigManager: {e}")
        return False
    
    try:
        from core.config.legacy_compatibility import get_election_id, get_data_path, validate_election_config
        print("✅ legacy_compatibility importit")
    except ImportError as e:
        print(f"❌ legacy_compatibility importit: {e}")
        return False
    
    return True

def test_functionality():
    """Testaa että toiminnallisuus toimii"""
    print("\n🧪 TESTATAAN TOIMINNALLISUUS...")
    
    try:
        from core.config import ConfigManager
        
        # Testaa perustoiminnot
        manager = ConfigManager("test_election")
        config = manager.get_election_config()
        
        if config and config["election"]["id"] == "test_election":
            print("✅ ConfigManager.get_election_config()")
        else:
            print("❌ ConfigManager.get_election_config() - odotettiin test_election")
            return False
        
        # Testaa config info
        info = manager.get_config_info()
        if info and "election_id" in info:
            print("✅ ConfigManager.get_config_info()")
        else:
            print("❌ ConfigManager.get_config_info()")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Toiminnallisuustesti epäonnistui: {e}")
        return False

def test_cli():
    """Testaa CLI-toiminnot"""
    print("\n🧪 TESTATAAN CLI...")
    
    try:
        from core.config.legacy_compatibility import get_election_id
        election_id = get_election_id("test_election")
        if election_id == "test_election":
            print("✅ get_election_id()")
        else:
            print(f"❌ get_election_id() - odotettiin 'test_election', saatiin '{election_id}'")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ CLI-testi epäonnistui: {e}")
        return False

if __name__ == "__main__":
    print("🚀 CONFIG-MANAGER MIGRAATION TESTI")
    print("=" * 50)
    
    success = True
    success &= test_imports()
    success &= test_functionality() 
    success &= test_cli()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 KAIKKI TESTIT LÄPÄISTY! MIGRAATIO ONNISTUI!")
    else:
        print("❌ MIGRAATIO TESTIT EPÄONNISTUIVAT")
        sys.exit(1)
