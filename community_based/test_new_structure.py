#!/usr/bin/env python3
"""
Testaa uuden rakenteen toimivuus
"""

import sys
from pathlib import Path

def test_structure():
    """Testaa että uusi rakenne on paikallaan"""
    print("🧪 TESTATAAN UUTTA RAKENNETTA")
    print("=" * 50)
    
    required_dirs = ["managers", "cli", "utils", "docs"]
    required_files = [
        "managers/unified_system_chain.py",
        "managers/unified_question_handler.py", 
        "cli/cli_template.py",
        "utils/json_utils.py",
        "utils/file_utils.py",
        "utils/ipfs_client.py"
    ]
    
    all_ok = True
    
    # Tarkista hakemistot
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"✅ Hakemisto: {dir_name}")
        else:
            print(f"❌ Hakemisto puuttuu: {dir_name}")
            all_ok = False
    
    # Tarkista tiedostot
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ Tiedosto: {file_path}")
        else:
            print(f"❌ Tiedosto puuttuu: {file_path}")
            all_ok = False
    
    # Testaa importit
    try:
        from managers.unified_system_chain import UnifiedSystemChain
        print("✅ UnifiedSystemChain import onnistui")
    except ImportError as e:
        print(f"❌ UnifiedSystemChain import epäonnistui: {e}")
        all_ok = False
    
    try:
        from managers.unified_question_handler import UnifiedQuestionHandler
        print("✅ UnifiedQuestionHandler import onnistui")
    except ImportError as e:
        print(f"❌ UnifiedQuestionHandler import epäonnistui: {e}")
        all_ok = False
    
    try:
        from cli.cli_template import CLITemplate
        print("✅ CLITemplate import onnistui")
    except ImportError as e:
        print(f"❌ CLITemplate import epäonnistui: {e}")
        all_ok = False
    
    if all_ok:
        print("\n🎯 KAIKKI TESTIT LÄPÄISTY! Uusi rakenne valmis.")
        return 0
    else:
        print("\n⚠️  JOITAKIN ONGELMIA HAVAITTU - tarkista ylläolevat virheet")
        return 1

if __name__ == "__main__":
    sys.exit(test_structure())
