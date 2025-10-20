# cli_interface.py (päivitetty)
from mock_ipfs import MockIPFS
from election_data_manager import ElectionDataManager
from search_engine import SearchEngine

def show_questions(manager):
    """Näyttää kaikki kysymykset"""
    questions = manager.get_all_questions()
    print(f"\n📝 KYSYMYKSET ({len(questions)} kpl)")
    print("=" * 40)
    
    for i, question in enumerate(questions, 1):
        q_id = question.get('id', 'N/A')
        category = question.get('category', {}).get('fi', 'Ei kategoriaa')
        q_text = question.get('question', {}).get('fi', 'Ei tekstiä')
        
        print(f"{i}. [{category}] {q_text}")
        print(f"   ID: {q_id}")
        print()

def answer_questions(manager):
    """Kysyy käyttäjältä vastauksia kysymyksiin"""
    questions = manager.get_all_questions()
    user_answers = {}
    
    print(f"\n📝 VASTAUSKERTOMA ({len(questions)} kysymystä)")
    print("=" * 40)
    print("Vastaa asteikolla -5 (täysin eri mieltä) - 5 (täysin samaa mieltä)")
    print()
    
    for question in questions:
        q_id = question.get('id')
        q_text = question.get('question', {}).get('fi', 'Ei tekstiä')
        
        print(f"Kysymys: {q_text}")
        
        while True:
            try:
                answer = int(input("Vastaus (-5 - 5): "))
                if -5 <= answer <= 5:
                    user_answers[str(q_id)] = answer
                    break
                else:
                    print("Virhe: Vastauksen tulee olla välillä -5 - 5")
            except ValueError:
                print("Virhe: Syötä numero")
        
        print()
    
    print(f"✅ Vastattu {len(user_answers)} kysymykseen")
    return user_answers

def find_candidates(manager, user_answers):
    """Etsii ehdokkaita käyttäjän vastausten perusteella"""
    ipfs = MockIPFS()  # Tässä yksinkertaistus - oikeassa käytössä jaettu instanssi
    search_engine = SearchEngine(ipfs, manager)
    
    print(f"\n🔍 ETSITÄÄN EHDOKKAITA...")
    matches = search_engine.find_matching_candidates(user_answers)
    
    if matches:
        search_engine.print_match_results(matches)
        
        # Kysy haluaako käyttäjä nähdä yksityiskohdat
        show_details = input("\nHaluatko nähdä yksityiskohtaiset vertailut? (k/e): ")
        if show_details.lower() == 'k':
            best_match = matches[0]
            candidate = best_match["candidate"]
            print(f"\n📊 YKSITYISKOHTAISET TULOKSET: {candidate['name']}")
            print("=" * 50)
            
            for detail in best_match["match_details"]:
                q_id = detail["question_id"]
                q_text = search_engine.get_question_text(q_id)
                user_ans = detail["user_answer"]
                cand_ans = detail["candidate_answer"]
                
                print(f"Kysymys: {q_text}")
                print(f"  Sinun vastauksesi: {user_ans}/5")
                print(f"  Ehdokkaan vastaus: {cand_ans}/5")
                print(f"  Yhteensopivuus: {detail['similarity']}/10 pistettä")
                print()
    else:
        print("❌ Ei vastaavia ehdokkaita löytynyt")

def main():
    """Pääkäyttöliittymä"""
    ipfs = MockIPFS()
    manager = ElectionDataManager(ipfs)
    
    # Alusta testivaali
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
    
    print("🎯 HAJautettu Vaalikone")
    print("======================")
    print("Tervetuloa testaamaan hajautettua vaalikonetta!")
    print("Tämä on demo, jossa on valmiina testidataa.")
    print()
    
    user_answers = None
    
    while True:
        print("\nValitse toiminto:")
        print("1. Näytä kysymykset")
        print("2. Vastaa kysymyksiin") 
        print("3. Etsi ehdokkaita")
        print("4. Lopeta")
        
        choice = input("Valinta: ").strip()
        
        if choice == "1":
            show_questions(manager)
        elif choice == "2":
            user_answers = answer_questions(manager)
        elif choice == "3":
            if user_answers:
                find_candidates(manager, user_answers)
            else:
                print("❌ Vastaa ensin kysymyksiin (valinta 2)")
        elif choice == "4":
            print("Kiitos käytöstä! 👋")
            break
        else:
            print("❌ Virheellinen valinta")

if __name__ == "__main__":
    main()
