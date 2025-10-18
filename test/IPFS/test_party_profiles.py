# test_party_profiles.py
from mock_ipfs import MockIPFS
from election_data_manager import ElectionDataManager
from candidate_registration import CandidateRegistration
from candidate_answers import CandidateAnswerManager
from party_profile import PartyProfile, PartyComparison

def test_party_profiles():
    print("🧪 TESTATAAN PUOLUEPROFIILIJÄRJESTELMÄÄ")
    
    ipfs = MockIPFS()
    manager = ElectionDataManager(ipfs)
    
    # Alusta vaali
    meta_data = {
        "system": "Decentralized Candidate Matcher", 
        "version": "2.0.0",
        "election": {
            "id": "test_election",
            "country": "FI",
            "type": "municipal",
            "name": {
                "fi": "Testivaali",
                "en": "Test Election"
            },
            "date": "2026-01-12",
            "language": "fi"
        }
    }
    manager.initialize_election(meta_data)
    
    # Lisää testikysymyksiä
    questions = [
        {
            "id": 1,
            "category": {"fi": "Ympäristö", "en": "Environment"},
            "question": {
                "fi": "Pitäisikö kaupungin vähentää hiilidioksidipäästöjä?",
                "en": "Should the city reduce carbon emissions?"
            },
            "scale": {"min": -5, "max": 5}
        },
        {
            "id": 2,
            "category": {"fi": "Liikenne", "en": "Transportation"},
            "question": {
                "fi": "Pitäisikö julkisen liikenteen olla ilmaista?",
                "en": "Should public transport be free?"
            },
            "scale": {"min": -5, "max": 5}
        }
    ]
    
    for question in questions:
        manager.add_question(question, is_official=True)
    
    # Rekisteröi ehdokkaita eri puolueisiin
    registration = CandidateRegistration(ipfs, manager)
    answer_manager = CandidateAnswerManager(ipfs, manager)
    
    # Puolue 1: Vihreä Puolue (yhtenäiset vastaukset)
    for i in range(3):
        keys = registration.generate_key_pair()
        candidate_data = {
            "name": f"Vihreä Ehdokas {i+1}",
            "party": "Vihreä Puolue",
            "district": "Helsinki"
        }
        registration.register_candidate(candidate_data, keys["private_key"])
        
        # Yhtenäiset vihreät vastaukset
        answers = [
            {"question_id": 1, "answer": 5, "confidence": 0.9},
            {"question_id": 2, "answer": 4, "confidence": 0.8}
        ]
        answer_manager.submit_answers(i+1, answers, keys["private_key"])
    
    # Puolue 2: Sekalainen Puolue (erilaiset vastaukset)
    for i in range(3):
        keys = registration.generate_key_pair()
        candidate_data = {
            "name": f"Sekalainen Ehdokas {i+1}",
            "party": "Sekalainen Puolue", 
            "district": "Espoo"
        }
        registration.register_candidate(candidate_data, keys["private_key"])
        
        # Eri vastaukset
        answers = [
            {"question_id": 1, "answer": i-2, "confidence": 0.7},  # -1, 0, 1
            {"question_id": 2, "answer": 3-i, "confidence": 0.6}   # 3, 2, 1
        ]
        answer_manager.submit_answers(i+4, answers, keys["private_key"])
    
    # Testaa puolueprofiilit
    party_profile = PartyProfile(ipfs, manager)
    party_comparison = PartyComparison(ipfs, manager)
    
    print("\n1. PUOLUELISTAUS:")
    parties = party_comparison.get_all_parties()
    for party in parties:
        print(f"  - {party}")
    
    print("\n2. PUOLUEEN KESKIARVOVASTAUKSET:")
    for party in parties:
        party_answers = party_profile.calculate_party_answers(party)
        print(f"\n📊 {party}:")
        for q_id, answer_data in party_answers.get("averaged_answers", {}).items():
            print(f"   Kysymys {q_id}: {answer_data['answer']}/5 (luottamus: {answer_data['confidence']:.0%})")
    
    print("\n3. PUOLUEEN KONSENSUS:")
    for party in parties:
        consensus = party_profile.get_party_consensus(party)
        print(f"\n🎯 {party}:")
        print(f"   Kokonaiskonsensus: {consensus.get('overall_consensus', 0):.1f}%")
    
    print("\n4. PUOLUEVERTAILU:")
    user_answers = {"1": 4, "2": 3}  # Ympäristö- ja liikennemyönteinen
    comparisons = party_comparison.compare_parties(user_answers)
    for comp in comparisons:
        print(f"   {comp['party_name']}: {comp['match_percentage']:.1f}%")
    
    print("\n🎉 PUOLUEPROFIILIJÄRJESTELMÄ TESTATTU!")

if __name__ == "__main__":
    test_party_profiles()
