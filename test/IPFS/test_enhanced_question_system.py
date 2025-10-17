# test_enhanced_question_system.py
from mock_ipfs import MockIPFS
from election_data_manager import ElectionDataManager
from question_submission import QuestionSubmission, QuestionSearch
import uuid

def test_enhanced_question_system():
    print("🧪 TESTATAAN PARANNETTUA KYSYMYSJÄRJESTELMÄÄ")
    
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
    
    # Lisää testikysymyksiä UUID:illa
    test_questions = [
        {
            "id": str(uuid.uuid4()),  # UUID ID
            "category": {"fi": "Ympäristö", "en": "Environment"},
            "question": {
                "fi": "Pitäisikö kaupungin vähentää hiilidioksidipäästöjä?",
                "en": "Should the city reduce carbon emissions?"
            },
            "tags": {
                "fi": ["ympäristö", "hiilidioksidi", "ilmasto"],
                "en": ["environment", "carbon", "climate"]
            },
            "scale": {"min": -5, "max": 5}
        },
        {
            "id": str(uuid.uuid4()),  # UUID ID
            "category": {"fi": "Liikenne", "en": "Transportation"},
            "question": {
                "fi": "Pitäisikö julkisen liikenteen olla ilmaista?",
                "en": "Should public transport be free?"
            },
            "tags": {
                "fi": ["liikenne", "julkinen liikenne", "maksuttomuus"],
                "en": ["transportation", "public transport", "free"]
            },
            "scale": {"min": -5, "max": 5}
        }
    ]
    
    for question in test_questions:
        manager.add_question(question, is_official=True)
    
    # Testaa kysymyksen lähetystä
    question_submission = QuestionSubmission(ipfs, manager)
    question_search = QuestionSearch(manager)
    
    print("\n1. TESTI: Kysymys ilman asteikkoa (pitäisi epäonnistua)")
    question_data_no_scale = {
        "question": {"fi": "Uusi kysymys", "en": "New question"},
        "tags": {"fi": ["testi"], "en": ["test"]},
        # scale puuttuu tarkoituksella
    }
    
    result = question_submission.submit_question(question_data_no_scale)
    print(f"Tulos: {'✅ Onnistui' if result['success'] else '❌ Epäonnistui'}")
    if result['errors']:
        print(f"Virheet: {result['errors']}")
    
    print("\n2. TESTI: Sumea haku")
    fuzzy_results = question_search.fuzzy_search("hiilidioksidi")
    print(f"Löytyi {len(fuzzy_results)} kysymystä sumealla haulla")
    for result in fuzzy_results:
        print(f"  - {result['question']['question']['fi']} ({result['similarity_score']:.2f})")
    
    print("\n3. TESTI: UUID ID:t")
    question_data_new = {
        "category": {"fi": "Koulutus", "en": "Education"},
        "question": {
            "fi": "Pitäisikö kaupungin tarjota ilmaista koodauskoulutusta?",
            "en": "Should the city offer free coding education?"
        },
        "tags": {
            "fi": ["koulutus", "ohjelmointi", "digitalisaatio"],
            "en": ["education", "programming", "digitalization"]
        },
        "scale": {"min": -5, "max": 5}
    }
    
    result = question_submission.submit_question(question_data_new)
    print(f"Tulos: {'✅ Onnistui' if result['success'] else '❌ Epäonnistui'}")
    if result['success']:
        question_id = result['question_id']
        print(f"Kysymys ID (UUID): {question_id}")
        print(f"UUID kelvollinen: {len(question_id) == 36}")  # UUID pituus
    
    print("\n🎉 PARANNETTU KYSYMYSJÄRJESTELMÄ TESTATTU!")

if __name__ == "__main__":
    test_enhanced_question_system()
