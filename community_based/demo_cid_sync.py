# demo_cid_sync.py
def demonstrate_cid_sync_workflow():
    """Demonstroi CID-pohjaista synkronointityökulkua"""
    
    # Alusta synkronointimanageri
    sync_manager = CIDSyncManager()
    bidir_sync = CompleteBidirectionalSync(sync_manager)
    
    print(f"Paikallinen järjestelmä ID: {sync_manager.local_system_id}")
    
    # 1. Lisää uusi paikallinen kysymys (ilman CID:ä)
    question_data = {
        "local_id": sync_manager._generate_local_id(),
        "ipfs_cid": None,
        "source": "local",
        "global_version": 1,
        "timestamps": {
            "created_local": sync_manager._get_current_timestamp(),
            "modified_local": sync_manager._get_current_timestamp(),
            "synced_to_ipfs": None,
            "imported_from_ipfs": None
        },
        "content": {
            "category": {"fi": "Testi", "en": "Test", "sv": "Test"},
            "question": {"fi": "Uusi paikallinen kysymys?", "en": "New local question?", "sv": "Ny lokal fråga?"},
            "tags": ["test", "local"],
            "scale": {"min": -5, "max": 5}
        },
        "elo_rating": {
            "base_rating": 1000,
            "comparison_delta": 0,
            "vote_delta": 0,
            "current_rating": 1000
        }
    }
    
    # Lisää questions.json:iin
    questions_data = sync_manager._load_json('questions.json')
    questions_data.setdefault('questions', []).append(question_data)
    questions_data['metadata']['last_updated'] = sync_manager._get_current_timestamp()
    questions_data['metadata']['sync_status']['local_modified'] = True
    sync_manager._save_json('questions.json', questions_data)
    
    print(f"Lisätty uusi paikallinen kysymys: {question_data['local_id']}")
    print(f"Kysymyksen CID aluksi: {question_data['ipfs_cid']}")
    
    # 2. Suorita kaksisuuntainen synkronointi
    sync_results = bidir_sync.full_sync_cycle()
    
    # 3. Tarkista että kysymys sai CID:n
    updated_questions = sync_manager._load_json('questions.json')
    updated_question = next(
        (q for q in updated_questions['questions'] 
         if q['local_id'] == question_data['local_id']), 
        None
    )
    
    if updated_question and updated_question['ipfs_cid']:
        print(f"Kysymys sai CID:n: {updated_question['ipfs_cid']}")
        print(f"Lähde: {updated_question['source']}")
    else:
        print("Kysymys ei saanut CID:ä")
    
    # 4. Simuloi toisen laitteen synkronointia
    print("\n--- Simuloidaan toisen laitteen IPFS-synkronointia ---")
    
    # Toinen laite lataa samat kysymykset IPFS:stä
    ipfs_results = sync_manager.sync_ipfs_to_questions()
    
    print(f"Toinen laite tuonut {ipfs_results} uutta kysymystä IPFS:stä")

if __name__ == "__main__":
    demonstrate_cid_sync_workflow()
