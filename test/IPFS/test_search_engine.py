# test_search_engine.py
from mock_ipfs import MockIPFS
from election_data_manager import ElectionDataManager
from candidate_registration import CandidateRegistration
from candidate_answers import CandidateAnswerManager
from search_engine import SearchEngine

def test_search_engine():
    """Testaa hakualgoritmia koko datan kanssa"""
    print("🧪 TESTATAAN HAKUALGORITMIA")
    
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
    search_engine = SearchEngine(ipfs, election_manager)
    
    # 1. Lisää kysymyksiä
    print("\n📝 LISÄTÄÄN KYSYMYKSIÄ...")
    
    questions = [
        {
            "id": 1,
            "category": {"fi": "Ympäristö", "en": "Environment"},
            "question": {
                "fi": "Pitäisikö kaupungin vähentää hiilidioksidipäästöjä 50% vuoteen 2030 mennessä?",
                "en": "Should the city reduce carbon dioxide emissions by 50% by 2030?"
            },
            "scale": {"min": -5, "max": 5}
        },
        {
            "id": 2, 
            "category": {"fi": "Liikenne", "en": "Transportation"},
            "question": {
                "fi": "Pitäisikö julkisen liikenteen olla ilmaista opiskelijoille?",
                "en": "Should public transport be free for students?"
            },
            "scale": {"min": -5, "max": 5}
        },
        {
            "id": 3,
            "category": {"fi": "Koulutus", "en": "Education"}, 
            "question": {
                "fi": "Pitäisikö kaupungin tarjota ilmaista ohjelmointikoulutusta nuorille?",
                "en": "Should the city offer free programming education for youth?"
            },
            "scale": {"min": -5, "max": 5}
        }
    ]
    
    for question in questions:
        election_manager.add_question(question, is_official=True)
    
    # 2. Rekisteröi ehdokkaita ja anna vastauksia
    print("\n👤 REKISTERÖIDÄÄN EHDOKKAITA JA ANNETAAN VASTAUKSIA...")
    
    # Ehdokas 1: Matti Meikäläinen
    keys1 = registration.generate_key_pair()
    candidate1_data = {
        "name": "Matti Meikäläinen",
        "party": "Vihreä Puolue", 
        "district": "Helsinki"
    }
    registration.register_candidate(candidate1_data, keys1["private_key"])
    
    # Ehdokas 2: Liisa Esimerkki
    keys2 = registration.generate_key_pair() 
    candidate2_data = {
        "name": "Liisa Esimerkki",
        "party": "Teknologia Puolue",
        "district": "Espoo"
    }
    registration.register_candidate(candidate2_data, keys2["private_key"])
    
    # Ehdokas 3: Testi Tyyppi
    keys3 = registration.generate_key_pair()
    candidate3_data = {
        "name": "Testi Tyyppi", 
        "party": "Perinteinen Puolue",
        "district": "Vantaa"
    }
    registration.register_candidate(candidate3_data, keys3["private_key"])
    
    # Hae ehdokas ID:t
    candidates = election_manager.get_election_data("candidates.json")
    candidate_ids = [c["id"] for c in candidates["candidates"]]
    
    # 3. Anna vastauksia ehdokkaille
    print("\n📝 ANNETAAN EHDOKKAIDEN VASTAUKSET...")
    
    # Matti (vihreä) - ympäristömyönteinen
    matti_answers = [
        {"question_id": 1, "answer": 5, "confidence": 0.9, "comment": {"fi": "Erittäin tärkeää"}},
        {"question_id": 2, "answer": 4, "confidence": 0.8, "comment": {"fi": "Kannatan"}},
        {"question_id": 3, "answer": 3, "confidence": 0.6, "comment": {"fi": "Hyvä idea"}}
    ]
    answer_manager.submit_answers(candidate_ids[0], matti_answers, keys1["private_key"])
    
    # Liisa (teknologia) - koulutusmyönteinen  
    liisa_answers = [
        {"question_id": 1, "answer": 3, "confidence": 0.7, "comment": {"fi": "Tärkeä aihe"}},
        {"question_id": 2, "answer": 2, "confidence": 0.5, "comment": {"fi": "Osittain samaa mieltä"}},
        {"question_id": 3, "answer": 5, "confidence": 0.9, "comment": {"fi": "Ehdottomasti tärkeää"}}
    ]
    answer_manager.submit_answers(candidate_ids[1], liisa_answers, keys2["private_key"])
    
    # Testi (perinteinen) - maltillinen
    testi_answers = [
        {"question_id": 1, "answer": 2, "confidence": 0.6, "comment": {"fi": "Kohtuullista"}},
        {"question_id": 2, "answer": -1, "confidence": 0.7, "comment": {"fi": "En täysin kannata"}},
        {"question_id": 3, "answer": 1, "confidence": 0.5, "comment": {"fi": "Rajoitetusti"}}
    ]
    answer_manager.submit_answers(candidate_ids[2], testi_answers, keys3["private_key"])
    
    # 4. Testaa hakua erilaisilla käyttäjän vastauksilla
    print("\n🔍 TESTATAAN HAKUA ERILAISILLA VASTAUKSILLA...")
    
    # Testi 1: Ympäristömyönteinen käyttäjä
    print("\n--- TESTI 1: YMPÄRISTÖMYÖNTEINEN KÄYTTÄJÄ ---")
    user_answers_1 = {
        "1": 5,  # Ympäristökysymys
        "2": 4,  # Liikenne
        "3": 3   # Koulutus
    }
    
    matches_1 = search_engine.find_matching_candidates(user_answers_1)
    search_engine.print_match_results(matches_1)
    
    # Testi 2: Koulutusmyönteinen käyttäjä
    print("\n--- TESTI 2: KOULUTUSMYÖNTEINEN KÄYTTÄJÄ ---")
    user_answers_2 = {
        "1": 3,  # Ympäristökysymys
        "2": 2,  # Liikenne  
        "3": 5   # Koulutus
    }
    
    matches_2 = search_engine.find_matching_candidates(user_answers_2)
    search_engine.print_match_results(matches_2)
    
    # Testi 3: Maltillinen käyttäjä
    print("\n--- TESTI 3: MALTILLINEN KÄYTTÄJÄ ---")
    user_answers_3 = {
        "1": 2,  # Ympäristökysymys
        "2": 0,  # Liikenne
        "3": 1   # Koulutus
    }
    
    matches_3 = search_engine.find_matching_candidates(user_answers_3)
    search_engine.print_match_results(matches_3)
    
    # 5. Näytä yksityiskohtaiset tulokset
    print("\n📊 YKSITYISKOHTAISET TULOKSET (TESTI 1):")
    best_match = matches_1[0] if matches_1 else None
    if best_match:
        candidate = best_match["candidate"]
        print(f"Paras ehdokas: {candidate['name']} ({best_match['match_percentage']:.1f}%)")
        print("\nYksityiskohtaiset vertailut:")
        
        for detail in best_match["match_details"]:
            q_id = detail["question_id"]
            q_text = search_engine.get_question_text(q_id)
            user_ans = detail["user_answer"]
            cand_ans = detail["candidate_answer"]
            similarity = detail["similarity"]
            
            print(f"  {q_text[:60]}...")
            print(f"    Sinä: {user_ans}/5, Ehdokas: {cand_ans}/5")
            print(f"    Yhteensopivuus: {similarity}/10 pistettä")
            print()
    
    print("🎉 HAKUALGORITMIN TESTI ONNISTUI!")

if __name__ == "__main__":
    test_search_engine()
