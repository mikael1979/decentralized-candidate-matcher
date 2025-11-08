#!/usr/bin/env python3
# test_all_new_features.py
"""
Testaa kaikkia uusia ominaisuuksia yhdessä
Käyttö: python test_all_new_features.py
"""

import sys
from datetime import datetime

sys.path.append('.')

def test_all_new_features():
    """Testaa kaikkia uusia ominaisuuksia yhdessä"""
    
    print("🧪 KAIKKIEN UUSIEN OMINAISUUKSIEN YHTEISTESTI")
    print("=" * 60)
    
    tests = [
        ("IPFS Lohkot", "test_ipfs_blocks"),
        ("Laajennettu Palautus", "test_enhanced_recovery"), 
        ("Integriteettivalvonta", "test_enhanced_integrity"),
        ("System Chain", "test_enhanced_system_chain")
    ]
    
    results = []
    
    for test_name, test_module in tests:
        print(f"\n🎯 TESTATAAN: {test_name}")
        print("-" * 40)
        
        try:
            # Suorita testi moduulina
            if test_module == "test_ipfs_blocks":
                from test_ipfs_blocks import test_ipfs_blocks as test_func
            elif test_module == "test_enhanced_recovery":
                from test_enhanced_recovery import test_enhanced_recovery as test_func
            elif test_module == "test_enhanced_integrity":
                from test_enhanced_integrity import test_enhanced_integrity as test_func
            elif test_module == "test_enhanced_system_chain":
                from test_enhanced_system_chain import test_enhanced_system_chain as test_func
            else:
                print(f"❌ Tuntematon testi: {test_module}")
                results.append((test_name, False))
                continue
            
            success = test_func()
            results.append((test_name, success))
            
            if success:
                print(f"✅ {test_name}: ONNISTUI")
            else:
                print(f"❌ {test_name}: EPÄONNISTUI")
                
        except Exception as e:
            print(f"❌ {test_name}: VIRHE - {e}")
            results.append((test_name, False))
    
    # Yhteenveto
    print("\n" + "=" * 60)
    print("📊 TESTITULOKSET:")
    print("=" * 60)
    
    passed = 0
    for test_name, success in results:
        status = "✅ ONNISTUI" if success else "❌ EPÄONNISTUI"
        print(f"   {test_name}: {status}")
        if success:
            passed += 1
    
    total = len(results)
    print(f"\n🎯 YHTEENVETO: {passed}/{total} testiä onnistui")
    
    if passed == total:
        print("🎉 KAIKKI TESTIT ONNISTUIVAT! Järjestelmä on valmis.")
        return True
    else:
        print("⚠️  JOITKIN TESTIT EPÄONNISTUIVAT. Tarkista virheet.")
        return False

if __name__ == "__main__":
    success = test_all_new_features()
    sys.exit(0 if success else 1)
