# cli_question_interface.py
from question_submission import QuestionSubmission, QuestionSearch

def show_available_tags(question_submission):
    """Näyttää saatavilla olevat tagit"""
    tags = question_submission.get_available_tags()
    print(f"\n📋 KÄYTÖSSÄ OLEVAT TAGIT ({len(tags)} kpl):")
    if tags:
        # Näytä tagit siististi ryhmiteltynä
        for i in range(0, len(tags), 5):
            print("   " + ", ".join(tags[i:i+5]))
    else:
        print("   Ei vielä tageja")

def search_existing_questions(question_search):
    """Mahdollistaa olemassa olevien kysymysten haun sumealla haulla"""
    print("\n🔍 HAE OLEMASSA OLEVIA KYSYMYKSIÄ")
    
    search_type = input("Hakutapa (1=tarkka, 2=sumea, 3=molemmat): ").strip()
    query = input("Hakusana: ").strip()
    tags_input = input("Tagit (pilkulla eroteltuna, tai enter): ").strip()
    
    tags = [tag.strip() for tag in tags_input.split(',')] if tags_input else None
    
    results = []
    
    if search_type == "1" or search_type == "3":
        # Tarkka haku
        results.extend(question_search.search_questions(
            query=query if query else None,
            tags=tags if tags else None,
            similarity_threshold=0.8  # Korkea kynnys tarkalle haulle
        ))
    
    if search_type == "2" or search_type == "3":
        # Sumea haku
        fuzzy_results = question_search.fuzzy_search(query) if query else []
        results.extend(fuzzy_results)
    
    # Poista duplikaatit (sama kysymys voi tulla useasta hausta)
    seen_ids = set()
    unique_results = []
    for result in results:
        q_id = result['question'].get('id')
        if q_id not in seen_ids:
            seen_ids.add(q_id)
            unique_results.append(result)
    
    print(f"\n📊 HAKUTULOKSET ({len(unique_results)} kpl):")
    for i, result in enumerate(unique_results[:10], 1):  # Näytä vain 10 parasta
        question = result['question']
        score = result.get('relevance_score', result.get('similarity_score', 0))
        
        print(f"{i}. {question['question']['fi']}")
        print(f"   ID: {question.get('id', 'N/A')}")
        print(f"   Pistemäärä: {score:.2f}")
        print(f"   Tagit: {', '.join(question['tags']['fi'])}")
        print(f"   Kategoria: {question['category']['fi']}")
        if 'matched_by' in result:
            print(f"   Löytyi: {', '.join(result['matched_by'])}")
        print()

def submit_new_question_flow(ipfs, election_manager):
    """Kysymyksen lähetysprosessi UUID-tuella"""
    question_submission = QuestionSubmission(ipfs, election_manager)
    question_search = QuestionSearch(election_manager)
    
    print("\n📝 UUDEN KYSYMYKSEN LÄHETYS")
    print("=" * 50)
    
    # 1. Näytä saatavilla olevat tagit
    show_available_tags(question_submission)
    
    # 2. Mahdollisuus hakea olemassa olevia kysymyksiä
    search_first = input("\nHaluatko hakea ensin olemassa olevia kysymyksiä? (k/e): ").lower().strip()
    if search_first == 'k':
        search_existing_questions(question_search)
    
    # 3. Kysy kysymyksen tiedot
    print("\n📋 TÄYTÄ UUDEN KYSYMYKSEN TIEDOT")
    
    question_fi = input("Kysymys (suomeksi): ").strip()
    if not question_fi:
        print("❌ Kysymyksen teksti on pakollinen!")
        return
    
    question_en = input("Kysymys (englanniksi): ").strip()
    
    # Kategorian valinta
    categories = ["Ympäristö", "Liikenne", "Koulutus", "Terveys", "Turvallisuus", "Kulttuuri", "Muu"]
    print("\n💡 KATEGORIAT:")
    for i, cat in enumerate(categories, 1):
        print(f"  {i}. {cat}")
    
    try:
        cat_choice = int(input("Valitse kategoria (numero): ")) - 1
        category_fi = categories[cat_choice] if 0 <= cat_choice < len(categories) else "Muu"
        category_en = category_fi  # Yksinkertaistus
    except:
        category_fi = category_en = "Muu"
    
    # Tagien valinta
    print("\n🏷️  TAGIT (vähintään yksi vaaditaan)")
    available_tags = question_submission.get_available_tags()
    if available_tags:
        print("Olemassa olevat tagit:")
        for i in range(0, len(available_tags), 5):
            print("   " + ", ".join(available_tags[i:i+5]))
        print()
    
    tags_input = input("Anna tagit (pilkulla eroteltuna): ").strip()
    tags_fi = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
    
    if not tags_fi:
        print("❌ Vähintään yksi tagi vaaditaan!")
        return
    
    # Asteikon valinta
    print("\n📊 ASTEIKKO (pakollinen)")
    print("Valitse asteikko:")
    print("1. -5 (Täysin eri mieltä) - 5 (Täysin samaa mieltä)")
    print("2. -3 - 3 (yksinkertainen)")
    print("3. 1-5 (myönteinen)")
    
    scale_choice = input("Valinta (1/2/3): ").strip()
    if scale_choice == "2":
        scale = {"min": -3, "max": 3}
    elif scale_choice == "3":
        scale = {"min": 1, "max": 5}
    else:  # Oletus
        scale = {"min": -5, "max": 5}
    
    # Lisää asteikon selitteet
    scale["labels"] = {
        "fi": {
            str(scale["min"]): "Täysin eri mieltä",
            "0": "Neutraali" if scale["min"] < 0 < scale["max"] else "Erittäin huono",
            str(scale["max"]): "Täysin samaa mieltä"
        }
    }
    
    # Luo kysymysdata
    question_data = {
        "category": {
            "fi": category_fi,
            "en": category_en
        },
        "question": {
            "fi": question_fi,
            "en": question_en or question_fi  # Fallback suomeksi
        },
        "scale": scale,  # PAKOLLINEN ASTEIKKO
        "tags": {
            "fi": tags_fi,
            "en": [tag.lower() for tag in tags_fi]  # Yksinkertainen käännös
        }
    }
    
    # 4. Lähetä kysymys
    result = question_submission.submit_question(question_data)
    
    if result['success']:
        print(f"\n✅ KYSYMYS LÄHETETTY ONNISTUNEESTI!")
        print(f"📝 Kysymys ID: {result['question_id']}")  # UUID
        print(f"🔗 CID: {result['cid']}")
        print("\nKysymys siirtyy nyt yhteisön moderaatioon.")
        
    else:
        if result.get('requires_force'):
            # Näytä vastaavat kysymykset
            print(f"\n⚠️  LÖYTYI {len(result['similar_questions'])} VASTAAVAA KYSYMYSTÄ:")
            print("Tarkista, onko kysymyksesi jo olemassa:\n")
            
            for i, similar in enumerate(result['similar_questions'][:5], 1):  # Max 5
                question = similar['question']
                similarity = similar['similarity_score']
                
                print(f"{i}. {question['question']['fi']}")
                print(f"   Samankaltaisuus: {similarity:.1%}")
                print(f"   Tagit: {', '.join(question['tags']['fi'])}")
                print(f"   Kategoria: {question['category']['fi']}")
                print(f"   ID: {question.get('id', 'N/A')}")
                print()
            
            # Kysy haluaako lähettää silti
            force_send = input("Haluatko lähettää kysymyksen silti? (k/e): ").lower().strip()
            if force_send == 'k':
                force_result = question_submission.submit_question(question_data, force=True)
                if force_result['success']:
                    print(f"\n✅ KYSYMYS LÄHETETTY (VAHVISTUS)!")
                    print(f"📝 Kysymys ID: {force_result['question_id']}")  # UUID
                else:
                    print(f"\n❌ LÄHETYS EPÄONNISTUI: {force_result['errors']}")
            else:
                print("\n❌ Kysymystä ei lähetetty.")
                
        else:
            print(f"\n❌ LÄHETYS EPÄONNISTUI:")
            for error in result['errors']:
                print(f"  - {error}")

def question_management_main(ipfs, election_manager):
    """Päävalikko kysymysten hallinnalle"""
    question_submission = QuestionSubmission(ipfs, election_manager)
    question_search = QuestionSearch(election_manager)
    
    while True:
        print("\n📝 KYSYMYSTEN HALLINTA")
        print("1. Lähetä uusi kysymys")
        print("2. Hae olemassa olevia kysymyksiä")
        print("3. Näytä saatavilla olevat tagit")
        print("4. Palaa päävalikkoon")
        
        choice = input("Valinta: ").strip()
        
        if choice == "1":
            submit_new_question_flow(ipfs, election_manager)
        elif choice == "2":
            search_existing_questions(question_search)
        elif choice == "3":
            show_available_tags(question_submission)
        elif choice == "4":
            break
        else:
            print("Virheellinen valinta")
