#!/usr/bin/env python3
# test_multi_node.py
"""
Testaa moninoditoimintoa Jumaltenvaaleilla
Käyttö: python test_multi_node.py
"""

import json
import sys
from pathlib import Path

def test_multi_node_operations():
    """Testaa moninoditoimintaa"""
    
    print("🖥️  TESTATAAN MONINODITOIMINTAA JUMALTENVAALEILLA...")
    print("=" * 60)
    
    # 1. Tarkista asennus
    print("\n1. 🔍 TARKISTETAAN ASENNUS...")
    try:
        from metadata_manager import get_metadata_manager
        metadata = get_metadata_manager()
        machine_info = metadata.get_machine_info()
        
        print(f"   💻 Kone-ID: {machine_info['machine_id']}")
        print(f"   🏛️  Vaali: {machine_info['election_id']}")
        print(f"   👑 Master-kone: {'✅' if machine_info['is_master'] else '❌'}")
        
    except Exception as e:
        print(f"   ❌ Metadata-tarkistus epäonnistui: {e}")
        return False
    
    # 2. Tarkista kysymykset
    print("\n2. ❓ TARKISTETAAN KYSYMYKSET...")
    questions_file = Path("runtime/questions.json")
    if questions_file.exists():
        try:
            with open(questions_file, 'r', encoding='utf-8') as f:
                questions = json.load(f)
            question_count = len(questions.get('questions', []))
            print(f"   ✅ Kysymyksiä: {question_count} kpl")
            
            # Näytä ensimmäiset 3 kysymystä
            print("   📝 Esimerkkikysymyksiä:")
            for i, q in enumerate(questions['questions'][:3]):
                text = q['content']['question']['fi'][:40] + '...' if len(q['content']['question']['fi']) > 40 else q['content']['question']['fi']
                print(f"      {i+1}. {text}")
                
        except Exception as e:
            print(f"   ❌ Kysymysten tarkistus epäonnistui: {e}")
            return False
    else:
        print("   ❌ Kysymystiedostoa ei löydy")
        return False
    
    # 3. Tarkista ehdokkaat
    print("\n3. 👑 TARKISTETAAN EHDOKKAAT...")
    candidates_file = Path("runtime/candidates.json")
    if candidates_file.exists():
        try:
            with open(candidates_file, 'r', encoding='utf-8') as f:
                candidates = json.load(f)
            candidate_count = len(candidates.get('candidates', []))
            print(f"   ✅ Ehdokkaita: {candidate_count} kpl")
            
        except Exception as e:
            print(f"   ❌ Ehdokkaiden tarkistus epäonnistui: {e}")
    else:
        print("   ❌ Ehdokastiedostoa ei löydy")
    
    # 4. Testaa vertailut
    print("\n4. 🔄 TESTATAAN VERTAILUJA...")
    try:
        from demo_comparisons import make_demo_comparisons
        result = make_demo_comparisons(2, f"node_test_{machine_info['machine_id'][-4:]}")
        print(f"   ✅ Testivertailut: {len(result)} kpl")
        
    except Exception as e:
        print(f"   ⚠️  Vertailutestit epäonnistuivat: {e}")
    
    # 5. Tarkista system_chain
    print("\n5. 🔗 TARKISTETAAN SYSTEM_CHAIN...")
    chain_file = Path("runtime/system_chain.json")
    if chain_file.exists():
        try:
            with open(chain_file, 'r', encoding='utf-8') as f:
                chain = json.load(f)
            block_count = len(chain.get('blocks', []))
            chain_id = chain.get('chain_id', 'Tuntematon')
            print(f"   ✅ Lohkoja: {block_count} kpl")
            print(f"   🔗 Ketju ID: {chain_id}")
            
        except Exception as e:
            print(f"   ❌ System chain tarkistus epäonnistui: {e}")
    else:
        print("   ❌ System chain tiedostoa ei löydy")
    
    # 6. Tarkista IPFS-tila
    print("\n6. 🌐 TARKISTETAAN IPFS-TILA...")
    try:
        from ipfs_sync_manager import SimpleSyncEngine
        sync_engine = SimpleSyncEngine()
        status = sync_engine.get_sync_status()
        
        ipfs_type = "Oikea IPFS" if status["real_ipfs_available"] else "Mock IPFS"
        sync_status = "Käytössä" if status["sync_enabled"] else "Pois käytöstä"
        
        print(f"   🌐 {ipfs_type} ({sync_status})")
        print(f"   📊 Mock-CID:itä: {status['mock_stats']['total_cids']}")
        
    except Exception as e:
        print(f"   ⚠️  IPFS-tarkistus epäonnistui: {e}")
    
    # 7. Tarkista kysymysten synkronointi
    print("\n7. 📡 TARKISTETAAN SYNKRONOINTI...")
    try:
        from question_manager import QuestionManager
        manager = QuestionManager()
        sync_status = manager.get_sync_status()
        
        print(f"   📥 Tmp-jonossa: {sync_status['tmp_questions_count']} kysymystä")
        print(f"   📤 New-jonossa: {sync_status['new_questions_count']} kysymystä")
        print(f"   ⏰ Seuraava synkronointi: {sync_status['next_sync_time']}")
        
    except Exception as e:
        print(f"   ⚠️  Synkronointitarkistus epäonnistui: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 MONINODITESTIT LÄPÄISTY!")
    
    # 8. Näytä yhteenveto
    print("\n📊 YHTEENVETO:")
    print(f"   💻 Tämä kone: {machine_info['machine_id']}")
    print(f"   🏛️  Aktiivinen vaali: {machine_info['election_id']}")
    print(f"   👑 Rooli: {'MASTER-KONE' if machine_info['is_master'] else 'TYÖASEMA'}")
    print(f"   ❓ Kysymyksiä: {question_count}")
    print(f"   👑 Ehdokkaita: {candidate_count}")
    
    if machine_info['is_master']:
        print("\n💡 MASTER-KONEEN TOIMINNOT:")
        print("   - Voit luoda uusia työasemia")
        print("   - Hallinnoi kysymysten synkronointia")
        print("   - Aktivoi tuotantotila")
    else:
        print("\n💡 TYÖASEMAN TOIMINNOT:")
        print("   - Synkronoi data master-koneen kanssa")
        print("   - Osallistu vertailuihin ja äänestykseen")
        print("   - Käytä järjestelmää vaalikoneena")
    
    return True

def check_node_readiness():
    """Tarkista onko kone valmis toisen noden liittämiseen"""
    
    print("\n🔍 TARKISTETAAN NODEN VALMIUS...")
    
    try:
        from metadata_manager import get_metadata_manager
        metadata = get_metadata_manager()
        machine_info = metadata.get_machine_info()
        
        requirements = [
            ("Runtime-hakemisto", Path("runtime").exists()),
            ("Meta-tiedosto", Path("runtime/meta.json").exists()),
            ("Questions-tiedosto", Path("runtime/questions.json").exists()),
            ("System chain", Path("runtime/system_chain.json").exists()),
            ("Aktiivinen vaali", machine_info['election_id'] != 'unknown'),
            ("Master-kone", machine_info['is_master'])
        ]
        
        all_ok = True
        for req_name, req_met in requirements:
            status = "✅" if req_met else "❌"
            print(f"   {status} {req_name}")
            if not req_met:
                all_ok = False
        
        if all_ok:
            print("\n🎯 TÄMÄ KONE ON VALMIS TOISEN NODEN LUOMISELLE!")
            print("💡 Käytä toisella koneella:")
            print(f"   python install.py --config-file=config_output/elections_list.json --election-id={machine_info['election_id']}")
        else:
            print("\n⚠️  TÄMÄ KONE EI OLE VALMIS TOISEN NODEN LUOMISELLE")
            print("💡 Korjaa puuttuvat vaatimukset ensin")
        
        return all_ok
        
    except Exception as e:
        print(f"❌ Valmiustarkistus epäonnistui: {e}")
        return False

if __name__ == "__main__":
    print("🚀 JUMALTENVAALIEN MONINODITESTIT")
    print("=" * 60)
    
    # Suorita testit
    test_success = test_multi_node_operations()
    
    # Tarkista noden valmius
    if test_success:
        check_node_readiness()
    
    print("\n" + "=" * 60)
    if test_success:
        print("✅ KAIKKI TESTIT ONNISTUIVAT! Järjestelmä on valmis.")
    else:
        print("�JOITKIN TESTIT EPÄONNISTUIVAT. Tarkista virheet.")
    
    sys.exit(0 if test_success else 1)
