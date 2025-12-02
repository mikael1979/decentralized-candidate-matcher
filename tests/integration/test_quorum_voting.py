# tests/integration/test_quorum_voting.py
#!/usr/bin/env python3
"""
Testaa hajautettua kvoorumivahvistusjärjestelmää
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import os
import json

sys.path.insert(0, os.path.abspath('.'))

try:
    from src.managers.quorum_manager import QuorumManager
    from src.managers.media_registry import MediaRegistry
except ImportError as e:
    print(f"Import-virhe: {e}")
    sys.exit(1)

def test_quorum_voting():
    """Testaa kvoorumivahvistusjärjestelmää"""
    print("🧪 Testataan hajautettua kvoorumivahvistusta...")
    
    try:
        quorum_manager = QuorumManager("Jumaltenvaalit2026")
        media_registry = MediaRegistry("Jumaltenvaalit2026")
        
        # 1. Luo testipuolue
        test_party = {
            "party_id": "party_quorum_test",
            "name": {"fi": "Kvoorumi-testipuolue", "en": "Quorum Test Party", "sv": "Kvorum Testparti"},
            "crypto_identity": {
                "key_fingerprint": "test123456789abcd"
            }
        }
        
        # 2. Alusta vahvistusprosessi
        verification = quorum_manager.initialize_party_verification(test_party)
        
        print("✅ Vahvistusprosessi aloitettu!")
        print(f"   Puolue: {verification['party_name']}")
        print(f"   Vaihe: {verification['current_phase']}")
        print(f"   Aikaraja: {verification['verification_timeout'][11:16]}")
        
        # 3. Lisää mediavahvistuksia
        media_pub = media_registry.register_media_publication(
            party_id=test_party["party_id"],
            party_name=test_party["name"]["fi"],
            public_key_fingerprint=test_party["crypto_identity"]["key_fingerprint"],
            media_url="https://vaalit.fi/julkaisut/kvoorumi-testi",
            publication_data={"title": "Testijulkaisu"}
        )
        
        quorum_manager.add_media_verification(verification, media_pub, "node_zeus")
        quorum_manager.add_media_verification(verification, media_pub, "node_athena")
        
        print(f"   Mediavahvistuksia: {len(verification['media_verifications'])}/2")
        
        # 4. Simuloi äänestys
        test_votes = [
            {"node": "node_zeus", "vote": "approve", "justification": "Hyvä mediavahvistus"},
            {"node": "node_athena", "vote": "approve", "justification": "Vahva PKI-toteutus"},
            {"node": "node_poseidon", "vote": "approve", "justification": "Kaikki kriteerit täytetty"},
            {"node": "node_ares", "vote": "reject", "justification": "Liian vähän tietoja"},
            {"node": "node_aphrodite", "vote": "abstain", "justification": "Tarvitsen lisätietoja"}
        ]
        
        print("\n🗳️  Simuloidaan äänestystä...")
        for test_vote in test_votes:
            # Käytä testijulkaista avainta
            quorum_manager.cast_vote(
                verification_process=verification,
                node_id=test_vote["node"],
                vote=test_vote["vote"],
                node_public_key=f"public_key_{test_vote['node']}",
                justification=test_vote["justification"]
            )
            print(f"   {test_vote['node']}: {test_vote['vote']} - {test_vote['justification']}")
        
        # 5. Tarkista tila
        status = quorum_manager.get_verification_status(verification)
        
        print(f"\n📊 VAHVISTUSTILA:")
        print(f"   Vaihe: {status['current_phase']}")
        print(f"   Ääniä: {status['total_votes']} (hyväksy: {status['approve_votes']}, hylkää: {status['reject_votes']})")
        print(f"   Mediavahvistuksia: {status['media_verifications']}")
        print(f"   Aikaa jäljellä: {status['time_remaining_hours']:.1f}h")
        print(f"   Päätös: {status['final_decision'] or 'KESKEN'}")
        print(f"   Kvoorumi saavutettu: {'✅ KYLLÄ' if status['quorum_met'] else '❌ EI'}")
        
        # 6. Tallenna testitulokset
        quorum_file = "test_quorum_voting.json"
        with open(quorum_file, 'w') as f:
            json.dump({
                "verification_process": verification,
                "status": status,
                "test_votes": test_votes
            }, f, indent=2)
        
        print(f"📁 Kvoorumitestit tallennettu: {quorum_file}")
        
        return status['quorum_met']
        
    except Exception as e:
        print(f"❌ Kvoorumitesti epäonnistui: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_quorum_voting()
    sys.exit(0 if success else 1)
