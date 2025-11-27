#!/usr/bin/env python3
"""
Korjaa config_manager importit uuteen rakenteeseen
"""
import os
import re

# Korjattavat tiedostot ja korjaukset
FIXES = {
    # Vanha: from core.config_manager import ConfigManager
    # Uusi: from core.config import ConfigManager
    r'from core\.config_manager import ConfigManager': 'from core.config import ConfigManager',
    r'from src\.core\.config_manager import ConfigManager': 'from src.core.config import ConfigManager',
    
    # Vanha: from core.config_manager import get_election_id, get_data_path
    # Uusi: from core import get_election_id, get_data_path
    r'from core\.config_manager import (get_election_id, get_data_path)': r'from core import \1',
    r'from src\.core\.config_manager import (get_election_id, get_data_path)': r'from src.core import \1',
    
    # Vanha: from core.config_manager import get_election_id
    # Uusi: from core import get_election_id  
    r'from core\.config_manager import get_election_id': 'from core import get_election_id',
    r'from src\.core\.config_manager import get_election_id': 'from src.core import get_election_id',
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
    print("🔧 KORJATAAN CONFIG_MANAGER IMPORTIT...")
    
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
