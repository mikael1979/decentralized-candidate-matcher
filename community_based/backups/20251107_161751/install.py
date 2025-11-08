# install.py - PÄIVITETTY MASTER-ASENNUS
#!/usr/bin/env python3
# install.py - PÄIVITETTY VERSIO
"""
Vaalijärjestelmän asennus- ja konfiguraatiotyökalu - PÄIVITETTY
Käyttö: 
  python install.py --config-file=elections_list.json --election-id=vaali_2024 --first-install
  python install.py --config-file=elections_list.json --election-id=vaali_2024 (työasema)
"""

import argparse
import sys
from pathlib import Path

# Lisää nykyinen hakemisto polkuun
sys.path.append('.')

def main():
    parser = argparse.ArgumentParser(description="Vaalijärjestelmän asennus - PÄIVITETTY")
    parser.add_argument('--config-file', required=True, help='Konfiguraatiotiedosto (elections_list.json)')
    parser.add_argument('--election-id', required=True, help='Asennettavan vaalin ID')
    parser.add_argument('--first-install', action='store_true', help='Ensimmäinen asennus (master-kone)')
    parser.add_argument('--output-dir', default='runtime', help='Output-hakemisto')
    parser.add_argument('--verify', action='store_true', help='Tarkista asennus')
    parser.add_argument('--master-cid', help='Master-noden CID (työasemalle)')
    
    args = parser.parse_args()
    
    print("🎯 VAAILIJÄRJESTELMÄN ASENNUS - PÄIVITETTY")
    print("=" * 60)
    
    try:
        # Tuo riippuvuudet
        from mock_ipfs import MockIPFS
        from installation_engine import InstallationEngine
        from metadata_manager import get_metadata_manager
        from enhanced_integrity_manager import EnhancedIntegrityManager
        
        # Alusta IPFS (mock)
        ipfs = MockIPFS()
        
        # Alusta asennusmoottori
        engine = InstallationEngine(args.output_dir)
        engine.set_ipfs_client(ipfs)
        
        if args.verify:
            # Tarkista asennus
            print("🔍 TARKISTETAAN ASENNUS...")
            success = engine.verify_installation(args.election_id)
            if success:
                print("✅ Asennus tarkistettu onnistuneesti")
                return True
            else:
                print("❌ Asennuksen tarkistus epäonnistui")
                return False
        
        # Lataa konfiguraatio
        elections_data = engine.load_elections_config(args.config_file)
        
        # Listaa saatavilla olevat vaalit
        engine.list_available_elections(elections_data)
        
        # Tarkista että vaali on olemassa konfiguraatiossa
        election_exists = any(e['election_id'] == args.election_id for e in elections_data['elections'])
        if not election_exists:
            print(f"❌ Vaalia '{args.election_id}' ei löydy konfiguraatiosta")
            return False
        
        # Päätä first-install tila
        first_install = args.first_install
        if not first_install:
            # Automaattinen first-install päätös
            metadata_manager = get_metadata_manager(args.output_dir)
            machine_info = metadata_manager.get_machine_info()
            
            print("🔍 FIRST-INSTALL PÄÄTÖSLOGIIKKA:")
            print(f"   Vaali '{args.election_id}' elections_list.json:ssa: {election_exists}")
            print(f"   Vaali asennettuna nykyiseen koneeseen: {machine_info['election_id'] == args.election_id}")
            
            # Päätä first-install tila
            if machine_info['election_id'] == 'unknown':
                first_install = True
                print("   📊 PÄÄTÖS: Ensimmäinen asennus (ei aiempaa vaalia)")
            elif machine_info['election_id'] != args.election_id:
                first_install = False
                print("   📊 PÄÄTÖS: Liity olemassa olevaan vaaliin (eri vaali asennettuna)")
            else:
                first_install = False
                print("   📊 PÄÄTÖS: Päivitä olemassa olevaa asennusta")
        
        if first_install:
            print("👑 MASTER-NODE ASENNUS")
            print("=" * 40)
            
            # 1. Asenna vaali
            result = engine.install_election(args.election_id, elections_data, first_install)
            
            # 2. Luo vaalirekisteri
            metadata_manager = get_metadata_manager(args.output_dir)
            registry = metadata_manager.create_election_registry(result['election'])
            
            # 3. Alusta IPFS-lohkot
            from enhanced_recovery_manager import EnhancedRecoveryManager
            recovery_manager = EnhancedRecoveryManager(
                args.output_dir, ipfs, args.election_id, machine_info['machine_id']
            )
            metadata_cid = recovery_manager.initialize_recovery_system()
            
            # 4. Luo master-noden identiteetti IPFS:ään
            master_node_data = {
                "election_id": args.election_id,
                "node_id": machine_info['machine_id'],
                "node_type": "master",
                "ipfs_blocks_metadata_cid": metadata_cid,
                "created_at": result['installation_time'],
                "capabilities": ["master_operations", "worker_registration", "data_sync"]
            }
            
            master_cid = ipfs.upload(master_node_data)
            
            # 5. Päivitä elections_list master-CID:llä
            for election in elections_data['elections']:
                if election['election_id'] == args.election_id:
                    election['master_node_cid'] = master_cid
                    election['installation_status'] = 'master_installed'
                    break
            
            # Tallenna päivitetty elections_list
            with open(args.config_file, 'w', encoding='utf-8') as f:
                json.dump(elections_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Master-node rekisteröity: {master_cid}")
            
        else:
            print("💻 TYÖASEMAN ASENNUS")
            print("=" * 40)
            
            # Etsi master-CID
            master_cid = args.master_cid
            if not master_cid:
                for election in elections_data['elections']:
                    if election['election_id'] == args.election_id:
                        master_cid = election.get('master_node_cid')
                        break
            
            if not master_cid:
                print("❌ Master-noden CID puuttuu. Käytä --master-cid tai varmista että elections_list on päivitetty.")
                return False
            
            print(f"🔗 Yhdistetään master-nodeen: {master_cid}")
            
            # 1. Lataa master-noden tiedot
            master_data = ipfs.download(master_cid)
            if not master_data:
                print("❌ Master-noden tietoja ei voitu ladata")
                return False
            
            # 2. Asenna vaali
            result = engine.install_election(args.election_id, elections_data, first_install)
            
            # 3. Rekisteröi työasema master-nodeen
            metadata_manager = get_metadata_manager(args.output_dir)
            machine_info = metadata_manager.get_machine_info()
            
            worker_registered = metadata_manager.register_worker_node(
                machine_info['machine_id'], 
                args.election_id
            )
            
            if not worker_registered:
                print("⚠️  Työasemaa ei voitu rekisteröidä - jatketaan offline-tilassa")
            
            # 4. Alusta IPFS-lohkot työasemalle
            from enhanced_recovery_manager import EnhancedRecoveryManager
            recovery_manager = EnhancedRecoveryManager(
                args.output_dir, ipfs, args.election_id, machine_info['machine_id']
            )
            
            # Yritä synkronoida master-noden lohkometadata
            try:
                metadata_cid = master_data.get('ipfs_blocks_metadata_cid')
                if metadata_cid:
                    # Tässä vaiheessa pitäisi oikeasti synkronoida lohkot masterilta
                    # Mutta nyt alustetaan oma järjestelmä
                    recovery_manager.initialize_recovery_system()
                    print("✅ IPFS-lohkot alustettu työasemalle")
                else:
                    recovery_manager.initialize_recovery_system()
                    print("✅ IPFS-lohkot alustettu (standalone-tilassa)")
            except Exception as e:
                print(f"⚠️  IPFS-lohkojen alustus epäonnistui: {e}")
                recovery_manager.initialize_recovery_system()
        
        print("\n✅ ASENNUS ONNISTUI!")
        print("=" * 40)
        print(f"🏛️  Vaali: {result['election']['name']['fi']}")
        print(f"💻 Kone-ID: {result['machine_info']['machine_id']}")
        print(f"👑 Rooli: {'MASTER-NODE' if first_install else 'TYÖASEMA'}")
        if first_install:
            print(f"🔗 Master-CID: {master_cid}")
        print(f"📁 Hakemisto: {args.output_dir}")
        print(f"⏰ Aikaleima: {result['installation_time']}")
        
        # Tarkista asennus
        print("\n🔍 TARKISTETAAN ASENNUS...")
        verification_success = engine.verify_installation(args.election_id)
        
        if verification_success:
            print("\n💡 KÄYTTÖÖNOTTO VALMIS!")
            print("=" * 40)
            
            if first_install:
                print("🎯 MASTER-NODE TOIMINNOT:")
                print("   - Luo työasemia komennolla:")
                print(f"     python install.py --config-file={args.config_file} --election-id={args.election_id}")
                print(f"   - Master-CID: {master_cid}")
                print("   - Hallinnoi kysymysten synkronointia")
                print("   - Aktivoi tuotantotila: python enable_production.py")
            else:
                print("🎯 TYÖASEMAN TOIMINNOT:")
                print("   - Osallistu vertailuihin: python demo_comparisons.py")
                print("   - Tarkista tila: python system_bootstrap.py")
                print("   - Synkronoi data master-noden kanssa")
            
            print("\n📊 TESTAA JÄRJESTELMÄÄ:")
            print("   python system_bootstrap.py          # Tarkista käynnistys")
            print("   python manage_questions.py status   # Kysymysten tila")
            print("   python demo_comparisons.py --user testi --count 3")
            
            return True
        else:
            print("❌ Asennuksen tarkistus epäonnistui - tarkista tiedostot")
            return False
            
    except ImportError as e:
        print(f"❌ Riippuvuus puuttuu: {e}")
        print("💡 Varmista että kaikki moduulit ovat saatavilla")
        return False
    except Exception as e:
        print(f"❌ Asennus epäonnistui: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
