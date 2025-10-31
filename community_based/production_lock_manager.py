#!/usr/bin/env python3
# production_lock_manager.py
"""
Tuotantolukituksen hallinta
Käyttö: 
  python enable_production.py
  TAI
  python manage_questions.py production-lock
"""

import json
from pathlib import Path
from datetime import datetime

class ProductionLockManager:
    """Tuotantolukituksen hallinta"""
    
    def __init__(self):
        self.lock_file = Path("runtime/production.lock")
        self.fingerprint_file = Path("runtime/file_fingerprints.json")
    
    def enable_production_mode(self):
        """Aktivoi tuotantotilan lukitus"""
        
        print("🔒 AKTIVOIDAAN TUOTANTOTILA...")
        print("=" * 50)
        
        # Tarkista että järjestelmä on asennettu
        if not Path("runtime").exists():
            print("❌ Runtime-hakemisto puuttuu - asenna järjestelmä ensin")
            return False
        
        # Tarkista että vaali on konfiguroitu
        if not Path("runtime/meta.json").exists():
            print("❌ Meta-tiedosto puuttuu - konfiguroi vaali ensin")
            return False
        
        if self.lock_file.exists():
            print("⚠️  Järjestelmä on jo lukittu tuotantotilaan")
            return False
            
        try:
            # 1. Tarkista että fingerprint-järjestelmä on saatavilla
            from enhanced_integrity_manager import EnhancedIntegrityManager
            integrity = EnhancedIntegrityManager("development")
            
            # 2. Generoi fingerprint-rekisteri
            print("🔍 Generoidaan fingerprint-rekisteri...")
            registry = integrity.generate_fingerprint_registry()
            
            # 3. Tallenna fingerprintit paikallisesti
            with open(self.fingerprint_file, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)
            print(f"✅ Fingerprint-rekisteri tallennettu: {len(registry['modules'])} moduulia")
            
            # 4. Tallenna IPFS:ään (mock tai oikea)
            try:
                from mock_ipfs import MockIPFS
                ipfs = MockIPFS()
                
                # Hae nykyinen vaali
                with open('runtime/meta.json', 'r', encoding='utf-8') as f:
                    meta_data = json.load(f)
                election_id = meta_data['election']['id']
                
                # Lukitse järjestelmä
                cid = integrity.lock_system_for_production(ipfs, election_id, "main_node")
                print(f"📦 Fingerprintit tallennettu IPFS:ään: {cid}")
                
            except ImportError:
                print("⚠️  IPFS ei saatavilla - käytetään vain paikallista fingerprintia")
                cid = "local_only"
            
            # 5. Luo lukkotiedosto
            lock_data = {
                "production_locked": True,
                "locked_at": datetime.now().isoformat(),
                "fingerprint_cid": cid,
                "total_modules": len(registry['modules']),
                "election_id": election_id if 'election_id' in locals() else "unknown"
            }
            
            with open(self.lock_file, 'w', encoding='utf-8') as f:
                json.dump(lock_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Järjestelmä lukittu tuotantotilaan")
            print(f"🔒 Lukkotiedosto: {self.lock_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Lukitus epäonnistui: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def verify_on_startup(self):
        """Tarkista järjestelmän eheys käynnistyessä"""
        if not self.lock_file.exists():
            print("🔓 Kehitystila - fingerprint-tarkistus ohitettu")
            return True
            
        print("🔒 Tuotantotila - tarkistetaan fingerprintit...")
        
        try:
            with open(self.lock_file, 'r', encoding='utf-8') as f:
                lock_data = json.load(f)
            
            from enhanced_integrity_manager import verify_system_integrity_enhanced
            
            # Hae vaali ID
            with open('runtime/meta.json', 'r', encoding='utf-8') as f:
                meta_data = json.load(f)
            election_id = meta_data['election']['id']
            
            result = verify_system_integrity_enhanced(election_id, "main_node")
            
            if not result:
                print("❌ JÄRJESTELMÄN EHYS VAARANTUNUT!")
                return False
            
            print("✅ Järjestelmän eheys varmistettu")
            return True
            
        except Exception as e:
            print(f"⚠️  Fingerprint-tarkistus epäonnistui: {e}")
            return False
    
    def get_lock_status(self):
        """Hae lukkotilan tiedot"""
        if not self.lock_file.exists():
            return {"locked": False}
        
        try:
            with open(self.lock_file, 'r', encoding='utf-8') as f:
                lock_data = json.load(f)
            
            return {
                "locked": True,
                "locked_at": lock_data.get("locked_at"),
                "fingerprint_cid": lock_data.get("fingerprint_cid"),
                "total_modules": lock_data.get("total_modules"),
                "election_id": lock_data.get("election_id")
            }
        except:
            return {"locked": False}

def main():
    """Pääohjelma tuotantotilan aktivointiin"""
    lock_manager = ProductionLockManager()
    
    print("🎯 VAAILIJÄRJESTELMÄN TUOTANTOTILAN AKTIVOINTI")
    print("=" * 60)
    
    # Näytä nykyinen tila
    status = lock_manager.get_lock_status()
    if status["locked"]:
        print(f"🔒 Järjestelmä on LUKITTU tuotantotilaan")
        print(f"   Lukittu: {status['locked_at']}")
        print(f"   Fingerprint CID: {status['fingerprint_cid']}")
        print(f"   Moduuleja: {status['total_modules']}")
        print(f"   Vaali: {status['election_id']}")
    else:
        print("🔓 Järjestelmä on KEHITYSTILASSA")
        print("   Fingerprint-tarkistuksia ei suoriteta")
    
    print("\n" + "=" * 60)
    
    # Kysy aktivointi
    if not status["locked"]:
        response = input("Haluatko aktivoida tuotantotilan? (K/e): ").strip().lower()
        if response in ['', 'k', 'kyllä', 'y', 'yes']:
            success = lock_manager.enable_production_mode()
            if success:
                print("\n🎉 TUOTANTOTILA AKTIVOITU ONNISTUNEESTI!")
                print("💡 Kaikki ohjelmat tarkistavat nyt fingerprintit käynnistyessä")
            else:
                print("\n❌ TUOTANTOTILAN AKTIVOINTI EPÄONNISTUI")
        else:
            print("Tuotantotilan aktivointi peruttu")

if __name__ == "__main__":
    main()
