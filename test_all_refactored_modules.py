#!/usr/bin/env python3
"""
Testaa kaikki refaktoroitu moduulit yhdessä.
"""
import sys
import subprocess
from pathlib import Path

# Lisää projektin juuri Python-polkuun
sys.path.insert(0, str(Path(__file__).parent))

def run_command(cmd, description):
    """Suorita komento ja raportoi tulos."""
    print(f"\n🔍 {description}")
    print(f"   Komento: {cmd}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("   ✅ SUCCESS")
            # Näytä ensimmäiset 3 riviä outputista
            lines = result.stdout.strip().split('\n')
            for line in lines[:3]:
                if line.strip():
                    print(f"      {line[:80]}...")
            return True
        else:
            print(f"   ❌ FAILED (exit code: {result.returncode})")
            if result.stderr:
                error_lines = result.stderr.strip().split('\n')
                for line in error_lines[:3]:
                    if line.strip():
                        print(f"      ERROR: {line[:80]}...")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ⏰ TIMEOUT (10s)")
        return False
    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")
        return False

def main():
    """Päätestifunktio."""
    print("=" * 60)
    print("🏗️  REFAKTOROITUJEN MODUULIEN KOKONAISTESTAUS")
    print("=" * 60)
    
    tests = [
        # 1. Install (refaktoroitu)
        ("python -m src.cli.install --list-elections", "Install module (list elections)"),
        
        # 2. Questions (refaktoroitu)  
        ("python -m src.cli.questions list --election Jumaltenvaalit2026", "Questions module (list)"),
        
        # 3. Answers (refaktoroitu)
        ("python -m src.cli.answers list --election Jumaltenvaalit2026", "Answers module (list)"),
        
        # 4. Config (refaktoroitu)
        ("python -m src.cli.config --help", "Config module (help)"),
        
        # 5. Vanha install.py (backward compatibility)
        ("python src/cli/install.py --list-elections", "Legacy install.py (backward compatibility)"),
    ]
    
    success_count = 0
    total_count = len(tests)
    
    for cmd, description in tests:
        if run_command(cmd, description):
            success_count += 1
    
    print("\n" + "=" * 60)
    print("📊 TESTITULOKSET:")
    print(f"   ✅ Onnistuneita: {success_count}/{total_count}")
    print(f"   📈 Onnistumisprosentti: {success_count/total_count*100:.1f}%")
    
    if success_count == total_count:
        print("\n🎉 KAIKKI REFAKTOROINNIT TOIMIVAT ONNISTUNEESTI!")
        print("   - install.py: ✅")
        print("   - manage_questions.py: ✅")
        print("   - manage_answers.py: ✅")
        print("   - config_manager.py: ✅")
        print("   - Backward compatibility: ✅")
    else:
        print(f"\n⚠️  {total_count - success_count} testiä epäonnistui")
        print("   Tarkista importit ja riippuvuudet.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
