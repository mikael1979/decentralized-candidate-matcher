# production_lock_manager.py - UUSI MODUULI
#!/usr/bin/env python3
"""
Tuotantolukituksen hallinta - Tarkistaa fingerprintit käynnistyessä
"""

import json
from pathlib import Path

class ProductionLockManager:
    def __init__(self):
        self.lock_file = Path("runtime/production.lock")
        self.fingerprint_file = Path("runtime/file_fingerprints.json")
    
    def is_production_locked(self):
        """Onko järjestelmä lukittu tuotantotilaan?"""
        return self.lock_file.exists()
    
    def verify_on_startup(self):
        """Tarkista fingerprintit käynnistyessä"""
        if not self.is_production_locked():
            print("🔓 Kehitystila - fingerprint-tarkistus ohitettu")
            return True
        
        print("🔒 Tuotantotila - tarkistetaan fingerprintit...")
        
        try:
            from enhanced_integrity_manager import verify_system_integrity_enhanced
            
            # Hae vaali ID
            with open('runtime/meta.json', 'r', encoding='utf-8') as f:
                meta_data = json.load(f)
            election_id = meta_data['election']['id']
            
            # Suorita täydellinen integriteettitarkistus
            result = verify_system_integrity_enhanced(election_id, "main_node")
            
            if not result:
                print("❌ JÄRJESTELMÄN EHYS VAARANTUNUT!")
                print("🚫 Ohjelma pysäytetty turvallisuussyistä")
                return False
            
            print("✅ Järjestelmän eheys varmistettu")
            return True
            
        except Exception as e:
            print(f"⚠️  Fingerprint-tarkistus epäonnistui: {e}")
            # Tuotantotilassa epäonnistuminen on vakava
            if self.is_production_locked():
                print("🚫 Ohjelma pysäytetty turvallisuussyistä")
                return False
            return True
