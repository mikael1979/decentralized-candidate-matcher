#!/usr/bin/env python3
"""
Korjaa quorum_manager importit uuteen rakenteeseen
"""
import os
import re

# Korjattavat tiedostot ja korjaukset
FIXES = {
    # Vanha: from managers.quorum_manager import QuorumManager
    # Uusi: from managers.quorum import QuorumManager
    r'from managers\.quorum_manager import QuorumManager': 'from managers.quorum import QuorumManager',
    r'from src\.managers\.quorum_manager import QuorumManager': 'from src.managers.quorum import QuorumManager',
    
    # Vanha: import managers.quorum_manager
    # Uusi: import managers.quorum
    r'import managers\.quorum_manager': 'import managers.quorum',
    r'import src\.managers\.quorum_manager': 'import src.managers.quorum',
}

def fix_file(filepath):
    """Korjaa yhden tiedoston importit"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        for old_pattern, new_pattern in FIXES.items():
            content = re.sub(old_pattern, new_pattern, content)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Korjattu: {filepath}")
            return True
        else:
            print(f"ℹ️  Ei muutoksia: {filepath}")
            return False
            
    except Exception as e:
        print(f"❌ Virhe tiedostossa {filepath}: {e}")
        return False

def main():
    """Pääfunktio"""
    print("🔧 KORJATAAN QUORUM_MANAGER IMPORTIT...")
    
    # Etsi kaikki Python-tiedostot
    python_files = []
    for root, dirs, files in os.walk('src'):
        for file in files:
            if file.endswith('.py') and '.backup' not in file and '__pycache__' not in root:
                python_files.append(os.path.join(root, file))
    
    fixed_count = 0
    for filepath in python_files:
        if fix_file(filepath):
            fixed_count += 1
    
    print(f"\n🎯 KORJAUS VALMIS: {fixed_count}/{len(python_files)} tiedostoa korjattu")

if __name__ == "__main__":
    main()
