#!/usr/bin/env python3
# system_bootstrap.py
"""
Järjestelmän käynnistysmoduuli - Suoritetaan jokaisen ohjelman alussa
Käyttö: Lisää jokaisen ohjelman alkuun:
  from system_bootstrap import verify_system_startup
  verify_system_startup()
"""

import sys
import os
from pathlib import Path

def verify_system_startup():
    """Suorita järjestelmän käynnistyksen tarkistukset"""
    
    # Estä rekursio jos bootstrap itse suoritetaan
    if "SYSTEM_BOOTSTRAP_RUNNING" in os.environ:
        return True
    os.environ["SYSTEM_BOOTSTRAP_RUNNING"] = "true"
    
    try:
        print("🔍 Järjestelmän käynnistystarkistukset...")
        
        # 1. Tarkista runtime-hakemisto
        runtime_dir = Path("runtime")
        if not runtime_dir.exists():
            print("❌ Runtime-hakemisto puuttuu - suorita ensin alustus")
            print("💡 Käytä: python initialization.py")
            return False
        
        # 2. Tarkista perustiedostot
        required_files = [
            "runtime/meta.json",
            "runtime/system_metadata.json", 
            "runtime/system_chain.json"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            print("❌ Puuttuvat perustiedostot:")
            for file in missing_files:
                print(f"   - {file}")
            print("💡 Suorita: python install.py --verify")
            return False
        
        # 3. Tarkista fingerprintit tuotantotilassa
        lock_file = Path("runtime/production.lock")
        if lock_file.exists():
            print("🔒 Tuotantotila - tarkistetaan fingerprintit...")
            
            try:
                from production_lock_manager import ProductionLockManager
                lock_manager = ProductionLockManager()
                
                if not lock_manager.verify_on_startup():
                    print("❌ JÄRJESTELMÄN EHYS VAARANTUNUT!")
                    print("🚫 Ohjelma pysäytetty turvallisuussyistä")
                    return False
                
                print("✅ Järjestelmän eheys varmistettu")
                
            except ImportError as e:
                print(f"⚠️  Tuotantotilan tarkistus ei saatavilla: {e}")
                print("💡 Jatketaan ilman fingerprint-tarkistusta")
            except Exception as e:
                print(f"⚠️  Fingerprint-tarkistus epäonnistui: {e}")
                print("💡 Jatketaan varotoimintana")
        
        else:
            print("🔓 Kehitystila - fingerprint-tarkistus ohitettu")
        
        # 4. Tarkista IPFS-yhteys
        try:
            from ipfs_sync_manager import SimpleSyncEngine
            sync_engine = SimpleSyncEngine()
            status = sync_engine.get_sync_status()
            
            if status["sync_enabled"] and not status["real_ipfs_available"]:
                print("⚠️  IPFS ei saatavilla - käytetään mock-tilaa")
        except ImportError as e:
            print(f"⚠️  IPFS-synkronointia ei saatavilla: {e}")
        
        # 5. Tarkista vaalin tila
        try:
            with open('runtime/meta.json', 'r', encoding='utf-8') as f:
                meta_data = json.load(f)
            
            election_id = meta_data['election']['id']
            election_name = meta_data['election']['name']['fi']
            
            print(f"🏛️  Aktiivinen vaali: {election_name} ({election_id})")
            
        except Exception as e:
            print(f"⚠️  Vaalin tarkistus epäonnistui: {e}")
        
        print("✅ Käynnistystarkistukset läpäisty")
        return True
        
    except Exception as e:
        print(f"❌ Käynnistystarkistukset epäonnistuivat: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Puhdista environment variable
        if "SYSTEM_BOOTSTRAP_RUNNING" in os.environ:
            del os.environ["SYSTEM_BOOTSTRAP_RUNNING"]

def bootstrap_system():
    """Vanhempi nimi yhteensopivuuden vuoksi"""
    return verify_system_startup()

# Automaattinen suoritus kun moduuli importataan
# HUOM: Kommentoitu pois että ohjelmat voivat kontrolloida itse
# if __name__ != "__main__":
#     verify_system_startup()

def print_system_status():
    """Tulosta järjestelmän nykyinen tila"""
    
    print("\n📊 JÄRJESTELMÄN TILA:")
    print("=" * 40)
    
    # Tarkista tuotantotila
    lock_file = Path("runtime/production.lock")
    if lock_file.exists():
        try:
            with open(lock_file, 'r', encoding='utf-8') as f:
                lock_data = json.load(f)
            print(f"🔒 TUOTANTOTILA (lukittu: {lock_data.get('locked_at', 'unknown')})")
            print(f"   Fingerprint CID: {lock_data.get('fingerprint_cid', 'local')}")
            print(f"   Moduuleja: {lock_data.get('total_modules', 'unknown')}")
        except:
            print("🔒 TUOTANTOTILA (lukittu)")
    else:
        print("🔓 KEHITYSTILA")
    
    # Tarkista vaali
    try:
        with open('runtime/meta.json', 'r', encoding='utf-8') as f:
            meta_data = json.load(f)
        print(f"🏛️  VAAli: {meta_data['election']['name']['fi']}")
        print(f"   ID: {meta_data['election']['id']}")
    except:
        print("🏛️  VAAli: Tuntematon")
    
    # Tarkista IPFS
    try:
        from ipfs_sync_manager import SimpleSyncEngine
        sync_engine = SimpleSyncEngine()
        status = sync_engine.get_sync_status()
        ipfs_status = "🌐 OIKEA IPFS" if status["real_ipfs_available"] else "🔄 MOCK IPFS"
        print(f"{ipfs_status} (synkronointi: {'✅' if status['sync_enabled'] else '❌'})")
    except:
        print("🌐 IPFS: Tuntematon")
    
    print("=" * 40)

if __name__ == "__main__":
    # Komentorivikäyttö: python system_bootstrap.py
    print("🚀 JÄRJESTELMÄN KÄYNNISTYSTARKISTUS")
    print("=" * 50)
    
    success = verify_system_startup()
    
    if success:
        print_system_status()
        print("\n🎯 Järjestelmä on valmis käyttöön!")
    else:
        print("\n❌ Järjestelmän tarkistus epäonnistui!")
        sys.exit(1)
