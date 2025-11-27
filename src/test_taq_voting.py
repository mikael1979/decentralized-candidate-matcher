# src/test_taq_voting.py
#!/usr/bin/env python3
"""
Testaa TAQ-äänestysprosessia
"""
import sys
sys.path.insert(0, 'src')

from managers.quorum import QuorumManager

def test_taq_voting():
    print("🧪 TESTATAAN TAQ-ÄÄNESTYSPROSESSIA...")
    
    manager = QuorumManager('test2024')
    
    # Luo puolue YLE:llä (TAQ-bonus)
    party_data = {
        'party_id': 'test_party_taq',
        'name': {'fi': 'TAQ-Testipuolue'},
        'crypto_identity': {'key_fingerprint': 'taq_test123'},
        'media_publications': [
            {'media_domain': 'yle.fi', 'trust_score': 9}
        ]
    }
    
    # Alusta vahvistusprosessi
    verification = manager.initialize_party_verification(party_data)
    print(f"\n🎯 Puolue: {verification['party_id']}")
    print(f"📊 TAQ-bonus: {verification['taq_bonus'].get('taq_enabled')}")
    print(f"👥 Vaaditut vahvistukset: {verification['required_approvals']}/3")
    
    # SIMULOI ÄÄNIÄ
    print("\n🗳️  SIMULOIDAAN ÄÄNESTYSTÄ...")
    
    # 1. Ääni (ei riitä vielä normaalisti, mutta TAQ:lla riittää 2/3)
    success1 = manager.cast_vote(verification, "node_1", "approve", "public_key_1", "Hyvä puolue!")
    print(f"Ääni 1 (node_1): {'✅ Onnistui' if success1 else '❌ Epäonnistui'}")
    
    # 2. Ääni (TAQ-puolue hyväksytään nyt 2 äänellä!)
    success2 = manager.cast_vote(verification, "node_2", "approve", "public_key_2", "Myös hyvä!")
    print(f"Ääni 2 (node_2): {'✅ Onnistui' if success2 else '❌ Epäonnistui'}")
    
    # Tarkista tila
    status = manager.get_verification_status(verification)
    print(f"\n📈 LOPPUTILA:")
    print(f"   Hyväksytyt äänet: {status['approve_votes']}/{status['required_approvals']}")
    print(f"   Päätös: {status['final_decision'] or 'Ei vielä'}")
    print(f"   TAQ-toiminta: {'✅ HYVÄKSYTTY TAQ:LLA' if status['final_decision'] == 'approved' else '❌ Ei hyväksytty'}")
    
    if status['final_decision'] == 'approved':
        print("\n🎉 TAQ-INTEGRAATIO ONNISTUI! Puolue hyväksyttiin 2/3 äänellä!")
    else:
        print("\n❌ Jotain meni pieleen - puoluetta ei hyväksytty")

if __name__ == "__main__":
    test_taq_voting()
