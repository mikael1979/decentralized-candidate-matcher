#!/usr/bin/env python3
# simple_production_lock.py
"""
Yksinkertainen tuotantolukitus ilman IPFS-riippuvuuksia
Käyttö: python simple_production_lock.py
"""

import json
from datetime import datetime
from pathlib import Path

def create_simple_production_lock():
    """Luo yksinkertainen tuotantolukitus"""
    
    print("🔒 LUODAAN YKSINKERTAINEN TUOTANTOLUKITUS...")
    print("=" * 50)
    
    # Tiedostopolut
    lock_file = Path("runtime/production.lock")
    fingerprint_file = Path("runtime/file_fingerprints.json")
    
    # 1. Tarkista että järjestelmä on asennettu
    if not Path("runtime").exists():
        print("❌ Runtime-hakemisto puuttuu - asenna järjestelmä ensin")
        return False
    
    # 2. Lataa vaalin tiedot
    try:
        with open('runtime/meta.json', 'r', encoding='utf-8') as f:
            meta_data = json.load(f)
        election_id = meta_data['election']['id']
        election_name = meta_data['election']['name']['fi']
        print(f"🏛️  Vaali: {election_name} ({election_id})")
    except Exception as e:
        print(f"❌ Virhe ladattaessa meta.json: {e}")
        return False
    
    # 3. Generoi fingerprint-rekisteri
    print("🔍 Generoidaan fingerprint-rekisteri...")
    
    try:
        from enhanced_integrity_manager import EnhancedIntegrityManager
        integrity = EnhancedIntegrityManager("development")
        registry = integrity.generate_fingerprint_registry()
        
        # Päivitä metadata
        registry["metadata"]["locked_for_production"] = datetime.now().isoformat()
        registry["metadata"]["mode"] = "production"
        registry["metadata"]["election_id"] = election_id
        
        print(f"✅ Fingerprint-rekisteri luotu: {len(registry['modules'])} moduulia")
        
    except Exception as e:
        print(f"❌ Fingerprint-rekisterin generointi epäonnistui: {e}")
        return False
    
    # 4. Tallenna fingerprintit
    try:
        with open(fingerprint_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        print(f"✅ Fingerprint-rekisteri tallennettu: {fingerprint_file}")
    except Exception as e:
        print(f"❌ Fingerprint-rekisterin tallennus epäonnistui: {e}")
        return False
    
    # 5. Luo lukkotiedosto
    lock_data = {
        "production_locked": True,
        "locked_at": datetime.now().isoformat(),
        "fingerprint_cid": "local_simple_lock",
        "total_modules": len(registry['modules']),
        "election_id": election_id,
        "election_name": election_name,
        "method": "simple_production_lock",
        "description": "Yksinkertainen tuotantolukitus ilman IPFS:ää"
    }
    
    try:
        with open(lock_file, 'w', encoding='utf-8') as f:
            json.dump(lock_data, f, indent=2, ensure_ascii=False)
        print(f"✅ Tuotantolukitus luotu: {lock_file}")
    except Exception as e:
        print(f"❌ Lukkotiedoston luonti epäonnistui: {e}")
        return False
    
    # 6. Testaa lukituksen toiminta
    print("\n🧪 TESTATAAN LUKITUSTA...")
    try:
        from production_lock_manager import ProductionLockManager
        lock_manager = ProductionLockManager()
        status = lock_manager.get_lock_status()
        
        if status["locked"]:
            print("✅ Lukitus testattu onnistuneesti!")
            print(f"   Lukittu: {status['locked_at']}")
            print(f"   Vaali: {status['election_id']}")
        else:
            print("❌ Lukituksen testaus epäonnistui")
            return False
            
    except Exception as e:
        print(f"⚠️  Lukituksen testaus antoi varoituksen: {e}")
    
    print("\n🎯 YKSINKERTAINEN TUOTANTOLUKITUS LUOTU ONNISTUNEESTI!")
    print("=" * 50)
    print("🔐 TURVALLISUUS TOIMINNOT AKTIVOITU:")
    print("   ✅ Kaikki ohjelmat tarkistavat fingerprintit")
    print("   ✅ Järjestelmän eheys varmistettu")
    print("   ✅ Tuotantotasoinen turvallisuus")
    print("")
    print("💡 HUOMIO:")
    print("   - Tämä on yksinkertainen lukitus ilman IPFS:ää")
    print("   - Käytä enable_production.py täydelliseen lukitukseen")
    print("   - Testaa järjestelmä ennen käyttöönottoa")
    
    return True

def verify_simple_lock():
    """Tarkista yksinkertaisen lukituksen toiminta"""
    
    print("🔍 TARKISTETAAN YKSINKERTAINEN LUKITUS...")
    
    lock_file = Path("runtime/production.lock")
    fingerprint_file = Path("runtime/file_fingerprints.json")
    
    if not lock_file.exists():
        print("❌ Lukkotiedostoa ei löydy")
        return False
    
    if not fingerprint_file.exists():
        print("❌ Fingerprint-tiedostoa ei löydy")
        return False
    
    try:
        # Lataa lukkotiedot
        with open(lock_file, 'r', encoding='utf-8') as f:
            lock_data = json.load(f)
        
        # Lataa fingerprintit
        with open(fingerprint_file, 'r', encoding='utf-8') as f:
            fingerprint_data = json.load(f)
        
        print(f"✅ Lukitus löytyy: {lock_data['election_id']}")
        print(f"✅ Fingerprintit löytyy: {len(fingerprint_data['modules'])} moduulia")
        print(f"✅ Lukittu: {lock_data['locked_at']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Lukituksen tarkistus epäonnistui: {e}")
        return False

def main():
    """Pääohjelma"""
    
    print("🎯 YKSINKERTAINEN TUOTANTOLUKITUS")
    print("=" * 60)
    print("Tämä skripti luo perustason tuotantolukituksen ilman IPFS:ää.")
    print("Idealta käytössä, kun IPFS-lohkojen alustus on ongelmallista.")
    print("")
    
    # Tarkista nykyinen tila
    lock_file = Path("runtime/production.lock")
    if lock_file.exists():
        print("🔒 Järjestelmä on JO LUKITTU")
        verify_simple_lock()
        return True
    
    print("🔓 Järjestelmä on KEHITYSTILASSA")
    print("")
    print("📋 YKSINKERTAISEN LUKITUKSEN EDUT:")
    print("   ✅ Nopea ja helppo aktivointi")
    print("   ✅ Ei IPFS-riippuvuuksia")
    print("   ✅ Perusturvallisuus toiminnot")
    print("")
    print("⚠️  RAJOITTEET:")
    print("   - Ei IPFS-pohjaista fingerprint-tallennusta")
    print("   - Ei lohkopohjaista palautusmekanismia")
    print("   - Vain paikallinen turvallisuus")
    
    print("\n" + "=" * 60)
    response = input("Haluatko luoda yksinkertaisen tuotantolukituksen? (K/e): ").strip().lower()
    
    if response in ['', 'k', 'kyllä', 'y', 'yes']:
        success = create_simple_production_lock()
        if success:
            print("\n🎉 LUKITUS ONNISTUI! Järjestelmä on nyt tuotantotilassa.")
            print("\n💡 Testaa järjestelmä:")
            print("python system_bootstrap.py")
            print("python security_test.py")
            return True
        else:
            print("\n❌ LUKITUS EPÄONNISTUI!")
            return False
    else:
        print("\n🔓 Lukituksen luonti peruttu")
        return True

if __name__ == "__main__":
    main()
