# check_system_status.py
#!/usr/bin/env python3
"""
Check system status and mode
"""

import json
from pathlib import Path

def check_system_status():
    print("🔍 JÄRJESTELMÄN TILAN TARKISTUS")
    print("=" * 50)
    
    # Check if production config exists
    production_config = Path("runtime/production_config.json")
    if production_config.exists():
        with open(production_config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("📊 TUOTANTOTILA:")
        print(f"   🔒 Lukittu: ✅ KYLLÄ")
        print(f"   🆔 Vaali: {config['metadata']['election_id']}")
        print(f"   ⏰ Lukittu: {config['metadata']['locked_at'][:19]}")
        print(f"   🔑 Lock ID: {config['metadata']['lock_entry_id']}")
        return "production"
    else:
        print("📊 KEHITYSTILA:")
        print("   🔓 Lukittu: ❌ EI")
        print("   💡 Järjestelmä on kehitystilassa")
        return "development"

def check_integrity_issues():
    print("\n🔧 TARKISTETAAN ONGELMIA...")
    
    # Check for syntax errors
    try:
        import system_bootstrap
        print("✅ system_bootstrap.py: Syntax OK")
    except SyntaxError as e:
        print(f"❌ system_bootstrap.py: Syntax error line {e.lineno}")
        print(f"   💬 {e.msg}")
        return False
    except Exception as e:
        print(f"⚠️  system_bootstrap.py: {e}")
    
    # Check required files
    required_files = [
        "runtime/questions.json",
        "runtime/meta.json",
        "runtime/system_chain.json"
    ]
    
    all_exist = True
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}: OK")
        else:
            print(f"❌ {file}: PUUTTUU")
            all_exist = False
    
    return all_exist

if __name__ == "__main__":
    status = check_system_status()
    integrity_ok = check_integrity_issues()
    
    print(f"\n🎯 YHTEENVETO:")
    print(f"   Tila: {'🔒 TUOTANTO' if status == 'production' else '🔓 KEHITYS'}")
    print(f"   Integriteetti: {'✅ OK' if integrity_ok else '❌ ONGELMIA'}")
    
    if status == "production":
        print("\n💡 Järjestelmä on jo tuotannossa! Ei tarvitse lukita uudelleen.")
    else:
        print("\n💡 Järjestelmä on valmis lukittavaksi: python enable_production.py")
