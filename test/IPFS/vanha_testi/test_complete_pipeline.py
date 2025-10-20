def test_complete_pipeline():
    """Testaa koko vaalikoneen putkea alusta loppuun"""
    ipfs = MockIPFS()
    manager = ElectionDataManager(ipfs)
    
    # 1. Alusta vaali (kuten aiemmin)
    
    # 2. Lisää ehdokkaiden vastaukset
    answer_manager = CandidateAnswerManager(ipfs, manager)
    
    # Matti Meikäläisen vastaukset
    matti_answers = [
        {"question_id": 1, "answer": 4, "confidence": 0.8},
        {"question_id": 2, "answer": 3, "confidence": 0.6},
        {"question_id": "user_1760317660476", "answer": 2, "confidence": 0.5}
    ]
    answer_manager.submit_answers(1, matti_answers)
    
    # Liisa Esimerkin vastaukset  
    liisa_answers = [
        {"question_id": 1, "answer": 5, "confidence": 0.9},
        {"question_id": 2, "answer": -2, "confidence": 0.7},
        {"question_id": "user_1760317660476", "answer": 4, "confidence": 0.8}
    ]
    answer_manager.submit_answers(2, liisa_answers)
    
    # 3. Testaa hakua
    search_engine = SearchEngine(ipfs, manager)
    
    # Käyttäjän vastaukset
    user_answers = {
        "1": 4,      # Ympäristökysymys
        "2": 2,      # Liikenne
        "user_1760317660476": 3  # Kaupunkipyörät
    }
    
    matches = search_engine.find_matching_candidates(user_answers)
    
    print("🔍 HAKUTULOKSET:")
    for match in matches:
        print(f"  {match['candidate']['name']}: {match['match_percentage']:.1f}%")
    
    return matches
