# test_candidate_profile.py
from mock_ipfs import MockIPFS
from election_data_manager import ElectionDataManager
from candidate_registration import CandidateRegistration
from candidate_answers import CandidateAnswerManager
from candidate_profile import CandidateProfile

def test_complete_profile_system():
    """Testaa koko ehdokasprofiilijärjestelmän"""
    print("🧪 TESTATAAN EHDOKASPROFIILIJÄRJESTELMÄÄ")
    
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
    
    # Alusta managerit
    registration = CandidateRegistration(ipfs, election_manager)
    answer_manager = CandidateAnswerManager(ipfs, election_manager) 
    profile_manager = CandidateProfile(ipfs, election_manager)
    
    # 1. Luo avainparit
    print("\n🔑 LUODAAN AVAINPARI...")
    keys = registration.generate_key_pair()
    
    # 2. Rekisteröi ehdokas
    print("\n📝 REKISTERÖIDÄÄN EHDOKAS...")
    candidate_data = {
        "name": "Liisa Esimerkki",
        "party": "Demo Puolue",
        "district": "Espoo",
        "contact_email": "liisa@example.com",
        "website": "https://liisa.example.com"
    }
    
    candidate_cid = registration.register_candidate(candidate_data, keys["private_key"])
    
    # 3. Hae ehdokas ID
    candidates = election_manager.get_election_data("candidates.json")
    candidate_id = candidates["candidates"][0]["id"]
    
    # 4. Lähetä vastauksia
    print("\n📝 LÄHETETÄÄN VASTAUKSET...")
    answers = [
        {
            "question_id": 1,
            "answer": 5,
            "confidence": 0.9,
            "comment": {
                "fi": "Täysin samaa mieltä, tämä on erittäin tärkeää",
                "en": "Strongly agree, this is very important"
            }
        },
        {
            "question_id": 2,
            "answer": 3,
            "confidence": 0.7, 
            "comment": {
                "fi": "Samaa mieltä, mutta toteutuskaavaa täytyy hioa",
                "en": "Agree, but implementation needs refinement"
            }
        }
    ]
    
    answer_cid = answer_manager.submit_answers(candidate_id, answers, keys["private_key"])
    
    # 5. Luo ja julkaise verkkosivuprofiili
    print("\n🌐 LUODAAN VERKKOSIVUPROFIILI...")
    profile_cid = profile_manager.publish_profile(candidate_id, keys["private_key"])
    
    # 6. Tarkista lopputulos
    print("\n📊 TARKISTETAAN LOPPUTILA...")
    
    # Hae ehdokas tiedot
    candidate = election_manager.get_candidate(candidate_id)
    
    print(f"✅ Ehdokas: {candidate['name']}")
    print(f"✅ Vastaukset: {'✅' if 'answer_cid' in candidate else '❌'}")
    print(f"✅ Profiili: {'✅' if 'profile_cid' in candidate else '❌'}")
    print(f"✅ HTML-sivu: {'✅' if 'profile_html_cid' in candidate else '❌'}")
    
    if 'profile_cid' in candidate:
        # Hae profiilin data
        profile_data = ipfs.get_json(candidate['profile_cid'])
        print(f"📄 Profiilin koko: {len(str(profile_data))} tavua")
        print(f"🕒 Luotu: {profile_data.get('generated_at', 'N/A')}")
    
    if 'profile_html_cid' in candidate:
        # Hae HTML-sivu
        html_data = ipfs.get_json(candidate['profile_html_cid'])
        print(f"🌐 HTML-sivun koko: {len(html_data.get('html', ''))} tavua")
        
        # Tallenna HTML paikallisesti testaamista varten
        with open(f"candidate_profile_{candidate_id}.html", "w", encoding="utf-8") as f:
            f.write(html_data['html'])
        print(f"💾 HTML tallennettu: candidate_profile_{candidate_id}.html")
    
    print("\n🎉 EHDOKASPROFIILIJÄRJESTELMÄ TESTATTU ONNISTUNEESTI!")

if __name__ == "__main__":
    test_complete_profile_system()
