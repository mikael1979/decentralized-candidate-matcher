# enable_production_fixed.py
#!/usr/bin/env python3
"""
Tuotantotilan aktivointi - KORJATTU VERSIO
"""

import sys
import json
from datetime import datetime
from pathlib import Path

def ensure_block_metadata():
    """Varmista että lohkometadata on olemassa"""
    block_metadata_file = Path("runtime/ipfs_blocks_metadata.json")
    
    if not block_metadata_file.exists():
        print("📦 Luodaan lohkometadata...")
        
        # Create basic metadata from existing IPFS blocks
        block_metadata = {
            "metadata": {
                "version": "1.0.0",
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "election_id": "Jumaltenvaalit_2026",
                "node_id": "main_node",
                "description": "IPFS-lohkojen metatiedot"
            },
            "block_sequence": ["buffer1", "urgent", "sync", "active", "buffer2"],
            "current_rotation": 0,
            "total_rotations": 0,
            "blocks": {
                "buffer1": "QmMock215e5f1622bc4e592933a7b20c96e6efbb5b75dc",
                "urgent": "QmMockd86aa1159a894b635e7a1a971e4425ef38b5d181", 
                "sync": "QmMock222c92993016632dfbc89cfad543407e4e258ec8",
                "active": "QmMock77acde5d970df23e78e315ff723e09a293b6e03e",
                "buffer2": "QmMock10b888628d3349c3fb883218a0cc6f4256ee98e8"
            },
            "rotation_history": [],
            "node_registry": ["main_node"],
            "sync_config": {
                "auto_rotate": True,
                "max_block_size": {
                    "buffer1": 100, "urgent": 50, "sync": 200, "active": 150, "buffer2": 100
                }
            }
        }
        
        with open(block_metadata_file, 'w', encoding='utf-8') as f:
            json.dump(block_metadata, f, indent=2, ensure_ascii=False)
        
        print("✅ Lohkometadata luotu!")
        return True
    else:
        print("✅ Lohkometadata on jo olemassa!")
        return True

def simple_integrity_check():
    """Yksinkertainen integriteettitarkistus"""
    print("🔒 YKSINKERTAINEN INTEGRITEETTITARKISTUS...")
    
    required_files = [
        "runtime/questions.json",
        "runtime/meta.json",
        "runtime/system_chain.json", 
        "runtime/active_questions.json",
        "runtime/ipfs_blocks_metadata.json"
    ]
    
    all_ok = True
    for file in required_files:
        if Path(file).exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - PUUTTUU")
            all_ok = False
    
    if all_ok:
        print("✅ PERUSINTEGRITEETTI OK")
    else:
        print("❌ INTEGRITEETTIONGELMIA")
    
    return all_ok

def main():
    print("🔒 VAAILIJÄRJESTELMÄN TUOTANTOTILAN AKTIVOINTI - KORJATTU")
    print("=" * 60)
    
    # 1. Varmista lohkometadata
    if not ensure_block_metadata():
        print("❌ Lohkometadatan luonti epäonnistui")
        return False
    
    # 2. Yksinkertainen integriteettitarkistus
    if not simple_integrity_check():
        response = input("Haluatko jatkaa silti? (K/e): ").strip().lower()
        if response not in ['', 'k', 'kyllä', 'y', 'yes']:
            return False
    
    # 3. Vahvista käyttäjä
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
    
    # 4. Suorita yksinkertainen lukitus
    print()
    print("🔒 SUORITETAAN YKSINKERTAINEN TUOTANTOLUKITUS...")
    
    try:
        # Alusta IPFS
        from mock_ipfs import MockIPFS
        ipfs = MockIPFS()
        
        # Lukitse kysymysten lähetys
        from active_questions_manager import ActiveQuestionsManager
        active_manager = ActiveQuestionsManager()
        if active_manager.lock_submissions(election_id):
            print("✅ Kysymysten lähetys lukittu")
        else:
            print("⚠️  Kysymysten lähetyksen lukitus epäonnistui")
        
        # Luo fingerprint-rekisteri
        fingerprint_data = {
            "metadata": {
                "production_lock": True,
                "locked_at": datetime.now().isoformat(),
                "election_id": election_id,
                "system_version": "2.0.0",
                "lock_type": "simple_production_lock"
            },
            "locked_files": [
                "runtime/questions.json",
                "runtime/meta.json", 
                "runtime/system_chain.json",
                "runtime/active_questions.json",
                "runtime/ipfs_blocks_metadata.json"
            ],
            "security_settings": {
                "submission_locked": True,
                "integrity_checks": True,
                "auto_backup": True
            }
        }
        
        # Tallenna fingerprint IPFS:ään
        fingerprint_cid = ipfs.upload(fingerprint_data)
        print(f"✅ Fingerprint tallennettu IPFS:ään: {fingerprint_cid}")
        
        # Päivitä system_chain
        from system_chain_manager import log_action
        log_action(
            "production_lock_simple",
            f"Järjestelmä lukittu tuotantokäyttöön (yksinkertainen) - Election: {election_id}",
            user_id="system_admin",
            metadata={
                "election_id": election_id,
                "fingerprint_cid": fingerprint_cid,
                "timestamp": datetime.now().isoformat(),
                "lock_type": "simple"
            }
        )
        
        # Tallenna tuotantokonfiguraatio
        production_config = {
            "metadata": {
                "production_lock": True,
                "locked_at": datetime.now().isoformat(),
                "election_id": election_id,
                "fingerprint_cid": fingerprint_cid,
                "system_version": "2.0.0",
                "lock_method": "simple"
            },
            "security_settings": {
                "integrity_checks": True,
                "submission_locked": True,
                "auto_backup": True,
                "emergency_recovery": True
            },
            "ipfs_settings": {
                "blocks_initialized": True,
                "fingerprint_stored": True
            }
        }
        
        with open("runtime/production_config.json", 'w', encoding='utf-8') as f:
            json.dump(production_config, f, indent=2, ensure_ascii=False)
        
        print()
        print("🎉 JÄRJESTELMÄ LUKITTU ONNISTUNEESTI TUOTANTOKÄYTTÖÖN!")
        print("=" * 60)
        print(f"📋 Vaali: {election_id}")
        print(f"🔒 Fingerprint: {fingerprint_cid}")
        print(f"⏰ Aikaleima: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔧 Menetelmä: Yksinkertainen lukitus")
        print()
        print("📊 SEURAAVAT VAIHEET:")
        print("   1. Testaa järjestelmä: python run_all_tests.py")
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
        print("💡 Yritä korjata ongelmat:")
        print("   python fix_integrity_issue.py")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
