#!/usr/bin/env python3
"""
Pikakorjaus turvallisuustestien ongelmiin
"""
import os
import subprocess
import sys

def fix_file_permissions():
    """Korjaa tiedostojen oikeudet"""
    print("🔐 Korjataan tiedostojen oikeuksia...")
    
    keys_dir = 'keys'
    files_to_fix = {
        'private_key.pem': '600',
        'system_info.json': '600', 
        'public_key.pem': '644'
    }
    
    for filename, permissions in files_to_fix.items():
        filepath = os.path.join(keys_dir, filename)
        if os.path.exists(filepath):
            try:
                os.chmod(filepath, int(permissions, 8))
                print(f"✅ {filename}: oikeudet {permissions}")
            except Exception as e:
                print(f"❌ {filename}: {e}")
        else:
            print(f"⚠️  {filename}: ei löydy")

def test_fixes():
    """Testaa korjaukset"""
    print("\n🔍 Testataan korjauksia...")
    
    # Tarkista oikeudet
    result = subprocess.run(['ls', '-la', 'keys/'], capture_output=True, text=True)
    print("Tiedostojen oikeudet keys/ hakemistossa:")
    print(result.stdout)
    
    # Käynnistä turvallisuustestit uudelleen
    print("\n🚀 Käynnistetään turvallisuustestit uudelleen...")
    os.system('python security_test.py')

if __name__ == '__main__':
    fix_file_permissions()
    test_fixes()
