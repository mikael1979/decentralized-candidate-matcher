# enable_production.py - UUSI PÄÄOHJELMA
#!/usr/bin/env python3
"""
Tuotantotilan aktivointi - LUKITSEE järjestelmän käyttöön
Käyttö: python enable_production.py
"""

import sys
import json
from datetime import datetime
from pathlib import Path

def main():
    print("🔒 VAAILIJÄRJESTELMÄN TUOTANTOTILAN AKTIVOINTI")
    print("=" * 60)
    
    # Tarkista että järjestelmä on asennettu
    if not Path("runtime").exists():
        print("❌ Runtime-hakemisto puuttuu - asenna järjestelmä ensin")
        return 1
    
    # Tarkista että vaali on konfiguroitu
    if not Path("runtime/meta.json").exists():
        print("❌ Meta-tiedosto puuttuu - konfiguroi vaali ensin")
        return 1
    
    try:
        # Tuo riippuvuudet
        from enhanced_integrity_manager import EnhancedIntegrityManager
        from mock_ipfs import MockIPFS
        
        # Alusta IPFS (mock)
        ipfs = MockIPFS()
        
        # Hae vaalin tiedot
        with open('runtime/meta.json', 'r', encoding='utf-8') as f:
            meta_data = json.load(f)
        election_id = meta_data['election']['id']
        
        # Alusta integriteettimanageri
        integrity = EnhancedIntegrityManager("development", ipfs)
        
        print("📋 TOIMINNOT:")
        print("1. Generoidaan fingerprintit kaikista moduuleista")
        print("2. Tallennetaan fingerprintit IPFS:ään")
        print("3. Luodaan tuotantolukko")
        print("4. Varmistetaan järjestelmän eheys")
        print()
        
        # Kysy vahvistus
        response = input("Haluatko jatkaa tuotantotilan aktivointia? (K/e): ").strip().lower()
        if response not in ['', 'k', 'kyllä', 'y', 'yes']:
            print("Aktivointi peruttu")
            return 0
        
        print("\n🔄 AKTIVOIDAAN TUOTANTOTILAA...")
        
        # 1. Generoi fingerprint-rekisteri
        print("🔍 Generoidaan fingerprint-rekisteri...")
        fingerprint_registry = integrity.generate_fingerprint_registry()
        
        # 2. Lukitse järjestelmä
        print("🔒 Lukitaan järjestelmä...")
        lock_entry_id = integrity.lock_system_for_production(ipfs, election_id, "main_node")
        
        # 3. Luo lukkotiedosto
        lock_file = Path("runtime/production.lock")
        lock_data = {
            "production_locked": True,
            "locked_at": datetime.now().isoformat(),
            "fingerprint_entry": lock_entry_id,
            "election_id": election_id,
            "total_modules": len(fingerprint_registry["modules"]),
            "security_level": "high"
        }
        
        with open(lock_file, 'w', encoding='utf-8') as f:
            json.dump(lock_data, f, indent=2, ensure_ascii=False)
        
        print("\n✅ TUOTANTOTILA AKTIVOITU ONNISTUNEESTI!")
        print("=" * 50)
        print(f"🔒 Lukko luotu: {lock_file}")
        print(f"📦 Fingerprint entry: {lock_entry_id}")
        print(f"📊 Moduuleja lukittu: {len(fingerprint_registry['modules'])}")
        print(f"🏛️  Vaali: {election_id}")
        print()
        print("💡 HUOMIO: Järjestelmä tarkistaa nyt fingerprintit käynnistyessä.")
        print("   Muutokset ohjelmatiedostoihin havaitaan automaattisesti.")
        
        return 0
        
    except ImportError as e:
        print(f"❌ Riippuvuus puuttuu: {e}")
        return 1
    except Exception as e:
        print(f"❌ Tuotantotilan aktivointi epäonnistui: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
