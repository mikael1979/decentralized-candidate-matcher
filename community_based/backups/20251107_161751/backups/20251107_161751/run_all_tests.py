#!/usr/bin/env python3
# run_all_tests.py
"""
Suorita kaikki järjestelmän testit järjestyksessä
"""
import subprocess
import sys
import os
from pathlib import Path

# Varmista että PYTHONPATH sisältää projektin juuren
os.environ["PYTHONPATH"] = str(Path(__file__).parent)

# Testijärjestys: ensin yksikkötestit, sitten integraatiotestit
TEST_COMMANDS = [
    # 1. Perustestit ja yksikkötestit
    ["python", "-m", "tests.simple_elo_test"],
    ["python", "-m", "tests.test_installation"],
    
    # 2. IPFS-lohkojen testit
    ["python", "-m", "tests.test_ipfs_blocks"],
    
    # 3. Integriteetti- ja turvallisuustestit
    ["python", "-m", "tests.test_enhanced_integrity"],
    ["python", "-m", "tests.security_test"],
    
    # 4. Palautusjärjestelmän testit
    ["python", "-m", "tests.test_enhanced_recovery"],
    
    # 5. System chain -testit
    ["python", "-m", "tests.test_enhanced_system_chain"],
    
    # 6. Asennustestit
    ["python", "-m", "tests.test_installation"],
    ["python", "-m", "tests.test_multi_node"],
    
    # 7. Kaikkien uusien ominaisuuksien yhdistelmätesti
    ["python", "-m", "tests.test_all_new_features"],
    
    # 8. Demot ja käyttötestit
    ["python", "-m", "tests.demo_comparisons", "--user", "test_runner", "--count", "3"],
    ["python", "-m", "tests.demo_voting"]
]

def run_test(command):
    """Suorita yksittäinen testi"""
    print(f"\n▶️  Suoritetaan: {' '.join(command)}")
    print("-" * 60)
    
    result = subprocess.run(
        command,
        cwd=Path(__file__).parent,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ ONNISTUI")
        if result.stdout:
            # Näytä vain yhteenveto, ei kaikkea outputtia
            if "ONNISTUI" in result.stdout or "✅" in result.stdout:
                last_lines = result.stdout.strip().split('\n')[-5:]
                print("\n".join(last_lines))
    else:
        print("❌ EPÄONNISTUI")
        if result.stderr:
            print("VIRHEOUTPUTTI:")
            print(result.stderr[-1000:])  # Viimeiset 1000 merkkiä
        if result.stdout:
            print("OUTPUTTI:")
            print(result.stdout[-500:])   # Viimeiset 500 merkkiä
    
    return result.returncode == 0

def main():
    """Pääohjelma"""
    print("🧪 HAJAUTETUN VAALIJÄRJESTELMÄN TÄYDELLINEN TESTAUS")
    print("=" * 70)
    print(f"Projektin juuri: {Path(__file__).parent}")
    print(f"Python versio: {sys.version}")
    print()
    
    # Tarkista että testihakemisto on olemassa
    if not Path("tests").exists():
        print("❌ tests/ hakemistoa ei löydy")
        print("💡 Suorita ensin: mv test_*.py tests/ && mv demo_*.py tests/")
        return False
    
    # Suorita testit
    passed = 0
    total = len(TEST_COMMANDS)
    
    for i, command in enumerate(TEST_COMMANDS, 1):
        print(f"\n{'='*70}")
        print(f"TESTI {i}/{total}")
        success = run_test(command)
        if success:
            passed += 1
        else:
            # Jatka muilla testeillä, mutta merkitse epäonnistuminen
            print(f"⚠️  Testi {i} epäonnistui, mutta jatketaan...")
    
    # Lopputulokset
    print(f"\n{'='*70}")
    print("📊 LOPPUTULOKSET")
    print(f"{'='*70}")
    print(f"✅ Onnistuneet testit: {passed}/{total}")
    print(f"❌ Epäonnistuneet testit: {total - passed}")
    
    if passed == total:
        print("\n🎉 KAIKKI TESTIT MENEVÄT LÄPI! Järjestelmä on valmis.")
        print("🎯 Seuraava vaihe: python enable_production.py")
        return True
    else:
        print(f"\n⚠️  {total - passed} testiä epäonnistui. Tarkista yllä olevat virheet.")
        print("💡 Yleisiä korjausvinkkejä:")
        print("   - Varmista että kaikki riippuvuudet on asennettu")
        print("   - Suorita ensin: python install.py --first-install --config-file=...")
        print("   - Tarkista että runtime/ hakemisto on olemassa")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
