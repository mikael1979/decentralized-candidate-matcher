#!/usr/bin/env python3
"""
Master Node Installation - Luo uuden vaalin ja master-noden
Käyttö: python master-install.py --election-id <id> --config <config_file>
"""

import argparse
import sys
from pathlib import Path

# Lisää polku jotta moduulit löytyvät
sys.path.append(str(Path(__file__).parent))

def main():
    parser = argparse.ArgumentParser(description="Master Node Installation")
    parser.add_argument('--election-id', required=True, help='Vaalin ID')
    parser.add_argument('--config', required=True, help='Konfiguraatiotiedosto')
    parser.add_argument('--namespace', help='IPFS-nimiavaruus (valinnainen)')
    parser.add_argument('--verify', action='store_true', help='Tarkista asennus')
    
    args = parser.parse_args()
    
    print("🎯 MASTER-NODE ASENNUS")
    print("=" * 50)
    
    try:
        from installation_engine import InstallationEngine
        
        engine = InstallationEngine()
        
        if args.verify:
            # Tarkistustila
            print("🔍 Tarkistetaan master-asennusta...")
            success = engine.verify_installation(args.election_id)
            if success:
                print("✅ Master-asennus tarkistettu - kaikki OK!")
                return 0
            else:
                print("❌ Master-asennuksessa ongelmia")
                return 1
        
        # 1. Lataa konfiguraatio
        print(f"📁 Ladataan konfiguraatiota: {args.config}")
        config = engine.load_elections_config(args.config)
        
        # 2. Etsi vaali
        election = None
        for e in config.get('elections', []):
            if e['election_id'] == args.election_id:
                election = e
                break
        
        if not election:
            print(f"❌ Vaalia ei löydy: {args.election_id}")
            print("💡 Saatavilla olevat vaalit:")
            for e in config.get('elections', []):
                print(f"   - {e['election_id']}: {e['name']['fi']}")
            return 1
        
        print(f"🏛️  Vaali löytyi: {election['name']['fi']}")
        
        # 3. Asenna master-node
        print("🔄 Asennetaan master-node...")
        result = engine.install_election(
            election_id=args.election_id,
            elections_data=config,
            first_install=True
        )
        
        if result:
            print("")
            print("✅ MASTER-NODE ASENNETTU ONNISTUNEESTI!")
            print("=" * 40)
            print(f"🏛️  Vaali: {election['name']['fi']}")
            print(f"🆔 Vaali-ID: {args.election_id}") 
            print(f"💻 Machine ID: {result['machine_info']['machine_id']}")
            print(f"👑 Rooli: {result['machine_info']['node_role']}")
            print(f"📅 Asennettu: {result['installation_time'][:19]}")
            print("")
            print("🔗 Seuraavat vaiheet:")
            print("   1. Tarkista asennus: python master-install.py --verify --election-id " + args.election_id)
            print("   2. Lisää worker-nodet: python worker-install.py --election-id " + args.election_id + " --master-node " + result['machine_info']['machine_id'])
            print("   3. Hallinnoi kysymyksiä: python manage_questions.py status")
            return 0
        else:
            print("❌ Master-asennus epäonnistui")
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
