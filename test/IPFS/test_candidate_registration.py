# test_candidate_registration.py
from mock_ipfs import MockIPFS
from election_data_manager import ElectionDataManager
from candidate_registration import CandidateRegistration
from candidate_answers import CandidateAnswerManager

def test_complete_candidate_flow():
    """Testaa koko ehdokasprosessin alusta loppuun"""
    print("🧪 TESTATAAN EHDOKKAAN REKISTERÖINTI & VASTAUSPROSESSIA")
    
    # Alusta järjestelmä
    ipfs = MockIPFS()
    election_manager = ElectionDataManager(ipfs)
    
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
    election_manager.initialize_election(meta_data)
    
    # Alusta rekisteröinti & vastausmanagerit
    registration = CandidateRegistration(ipfs, election_manager)
    answer_manager = CandidateAnswerManager(ipfs, election_manager)
    
    # 1. Ehdokas luo avainparin
    print("\n🔑 LUODAAN AVAINPARI...")
    keys = registration.generate_key_pair()
    print(f"✅ Avain pari luotu")
    print(f"   Fingerprint: {keys['key_fingerprint']}")
    
    # 2. Ehdokas rekisteröityy
    print("\n📝 REKISTERÖIDÄÄN EHDOKAS...")
    candidate_data = {
        "name": "Matti Meikäläinen",
        "party": "Test Puolue", 
        "district": "Helsinki",
        "contact_email": "matti@example.com",
        "website": "https://matti.example.com"
    }
    
    candidate_cid = registration.register_candidate(candidate_data, keys["private_key"])
    
    # 3. Ehdokas lähettää vastauksia
    print("\n📝 LÄHETETÄÄN VASTAUKSET...")
    answers = [
        {
            "question_id": 1,
            "answer": 4,
            "confidence": 0.8,
            "comment": {
                "fi": "Täysin samaa mieltä, mutta toteutus pitää olla kustannustehokas",
                "en": "Strongly agree, but implementation must be cost-effective"
            }
        },
        {
            "question_id": 2,
            "answer": -2, 
            "confidence": 0.6,
            "comment": {
                "fi": "Jokseenkin eri mieltä",
                "en": "Somewhat disagree"
            }
        }
    ]
    
    # Hae ehdokas ID
    candidates = election_manager.get_election_data("candidates.json")
    candidate_id = candidates["candidates"][0]["id"]
    
    answer_cid = answer_manager.submit_answers(candidate_id, answers, keys["private_key"])
    
    # 4. Tarkista lopputulos
    print("\n📊 TARKISTETAAN LOPPUTILA...")
    status = election_manager.get_election_status()
    print(f"Ehdokkaita: {status['files']['candidates.json']['candidates_count']}")
    
    # Hae ehdokkaan tiedot
    candidate = election_manager.get_candidate(candidate_id)
    print(f"Ehdokas: {candidate['name']}")
    print(f"Rekisteröity: {candidate['registration_date']}")
    print(f"Vastaukset: {'✅' if 'answer_cid' in candidate else '❌'}")
    
    # Hae vastaukset
    retrieved_answers = answer_manager.get_candidate_answers(candidate_id)
    if retrieved_answers:
        print(f"Vastauksia haettu: {len(retrieved_answers['answers'])} kpl")
    
    print("\n🎉 EHDOKASPROSESSI TESTATTU ONNISTUNEESTI!")

if __name__ == "__main__":
    test_complete_candidate_flow()
