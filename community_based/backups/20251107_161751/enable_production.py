# enable_production.py - PÄIVITETTY VERSIO
#!/usr/bin/env python3
"""
Tuotantotilan aktivointi - LUKITSEE järjestelmän käyttöön
PÄIVITETTY: Tarkistaa onko järjestelmä jo tuotannossa
"""

import sys
import json
from datetime import datetime
from pathlib import Path

def is_system_already_locked():
    """Tarkista onko järjestelmä jo lukittu tuotantoon"""
    production_config = Path("runtime/production_config.json")
    if production_config.exists():
        with open(production_config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config["metadata"]["production_lock"]
    return False

def main():
    print("🔒 VAAILIJÄRJESTELMÄN TUOTANTOTILAN AKTIVOINTI")
    print("=" * 60)
    
    # Tarkista onko jo lukittu
    if is_system_already_locked():
        print("ℹ️  JÄRJESTELMÄ ON JO LUKITTU TUOTANTOON!")
        print("💡 Ei tarvitse lukita uudelleen.")
        print("\n📊 Nykyinen tila:")
        
        with open("runtime/production_config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        metadata = config["metadata"]
        print(f"   🆔 Vaali: {metadata['election_id']}")
        print(f"   ⏰ Lukittu: {metadata['locked_at'][:19]}")
        print(f"   🔑 Lock ID: {metadata['lock_entry_id']}")
        
        response = input("\nHaluatko nollata lukituksen ja palata kehitystilaan? (k/E): ").strip().lower()
        if response in ['k', 'kyllä', 'y', 'yes']:
            return reset_to_development()
        else:
            return True
    
    print("Tämä komento lukitsee järjestelmän tuotantokäyttöön.")
    print("Lukituksen jälkeen:")
    print("  - Kysymysten lähetys lukitaan")
    print("  - Fingerprint-rekisteri tallennetaan IPFS:ään")
    print("  - Järjestelmä siirtyy development-tilasta production-tilaan")
    print("  - Integriteettivalvonta aktivoituu")
    print()
    
    # Tarkista että järjestelmä on alustettu
    runtime_files = [
        "runtime/questions.json",
        "runtime/meta.json", 
        "runtime/system_chain.json",
        "runtime/active_questions.json"
    ]
    
    missing_files = []
    for file in runtime_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ JÄRJESTELMÄ EI OLE ALUSTETTU!")
        print("Puuttuvat tiedostot:")
        for file in missing_files:
            print(f"  - {file}")
        print()
        print("💡 Alusta järjestelmä ensin:")
        print("   python complete_initialization.py")
        return False
    
    # Korjaa mahdolliset syntax errorit ensin
    print("🧪 TARKISTETAAN JÄRJESTELMÄN TILA...")
    try:
        from enhanced_integrity_manager import verify_system_integrity_enhanced
        integrity_ok = verify_system_integrity_enhanced("default_election", "main_node")
        
        if not integrity_ok:
            print("❌ INTEGRITEETTITARKISTUS EPÄONNISTUI!")
            print("💡 Korjaa ongelmat ennen tuotantoon siirtymistä.")
            response = input("Haluatko yrittää korjata syntax errorin automaattisesti? (K/e): ").strip().lower()
            if response in ['', 'k', 'kyllä', 'y', 'yes']:
                from fix_syntax_error import fix_syntax_error
                if fix_syntax_error():
                    print("🔄 Yritetään uudelleen...")
                    integrity_ok = verify_system_integrity_enhanced("default_election", "main_node")
            
            if not integrity_ok:
                print("💡 Korjaa ongelmat manuaalisesti tai suorita: python run_all_tests.py")
                return False
            
    except Exception as e:
        print(f"⚠️  Integriteettitarkistus epäonnistui: {e}")
        print("💡 Suorita testit manuaalisesti: python run_all_tests.py")
        response = input("Haluatko jatkaa silti? (K/e): ").strip().lower()
        if response not in ['', 'k', 'kyllä', 'y', 'yes']:
            return False
    
    # Vahvista käyttäjä
    print()
    print("🚨 TUOTANTOLUKITUS ON PERUUTAMATON TOIMINTO!")
    print("   - Kysymyksiä ei voi enää lähettää")
    print("   - Järjestelmä siirtyy täyteen turvallisuustilaan")
    print("   - Kaikki muutokset tallennetaan IPFS-lohkoihin")
    print()
    
    election_id = input("Vaalien ID (esim. Jumaltenvaalit_2026): ").strip()
    if not election_id:
        election_id = "Jumaltenvaalit_2026"
    
    confirmation = input(f"Lukitaanko järjestelmä vaaleille '{election_id}'? (KIRJOITA 'LOCK' vahvistaaksesi): ")
    if confirmation != "LOCK":
        print("🔧 Lukitus peruttu")
        return True
    
    # Suorita lukitus
    print()
    print("🔒 SUORITETAAN TUOTANTOLUKITUS...")
    
    try:
        # 1. Alusta IPFS
        from mock_ipfs import MockIPFS
        ipfs = MockIPFS()
        
        # 2. Aktivoi integriteettivalvonta KEHYSTILASSA
        from enhanced_integrity_manager import EnhancedIntegrityManager
        integrity = EnhancedIntegrityManager("development", ipfs)  # Tärkeä: development-tilassa lukitaan
        
        # 3. Lukitse järjestelmä
        lock_entry_id = integrity.lock_system_for_production(ipfs, election_id, "main_node")
        
        # 4. Lukitse kysymysten lähetys
        from active_questions_manager import ActiveQuestionsManager
        active_manager = ActiveQuestionsManager()
        active_manager.lock_submissions(election_id)
        
        # 5. Päivitä system_chain
        from system_chain_manager import log_action
        log_action(
            "production_lock",
            f"Järjestelmä lukittu tuotantokäyttöön - Election: {election_id}",
            user_id="system_admin",
            metadata={
                "election_id": election_id,
                "lock_entry_id": lock_entry_id,
                "timestamp": datetime.now().isoformat(),
                "fingerprint_verified": True
            }
        )
        
        # 6. Tallenna tuotantokonfiguraatio
        production_config = {
            "metadata": {
                "production_lock": True,
                "locked_at": datetime.now().isoformat(),
                "election_id": election_id,
                "lock_entry_id": lock_entry_id,
                "system_version": "2.0.0"
            },
            "security_settings": {
                "integrity_checks": True,
                "submission_locked": True,
                "auto_backup": True,
                "emergency_recovery": True
            },
            "ipfs_settings": {
                "blocks_initialized": True,
                "recovery_enabled": True
            }
        }
        
        with open("runtime/production_config.json", 'w', encoding='utf-8') as f:
            json.dump(production_config, f, indent=2, ensure_ascii=False)
        
        print()
        print("🎉 JÄRJESTELMÄ LUKITTU ONNISTUNEESTI TUOTANTOKÄYTTÖÖN!")
        print("=" * 60)
        print(f"📋 Vaali: {election_id}")
        print(f"🔒 Lukitus: {lock_entry_id}")
        print(f"⏰ Aikaleima: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print("📊 SEURAAVAT VAIHEET:")
        print("   1. Tarkista käyttöönotto: python run_all_tests.py")
        print("   2. Synkronoi työasemat: python sync_questions_from_master.py")
        print("   3. Käynnistä äänestys: python demo_voting.py")
        print()
        print("💡 KÄYTTÖOHJEET:")
        print("   - Kysymysten vertailu: python demo_comparisons.py")
        print("   - Äänestys: python demo_voting.py")
        print("   - Tilaseuranta: python manage_questions.py status")
        
        return True
        
    except Exception as e:
        print(f"❌ LUKITUS EPÄONNISTUI: {e}")
        print("💡 Tarkista että kaikki komponentit on alustettu:")
        print("   python complete_initialization.py")
        return False

def reset_to_development():
    """Nollaa tuotantolukitus ja palaa kehitystilaan"""
    print("\n🔄 PALAUTETAAN KEHITYSTILAAN...")
    
    try:
        # 1. Poista tuotantokonfiguraatio
        production_config = Path("runtime/production_config.json")
        if production_config.exists():
            production_config.unlink()
        
        # 2. Avaa kysymysten lähetys
        from active_questions_manager import ActiveQuestionsManager
        active_manager = ActiveQuestionsManager()
        active_manager.unlock_submissions()
        
        # 3. Päivitä system_chain
        from system_chain_manager import log_action
        log_action(
            "development_reset",
            "Järjestelmä palautettu kehitystilaan",
            user_id="system_admin",
            metadata={
                "reset_timestamp": datetime.now().isoformat(),
                "reason": "manual_reset"
            }
        )
        
        print("✅ JÄRJESTELMÄ PALAUTETTU KEHITYSTILAAN!")
        print("💡 Nyt voit tehdä muutoksia ja lukita uudelleen tarvittaessa.")
        return True
        
    except Exception as e:
        print(f"❌ Kehitystilaan palautus epäonnistui: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
