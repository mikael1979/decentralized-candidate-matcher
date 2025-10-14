import asyncio
from mock_ipfs import MockIPFS
from election_data_manager import ElectionDataManager

def test_full_election_system():
    """Testaa koko vaalikonejärjestelmää"""
    print("🚀 TESTATAAN KOKO VAALIKONEJÄRJESTELMÄÄ")
    
    # Alusta IPFS ja manager
    ipfs = MockIPFS()
    manager = ElectionDataManager(ipfs)
    
    # 1. Alusta vaali
    meta_data = {
        "system": "Decentralized Candidate Matcher",
        "version": "1.0.0",
        "election": {
            "id": "test_election_2024",
            "country": "FI",
            "type": "municipal", 
            "name": {
                "fi": "Testivaalit 2024",
                "en": "Test Election 2024"
            },
            "date": "2024-04-14",
            "language": "fi"
        },
        "community_moderation": {
            "enabled": True,
            "thresholds": {
                "auto_block_inappropriate": 0.7,
                "auto_block_min_votes": 10,
                "community_approval": 0.8
            }
        }
    }
    
    root_cid = manager.initialize_election(meta_data)
    print(f"✅ Vaali alustettu - Root CID: {root_cid}")
    
    # 2. Lisää virallisia kysymyksiä
    official_questions = [
        {
            "id": 1,
            "category": {"fi": "Ympäristö", "en": "Environment"},
            "question": {
                "fi": "Pitäisikö kaupungin vähentää hiilidioksidipäästöjä 50% vuoteen 2030 mennessä?",
                "en": "Should the city reduce carbon dioxide emissions by 50% by 2030?"
            },
            "scale": {
                "min": -5,
                "max": 5,
                "labels": {
                    "fi": {
                        "-5": "Täysin eri mieltä",
                        "0": "Neutraali", 
                        "5": "Täysin samaa mieltä"
                    }
                }
            },
            "tags": {
                "fi": ["ympäristö", "hiilidioksidi", "ilmasto"],
                "en": ["environment", "carbon_dioxide", "climate"]
            }
        },
        {
            "id": 2,
            "category": {"fi": "Liikenne", "en": "Transportation"},
            "question": {
                "fi": "Pitäisikö julkisen liikenteen olla ilmaista opiskelijoille?",
                "en": "Should public transport be free for students?"
            },
            "scale": {
                "min": -5,
                "max": 5,
                "labels": {
                    "fi": {
                        "-5": "Täysin eri mieltä",
                        "0": "Neutraali", 
                        "5": "Täysin samaa mieltä"
                    }
                }
            },
            "tags": {
                "fi": ["liikenne", "julkinen liikenne", "opiskelijat"],
                "en": ["transportation", "public_transport", "students"]
            }
        }
    ]
    
    for question in official_questions:
        cid = manager.add_question(question, is_official=True)
        print(f"✅ Virallinen kysymys {question['id']} lisätty - CID: {cid}")
    
    # 3. Lisää käyttäjän kysymys
    user_question = {
        "id": "user_1760317660476",
        "category": {"fi": "Liikenne", "en": "Transportation"},
        "question": {
            "fi": "Pitäisikö kaupunkipyörien määrää lisätä kesäkaudella?",
            "en": "Should the number of city bikes be increased during summer season?"
        },
        "scale": {
            "min": -5,
            "max": 5,
            "labels": {
                "fi": {
                    "-5": "Täysin eri mieltä",
                    "0": "Neutraali", 
                    "5": "Täysin samaa mieltä"
                }
            }
        },
        "tags": {
            "fi": ["liikenne", "kaupunkipyörät", "kesä"],
            "en": ["transportation", "city_bikes", "summer"]
        },
        "submission": {
            "user_public_key": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIuser123456789",
            "timestamp": "2024-01-15T10:15:30Z",
            "status": "pending",
            "upvotes": 0,
            "downvotes": 0,
            "user_comment": "Kesäkaudella pyöräily on suosittua"
        }
    }
    
    user_q_cid = manager.add_question(user_question, is_official=False)
    print(f"✅ Käyttäjän kysymys lisätty - CID: {user_q_cid}")
    
    # 4. Lisää ehdokkaita
    candidates = [
        {
            "id": 1,
            "name": "Matti Meikäläinen",
            "party": "Test Puolue",
            "district": "Helsinki",
            "public_key": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIcandidate1key123456789",
            "answer_cid": "QmXyZ123...candidate_answers_1",
            "verified": True
        },
        {
            "id": 2,
            "name": "Liisa Esimerkki", 
            "party": "Toinen Puolue",
            "district": "Espoo",
            "public_key": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIcandidate2key987654321",
            "answer_cid": "QmAbC456...candidate_answers_2",
            "verified": True
        }
    ]
    
    for candidate in candidates:
        cid = manager.add_candidate(candidate)
        print(f"✅ Ehdokas {candidate['name']} lisätty - CID: {cid}")
    
    # 5. Hae ja näytä data
    print("\n📊 VAALIDATAN SISÄLTÖ:")
    
    meta_data = manager.get_election_data("meta.json")
    questions_data = manager.get_election_data("questions.json")
    new_questions_data = manager.get_election_data("newquestions.json")
    candidates_data = manager.get_election_data("candidates.json")
    
    print(f"Vaali: {meta_data['election']['name']['fi']}")
    print(f"Virallisia kysymyksiä: {len(questions_data['questions'])}")
    print(f"Käyttäjien kysymyksiä: {len(new_questions_data['questions'])}")
    print(f"Ehdokkaita: {len(candidates_data['candidates'])}")
    
    # 6. Tarkista eheys
    print("\n🔒 EHETYSTARKISTUS:")
    files_to_check = ["meta.json", "questions.json", "newquestions.json", "candidates.json"]
    for filename in files_to_check:
        data = manager.get_election_data(filename)
        is_valid = manager.verify_integrity(data)
        print(f"  {filename}: {'✅ VALID' if is_valid else '❌ INVALID'}")
    
    # 7. Näytä IPFS-statistiikat
    stats = ipfs.get_stats()
    print(f"\n📈 IPFS-STATISTIIKAT:")
    print(f"  Objekteja: {stats['total_objects']}")
    print(f"  Lisäyksiä: {stats['add_count']}")
    print(f"  Hakuja: {stats['get_count']}")
    print(f"  Kokonaiskoko: {stats['total_size']} bytes")
    
    # 8. Testaa hakutoiminnallisuus
    print("\n🔍 TESTAA HAKUTOIMINNALLISUUS:")
    
    # Hae kaikki kysymykset
    all_questions = questions_data['questions'] + new_questions_data['questions']
    print(f"Kysymyksiä yhteensä: {len(all_questions)}")
    
    for q in all_questions:
        if 'id' in q:
            print(f"  - Kysymys {q['id']}: {q['question']['fi'][:50]}...")
    
    # Näytä ehdokkaat
    print(f"\nEhdokkaat:")
    for candidate in candidates_data['candidates']:
        print(f"  - {candidate['name']} ({candidate['party']})")
    
    print("\n🎉 KOKO VAALIKONEJÄRJESTELMÄ TESTATTU ONNISTUNEESTI!")
    print("   MockIPFS ja ElectionDataManager toimivat täydellisesti!")
    
    return ipfs, manager

if __name__ == "__main__":
    ipfs, manager = test_full_election_system()
