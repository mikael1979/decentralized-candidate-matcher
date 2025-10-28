# test_mock_ipfs.py
def test_mock_ipfs_workflow():
    """Testaa koko Mock-IPFS työkulun"""
    
    print("🚀 KÄYNNISTETÄÄN MOCK-IPFS TESTI")
    print("=" * 60)
    
    # 1. Alusta Mock-synkronointimanageri
    sync_manager = MockSyncManager(runtime_dir="runtime_test")
    
    # 2. Lisää testikysymyksiä
    test_questions = [
        {
            "category": {"fi": "Ympäristö", "en": "Environment", "sv": "Miljö"},
            "question": {"fi": "Pitäisikö kaupungin investoida enemmän pyöräteihin?", "en": "Should the city invest more in bicycle paths?", "sv": "Bör staden investera mer i cykelvägar?"},
            "tags": ["transport", "environment"],
            "scale": {"min": -5, "max": 5}
        },
        {
            "category": {"fi": "Koulutus", "en": "Education", "sv": "Utbildning"},
            "question": {"fi": "Pitäisikö perusopetuksen olla ilmaista kaikille?", "en": "Should basic education be free for everyone?", "sv": "Bör grundutbildning vara gratis för alla?"},
            "tags": ["education", "social"],
            "scale": {"min": -5, "max": 5}
        }
    ]
    
    print("\n📝 LISÄTÄÄN TESTIKYSYMYKSIÄ")
    question_ids = []
    for i, question_content in enumerate(test_questions):
        qid = sync_manager.add_new_question(question_content)
        question_ids.append(qid)
        print(f"  {i+1}. Kysymys lisätty: {qid}")
    
    # 3. Suorita synkronointi
    print("\n🔄 SUORITETAAN SYNKRONOINTI")
    sync_results = sync_manager.full_sync_cycle()
    
    # 4. Simuloi toisen laitteen synkronointia
    print("\n💻 SIMULOIDAAN TOISEN LAITTEEN SYNKRONOINTIA")
    
    # Luo toinen mock-manageri (simuloi toista laitetta)
    other_sync_manager = MockSyncManager(
        runtime_dir="runtime_test_other", 
        local_system_id="other_mock_system"
    )
    
    # Toinen laite synkronoi IPFS:stä
    other_results = other_sync_manager.sync_ipfs_to_local()
    
    # 5. Näytä lopputila
    print("\n📊 LOPPUTILA")
    print("=" * 40)
    
    # Laitteen 1 tilasto
    questions1 = sync_manager._load_json('questions.json')
    print("LAITE 1:")
    print(f"  - Kysymyksiä: {len(questions1.get('questions', []))}")
    print(f"  - Paikallisia: {len([q for q in questions1.get('questions', []) if q.get('source') in ['local', 'local_synced']])}")
    print(f"  - IPFS:stä: {len([q for q in questions1.get('questions', []) if q.get('source') == 'ipfs_imported'])}")
    
    # Laitteen 2 tilasto
    questions2 = other_sync_manager._load_json('questions.json')
    print("LAITE 2:")
    print(f"  - Kysymyksiä: {len(questions2.get('questions', []))}")
    print(f"  - Kaikki IPFS:stä tuotuja")
    
    print(f"\n🎯 MOCK-IPFS TESTI VALMIS!")
    return sync_results

if __name__ == "__main__":
    test_mock_ipfs_workflow()
