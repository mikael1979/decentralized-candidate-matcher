#!/usr/bin/env python3
# enable_production.py
"""
Aktivoi tuotantotila - KÄYTTÖ: python enable_production.py
"""

import sys
from pathlib import Path

def main():
    """Pääohjelma tuotantotilan aktivointiin"""
    
    print("🎯 VAAILIJÄRJESTELMÄN TUOTANTOTILAN AKTIVOINTI")
    print("=" * 60)
    
    try:
        # Tuo production lock manager
        from production_lock_manager import ProductionLockManager
        
        lock_manager = ProductionLockManager()
        
        # Näytä nykyinen tila
        status = lock_manager.get_lock_status()
        if status["locked"]:
            print(f"🔒 Järjestelmä on JO LUKITTU tuotantotilaan")
            print(f"   Lukittu: {status['locked_at']}")
            print(f"   Fingerprint CID: {status['fingerprint_cid']}")
            print(f"   Moduuleja: {status['total_modules']}")
            print(f"   Vaali: {status['election_id']}")
            print("\n💡 Järjestelmä on jo turvallisuustilassa")
            return True
        else:
            print("🔓 Järjestelmä on KEHITYSTILASSA")
            print("   - Fingerprint-tarkistuksia ei suoriteta")
            print("   - Ohjelmatiedostoja voi muokata vapaasti")
            print("   - Ei tuotantotason turvallisuutta")
        
        print("\n" + "=" * 60)
        print("📋 TUOTANTOTILAN EDUT:")
        print("   ✅ Estää ohjelmatiedostojen muuttamisen")
        print("   ✅ Varmistaa järjestelmän eheyden")
        print("   ✅ Lisää turvallisuutta tuotantokäyttöön")
        print("   ✅ Pakottaa versionhallinnan")
        print("")
        print("⚠️  HUOMIO:")
        print("   - Et voi enää muokata ohjelmatiedostoja")
        print("   - Kaikki muutokset vaativat uuden fingerprintin")
        print("   - Testaa järjestelmä ennen aktivointia")
        
        print("\n" + "=" * 60)
        
        # Kysy vahvistus
        response = input("Haluatko varmasti aktivoida tuotantotilan? (K/e): ").strip().lower()
        
        if response in ['', 'k', 'kyllä', 'y', 'yes']:
            print("\n🔒 AKTIVOIDAAN TUOTANTOTILA...")
            print("Tämä voi kestää hetken...")
            
            success = lock_manager.enable_production_mode()
            
            if success:
                print("\n🎉 TUOTANTOTILA AKTIVOITU ONNISTUNEESTI!")
                print("=" * 50)
                print("🔐 TURVALLISUUS TOIMINNOT AKTIVOITU:")
                print("   ✅ Kaikki ohjelmat tarkistavat fingerprintit")
                print("   ✅ Järjestelmän eheys varmistettu")
                print("   ✅ IPFS-fingerprint tallennettu")
                print("   ✅ Tuotantotasoinen turvallisuus")
                print("")
                print("💡 SEURAAVAT VAIHEET:")
                print("   1. Testaa kaikki ohjelmat uudelleenkäynnistyksellä")
                print("   2. Varmista että IPFS-synkronointi toimii")
                print("   3. Aktivoi kysymysten lähetyksen lukitus")
                print("   4. Käynnistä vaalikone tuotantokäyttöön")
                print("")
                print("🚨 TÄRKEÄÄ:")
                print("   - Älä muokkaa ohjelmatiedostoja enää!")
                print("   - Kaikki muutokset vaativat uuden version")
                print("   - Käytä versionhallintaa jatkokehitykseen")
                
                return True
            else:
                print("\n❌ TUOTANTOTILAN AKTIVOINTI EPÄONNISTUI")
                print("Tarkista virheilmoitus ja yritä uudelleen")
                return False
        else:
            print("\n🔓 Tuotantotilan aktivointi peruttu")
            print("Järjestelmä pysyy kehitystilassa")
            return True
            
    except ImportError as e:
        print(f"❌ TUOTANTOTILAN HALLINTA EI SAATAVILLA")
        print(f"   Virhe: {e}")
        print("")
        print("💡 RATKAISU:")
        print("   1. Toteuta production_lock_manager.py ensin")
        print("   2. Varmista että enhanced_integrity_manager.py on saatavilla")
        print("   3. Tarkista että kaikki riippuvuudet on asennettu")
        return False
    
    except Exception as e:
        print(f"❌ ODOTTAMATON VIRHE: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
