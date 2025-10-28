# example_usage.py
def example_candidate_workflow():
    """Esimerkki ehdokkaan lisäyksestä ja vastausten antamisesta"""
    manager = UnifiedSyncManager()
    
    # 1. Lisää uusi ehdokas
    candidate_data = {
        "basic_info": {
            "name": {
                "fi": "Matti Meikäläinen",
                "en": "Matti Meikalainen", 
                "sv": "Matti Meikalainen"
            },
            "party": "green_party",
            "district": "helsinki",
            "photo_url": "https://example.com/matti.jpg",
            "contact_info": {
                "email": "matti@example.com",
                "website": "https://matti.example.com"
            }
        },
        "answers": []  # Aluksi tyhjä
    }
    
    # 2. Määrittele vastaukset
    candidate_answers = [
        {
            "question_id": 1,
            "answer_value": 4,
            "explanation": {
                "fi": "Polkupyöräily on tärkeä osa kestävää liikennettä",
                "en": "Cycling is an important part of sustainable transport",
                "sv": "Cykling är en viktig del av hållbar transport"
            },
            "confidence": 4
        },
        {
            "question_id": 2, 
            "answer_value": -2,
            "explanation": {
                "fi": "Jätän varauksella, koska asia on monimutkainen",
                "en": "I'm cautious because the issue is complex",
                "sv": "Jag är försiktig eftersom frågan är komplex"
            },
            "confidence": 3
        }
    ]
    
    # 3. Lisää ehdokas vastauksineen
    candidate_id = manager.add_candidate_with_answers(candidate_data, candidate_answers)
    
    print(f"Ehdokas {candidate_id} lisätty onnistuneesti")
    
    # 4. Suorita synkronointi
    manager.full_sync_cycle()
    
    return candidate_id

# Suorita esimerkki
if __name__ == "__main__":
    example_candidate_workflow()
