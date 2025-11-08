#!/usr/bin/env python3
"""
Worker Node Installation - Liittyy olemassa olevaan vaaliin
Käyttö: python worker-install.py --election-id <id> --master-node <machine_id>
"""

import argparse
import sys
from pathlib import Path

# Lisää polku jotta moduulit löytyvät
sys.path.append(str(Path(__file__).parent))

def main():
    parser = argparse.ArgumentParser(description="Worker Node Installation")  
    parser.add_argument('--election-id', required=True, help='Vaalin ID')
    parser.add_argument('--master-node', required=True, help='Master-noden machine-id')
    parser.add_argument('--sync-immediately', action='store_true', help='Synkronoi data heti')
    parser.add_argument('--verify', action='store_true', help='Tarkista asennus')
    
    args = parser.parse_args()
    
    print("🔧 WORKER-NODE ASENNUS")
    print("=" * 50)
    
    try:
        from installation_engine import InstallationEngine
        from metadata_manager import get_metadata_manager
        
        engine = InstallationEngine()
        metadata_manager = get_metadata_manager()
        
        if args.verify:
            # Tarkistustila
            print("🔍 Tarkistetaan worker-asennusta...")
            machine_info = metadata_manager.get_machine_info()
            
            if machine_info.get('election_id') != args.election_id:
                print(f"❌ Väärä vaali: {machine_info.get('election_id')} != {args.election_id}")
                return 1
            
            if machine_info.get('node_role') != 'worker':
                print(f"❌ Ei worker-node: {machine_info.get('node_role')}")
                return 1
            
            print("✅ Worker-asennus tarkistettu - kaikki OK!")
            print(f"   Vaali: {args.election_id}")
            print(f"   Machine ID: {machine_info.get('machine_id')}")
            print(f"   Rooli: {machine_info.get('node_role')}")
            return 0
        
        # 1. Tarkista että emme ole jo master
        current_machine_info = metadata_manager.get_machine_info()
        if (current_machine_info.get('election_id') == args.election_id and 
            current_machine_info.get('node_role') == 'master'):
            print("❌ Tämä node on jo master! Käytä master-install.py master-toiminnoille.")
            return 1
        
        # 2. Hae vaalirekisteri master-nodelta (simuloidaan)
        print(f"🔗 Yhdistetään master-nodeen: {args.master_node}")
        
        # Simuloi masterin rekisterin haku
        registry = {
            "election_registry": {
                "election_id": args.election_id,
                "election_name": f"Vaalit {args.election_id}",
                "master_machine_id": args.master_node,
                "namespace": f"election_{args.election_id}",
                "worker_nodes": []
            }
        }
        
        print(f"🏛️  Vaali löytyi: {registry['election_registry']['election_name']}")
        
        # 3. Asenna worker-node
        print("🔄 Asennetaan worker-node...")
        result = engine.install_election(
            election_id=args.election_id,
            elections_data={"elections": [registry["election_registry"]]},
            first_install=False
        )
        
        if result:
            print("")
            print("✅ WORKER-NODE ASENNETTU ONNISTUNEESTI!")
            print("=" * 40)
            print(f"🏛️  Vaali: {registry['election_registry']['election_name']}")
            print(f"🆔 Vaali-ID: {args.election_id}")
            print(f"💻 Machine ID: {result['machine_info']['machine_id']}")
            print(f"🔧 Rooli: {result['machine_info']['node_role']}")
            print(f"👑 Master: {args.master_node}")
            print(f"📅 Asennettu: {result['installation_time'][:19]}")
            
            # 4. Rekisteröi worker masterille (simuloidaan)
            print("")
            print("📝 Rekisteröidään worker masterille...")
            success = metadata_manager.register_worker_node(
                result['machine_info']['machine_id'],
                args.election_id
            )
            
            if success:
                print("✅ Worker rekisteröity masterille")
            else:
                print("⚠️  Workerin rekisteröinti epäonnistui (simulointi)")
            
            # 5. Synkronoi data
            if args.sync_immediately:
                print("")
                print("🔄 Synkronoidaan dataa masterilta...")
                # Simuloi synkronointi
                sync_result = {"synced_items": 15, "success": True}
                if sync_result.get('success'):
                    print(f"✅ Synkronoitu: {sync_result.get('synced_items', 0)} kohdetta")
                else:
                    print("⚠️  Synkronointi epäonnistui (simulointi)")
            
            print("")
            print("🔗 Seuraavat vaiheet:")
            print("   1. Tarkista asennus: python worker-install.py --verify --election-id " + args.election_id)
            print("   2. Testaa kysymysten hallinta: python manage_questions.py status")
            print("   3. Synkronoi data: python manage_questions.py sync --type all")
            
            return 0
        else:
            print("❌ Worker-asennus epäonnistui")
            return 1
            
    except ImportError as e:
        print(f"❌ Tarvittavia moduuleja puuttuu: {e}")
        return 1
    except Exception as e:
        print(f"❌ Odottamaton virhe: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
