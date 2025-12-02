#!/usr/bin/env python3
"""
Integraatiotestien suorittaja - Päivitetty käyttämään yksinkertaisia testejä
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import os
import subprocess
import time
import json

def run_test(test_file):
    """Suorita yksittäinen testi subprocessina"""
    print(f"\n{'='*60}")
    print(f"🚀 SUORITETAAN: {test_file}")
    print(f"{'='*60}")
    
    try:
        # Suorita testi erillisenä prosessina
        result = subprocess.run([
            sys.executable, test_file
        ], capture_output=True, text=True, timeout=30)
        
        # Tulosta output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        success = result.returncode == 0
        
        if success:
            print(f"✅ {os.path.basename(test_file)} - PASS")
        else:
            print(f"❌ {os.path.basename(test_file)} - FAIL (exit code: {result.returncode})")
            
        return success
        
    except subprocess.TimeoutExpired:
        print(f"❌ {os.path.basename(test_file)} - TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ {os.path.basename(test_file)} - ERROR: {e}")
        return False

def main():
    """Pääfunktio testien suorittamiseen"""
    print("🎯 JUMALTENVAALIT - INTEGRAATIOTESTIT")
    print("=" * 60)
    
    # Tarkista että data/runtime hakemisto on olemassa
    os.makedirs("data/runtime", exist_ok=True)
    
    # Alusta tyhjät tiedostot jos eivät ole olemassa
    required_files = {
        "data/runtime/parties.json": {
            "metadata": {
                "version": "2.1.0", 
                "created": "2025-01-15T10:00:00+02:00",
                "last_updated": "2025-01-15T10:00:00+02:00",
                "election_id": "Jumaltenvaalit2026",
                "description": {
                    "fi": "Puolueiden hajautettu rekisteri",
                    "en": "Decentralized party registry", 
                    "sv": "Decentraliserat partiregister"
                }
            },
            "parties": [],
            "verification_history": []
        },
        "data/runtime/questions.json": {
            "metadata": {
                "version": "2.1.0",
                "created": "2025-01-15T10:00:00+02:00", 
                "last_updated": "2025-01-15T10:00:00+02:00",
                "election_id": "Jumaltenvaalit2026",
                "description": {
                    "fi": "Vaalikysymysten rekisteri",
                    "en": "Election questions registry",
                    "sv": "Valfrågoregister"
                }
            },
            "questions": []
        },
        "data/runtime/candidates.json": {
            "metadata": {
                "version": "2.1.0",
                "created": "2025-01-15T10:00:00+02:00",
                "last_updated": "2025-01-15T10:00:00+02:00", 
                "election_id": "Jumaltenvaalit2026",
                "description": {
                    "fi": "Ehdokkaiden rekisteri",
                    "en": "Candidate registry",
                    "sv": "Kandidatregister"
                }
            },
            "candidates": []
        }
    }
    
    for file_path, default_data in required_files.items():
        if not os.path.exists(file_path):
            print(f"📁 Alustetaan: {file_path}")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, indent=2, ensure_ascii=False)
    
    # KÄYTETÄÄN YKSINKERTAISIA TESTEJÄ - Nämä eivät vaadi monimutkaisia importteja
    test_files = [
        "tests/integration/test_party_creation_simple.py",
        "tests/integration/test_questions.py", 
        "tests/integration/test_candidates.py",
        "tests/integration/test_elo_comparison_simple.py",
        "tests/integration/test_analytics_simple.py",
        "tests/integration/test_answers.py"
    ]
    
    results = {}
    start_time = time.time()
    
    for test_file in test_files:
        if os.path.exists(test_file):
            results[test_file] = run_test(test_file)
            time.sleep(0.5)  # Pieni viive testien välissä
        else:
            print(f"❌ Testitiedostoa ei löydy: {test_file}")
            results[test_file] = False
    
    # Yhteenveto
    execution_time = time.time() - start_time
    print(f"\n{'='*60}")
    print("📊 TESTITULOKSET")
    print(f"{'='*60}")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_file, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {os.path.basename(test_file)}")
    
    print(f"\n⏱️  Suoritusaika: {execution_time:.2f} sekuntia")
    print(f"🎯 YHTEENVETO: {passed}/{total} testiä läpäisty")
    
    if passed == total:
        print("🎉 KAIKKI TESTIT LÄPÄISTY! Järjestelmä toimii odotetusti.")
    else:
        print("💡 JOITAIN TESTEJÄ EPÄONNISTUI. Tarkista järjestelmän tila.")
    
    # Näytä data-tiedostojen tilanne
    print(f"\n📁 DATA-TILANNE:")
    for file_path in required_files.keys():
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'parties' in data:
                        print(f"   📊 Puolueita: {len(data['parties'])}")
                    if 'questions' in data:
                        print(f"   ❓ Kysymyksiä: {len(data['questions'])}")
                    if 'candidates' in data:
                        print(f"   👑 Ehdokkaita: {len(data['candidates'])}")
            except Exception as e:
                print(f"   ❌ Virhe ladattaessa {file_path}: {e}")

if __name__ == "__main__":
    main()
