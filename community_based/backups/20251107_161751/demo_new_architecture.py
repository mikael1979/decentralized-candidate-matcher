#!/usr/bin/env python3
"""
Demo: Uuden Arkkitehtuurin Testaus ja Esittely
Näyttää kuinka kaikki uudet moduulit toimivat yhdessä
"""

import sys
import time
from pathlib import Path

def main():
    print("🎯 UUDEN ARKKITEHTUURIN DEMO")
    print("=" * 60)
    
    try:
        # 1. Alusta Dependency Container
        print("\n1. 🔄 ALUSTETAAN DEPENDENCY CONTAINER...")
        from core.dependency_container import get_container
        
        container = get_container(config_dir="config", runtime_dir="runtime")
        container.initialize()
        
        print("✅ Dependency container alustettu onnistuneesti!")
        
        # 2. Näytä järjestelmän tila
        print("\n2. 📊 JÄRJESTELMÄN TILA:")
        system_status = container.get_system_status()
        
        print(f"   • Initialized: {system_status['initialized']}")
        print(f"   • Mode: {system_status['configuration']['mode']}")
        print(f"   • IPFS käytössä: {system_status['dependencies']['ipfs_available']}")
        print(f"   • Repository: {type(container.question_repository).__name__}")
        
        # 3. Testaa kysymyksen lähetys
        print("\n3. 📝 TESTATAAN KYSYMYKSEN LÄHETTÄMISTÄ...")
        from application.commands import SubmitQuestionCommand
        from domain.value_objects import MultilingualText, Category, Scale, UserId
        
        # Luo testikysymys
        content = MultilingualText(
            fi="Pitäisiko kaupungin investoida enemmän pyöräteihin?",
            en="Should the city invest more in bicycle paths?",
            sv="Bör staden investera mer i cykelvägar?"
        )
        
        category = Category(
            name=MultilingualText(
                fi="Liikenne",
                en="Transportation", 
                sv="Transport"
            )
        )
        
        scale = Scale(
            min=-5,
            max=5,
            labels={
                "fi": {
                    "min": "Täysin eri mieltä",
                    "neutral": "Neutraali",
                    "max": "Täysin samaa mieltä"
                },
                "en": {
                    "min": "Strongly disagree",
                    "neutral": "Neutral", 
                    "max": "Strongly agree"
                },
                "sv": {
                    "min": "Helt avig",
                    "neutral": "Neutral",
                    "max": "Helt enig"
                }
            }
        )
        
        submit_command = SubmitQuestionCommand(
            content=content,
            category=category,
            scale=scale,
            submitted_by=UserId("demo_user_123"),
            tags=["liikenne", "kestävä kehitys", "kaupunkisuunnittelu"],
            metadata={"demo": True, "timestamp": time.time()}
        )
        
        result = container.question_service.submit_question(submit_command)
        
        if result.success:
            print(f"✅ Kysymys lähetetty onnistuneesti!")
            print(f"   • Kysymys ID: {result.data['question_id']}")
            print(f"   • Jonossa: {result.data['queue_position']}. sijalla")
            question_id = result.data['question_id']
        else:
            print(f"❌ Kysymyksen lähetys epäonnistui: {result.message}")
            return 1
        
        # 4. Testaa toinen kysymys
        print("\n4. 📝 LÄHETETÄÄN TOINEN KYSYMYS...")
        content2 = MultilingualText(
            fi="Tulisiko julkisen liikenteen hinnan olla ilmaista kaikille?",
            en="Should public transportation be free for everyone?",
            sv="Bör kollektivtrafiken vara gratis för alla?"
        )
        
        category2 = Category(
            name=MultilingualText(
                fi="Julkinen liikenne",
                en="Public Transportation",
                sv="Kollektivtrafik"
            )
        )
        
        submit_command2 = SubmitQuestionCommand(
            content=content2,
            category=category2,
            scale=scale,  # Sama asteikko
            submitted_by=UserId("demo_user_456"),
            tags=["julkinen liikenne", "hinnat", "saavutettavuus"],
            metadata={"demo": True}
        )
        
        result2 = container.question_service.submit_question(submit_command2)
        
        if result2.success:
            print(f"✅ Toinen kysymys lähetetty!")
            print(f"   • Kysymys ID: {result2.data['question_id']}")
            question_id2 = result2.data['question_id']
        else:
            print(f"❌ Toisen kysymyksen lähetys epäonnistui")
            question_id2 = "q_demo_2"
        
        # 5. Tarkista kysymysten tila
        print("\n5. 📊 TARKISTETAAN KYSYMYSJONON TILA...")
        from application.queries import import import import import  GetQuestionStatusQuery
        
        status_query = GetQuestionStatusQuery(include_stats=True)
        status_result = container.question_service.get_question_status(status_query)
        
        if status_result.success:
            data = status_result.data
            print(f"   • Väliaikaisia kysymyksiä: {data.get('temporary_questions', 0)}")
            print(f"   • Uusia kysymyksiä: {data.get('new_questions', 0)}")
            print(f"   • Aktiivisia kysymyksiä: {data.get('active_questions', 0)}")
            print(f"   • Keskimääräinen rating: {data.get('average_rating', 0):.1f}")
        else:
            print(f"   ❌ Tilatietojen haku epäonnistui: {status_result.error}")
        
        # 6. Testaa vertailu
        print("\n6. 🔄 TESTATAAN KYSYMYSVERTAILUA...")
        from application.commands import ProcessComparisonCommand
        
        # Oletetaan että kysymykset on nyt synkronoitu uusiin kysymyksiin
        # Käytetään ensimmäistä kysymystä vertailuun
        comparison_command = ProcessComparisonCommand(
            question_a_id=question_id,
            question_b_id=question_id2, 
            result="a_wins",  # Ensimmäinen kysymys voittaa
            user_id=UserId("comparison_user_123"),
            user_trust="regular_user",
            metadata={"demo": True, "comparison_type": "test"}
        )
        
        comparison_result = container.question_service.process_comparison(comparison_command)
        
        if comparison_result.success:
            print(f"✅ Vertailu käsitelty onnistuneesti!")
            data = comparison_result.data
            print(f"   • Kysymys A muutos: {data['question_a_change']:+d}")
            print(f"   • Kysymys B muutos: {data['question_b_change']:+d}")
            print(f"   • Uusi rating A: {data['new_rating_a']}")
            print(f"   • Uusi rating B: {data['new_rating_b']}")
        else:
            print(f"❌ Vertailun käsittely epäonnistui: {comparison_result.message}")
        
        # 7. Testaa äänestys
        print("\n7. 🗳️ TESTATAAN ÄÄNESTYSTÄ...")
        from application.commands import ProcessVoteCommand
        
        vote_command = ProcessVoteCommand(
            question_id=question_id,
            vote_type="upvote",
            user_id=UserId("voter_123"),
            confidence=4,  # Melko varma
            user_trust="regular_user",
            metadata={"demo": True}
        )
        
        vote_result = container.question_service.process_vote(vote_command)
        
        if vote_result.success:
            print(f"✅ Ääni käsitelty onnistuneesti!")
            data = vote_result.data
            print(f"   • Äänen tyyppi: {data['vote_type']}")
            print(f"   • Luottamus: {data['confidence']}/5")
            print(f"   • Rating-vaikutus: {data['rating_impact']:+d}")
            print(f"   • Uusi rating: {data['new_rating']}")
        else:
            print(f"❌ Äänestyksen käsittely epäonnistui: {vote_result.message}")
        
        # 8. Testaa synkronointi
        print("\n8. 🔄 TESTATAAN SYNKRONOINTIA...")
        from application.commands import SyncQuestionsCommand
        
        sync_command = SyncQuestionsCommand(
            sync_type="tmp_to_new",
            batch_size=2,
            force=True,  # Pakota synkronointi
            requested_by=UserId("demo_sync_user")
        )
        
        sync_result = container.question_service.sync_questions(sync_command)
        
        if sync_result.success:
            print(f"✅ Synkronointi onnistui!")
            data = sync_result.data
            print(f"   • Synkronoitu: {data['synced_count']} kysymystä")
            print(f"   • Jäljellä: {data['remaining_count']} kysymystä")
            print(f"   • Tyyppi: {data['sync_type']}")
        else:
            print(f"❌ Synkronointi epäonnistui: {sync_result.message}")
        
        # 9. Hae aktiiviset kysymykset
        print("\n9. 📋 HAE AKTIIVISET KYSYMYKSET...")
        from application.queries import import import import import  GetActiveQuestionsQuery
        
        active_query = GetActiveQuestionsQuery(
            election_id="demo_election_2024",
            limit=5
        )
        
        active_result = container.question_service.get_active_questions(active_query)
        
        if active_result.success:
            data = active_result.data
            questions = data.get('questions', [])
            print(f"✅ Löytyi {len(questions)} aktiivista kysymystä:")
            
            for i, question in enumerate(questions, 1):
                content = question.get('content', {})
                question_text = content.get('question', {})
                rating = question.get('elo_rating', {})
                
                print(f"   {i}. {question_text.get('fi', 'N/A')[:50]}...")
                print(f"      Rating: {rating.get('current_rating', 'N/A')}")
                print(f"      Vertailut: {rating.get('total_comparisons', 0)}")
                print()
        else:
            print(f"❌ Aktiivisten kysymysten haku epäonnistui: {active_result.error}")
        
        # 10. Testaa legacy-integraatio
        print("\n10. 🔗 TESTATAAN LEGACY-INTEGRAATIOTA...")
        from infrastructure.services.legacy_integration import LegacyIntegrationService
        
        integration = LegacyIntegrationService(runtime_dir="runtime")
        integration_status = integration.get_integration_status()
        
        print(f"   • Legacy-tiedostoja: {len(integration_status['legacy_files'])}")
        print(f"   • Uusia kysymyksiä: {integration_status['new_repository'].get('total_questions', 0)}")
        print(f"   • Migraatio suositeltu: {integration_status['migration_recommended']}")
        
        # 11. System chain -tila
        print("\n11. 🔗 SYSTEM CHAIN -TILA:")
        chain_status = container.system_logger.get_chain_status()
        print(f"   • Lohkoja: {chain_status.get('total_blocks', 0)}")
        print(f"   • Eheys varmistettu: {chain_status.get('integrity_verified', False)}")
        print(f"   • Viimeisin päivitys: {chain_status.get('last_updated', 'N/A')}")
        
        # 12. Lopetustilanne
        print("\n" + "=" * 60)
        print("🎉 DEMO SUORITETTU ONNISTUNEESTI!")
        print("\n📈 LOPPUTILANNE:")
        
        final_stats = container.question_repository.get_question_stats()
        print(f"   • Kysymyksiä yhteensä: {final_stats.get('total_questions', 0)}")
        print(f"   • Keskimääräinen rating: {final_stats.get('average_rating', 0):.1f}")
        
        # Näytä repositoryn tilastot
        recent_activity = final_stats.get('recent_activity', {})
        print(f"   • Väliaikaisia: {recent_activity.get('tmp_questions', 0)}")
        print(f"   • Uusia: {recent_activity.get('new_questions', 0)}")
        print(f"   • Aktiivisia: {recent_activity.get('active_questions', 0)}")
        
        print("\n💡 SEURAAVAT VAIheet:")
        print("   - Suorita: python manage_questions.py status (vanha järjestelmä)")
        print("   - Suorita: python demo_new_architecture.py (uusi järjestelmä)") 
        print("   - Vertaa tuloksia")
        print("   - Testaa: python interface/cli/question_cli.py system-status")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ DEMO EPAONNISTUI: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
