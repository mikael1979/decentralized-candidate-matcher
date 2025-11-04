#!/usr/bin/env python3
# manage_questions.py - PÄIVITETTY UUDELLE ARKKITEHTUURILLE
"""
Kysymysten hallintakomento - PÄIVITETTY KÄYTTÄMÄÄN UUTTA ARKKITEHTUURIA
Käyttää domain/application/infrastructure layer -komponentteja
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from datetime import timezone

# UUSI ARKKITEHTUURI: Käytä uusia moduuleja
from core.dependency_container import get_container, initialize_container
from application.commands import (
    SubmitQuestionCommand, 
    SyncQuestionsCommand,
    ListQuestionsCommand,
    GetQuestionCommand,
    UpdateQuestionCommand
)
from application.use_cases.submit_question import SubmitQuestionUseCase
from application.use_cases.sync_questions import SyncQuestionsUseCase
from application.use_cases.process_rating import ProcessRatingUseCase
from application.query_handlers.question_queries import QuestionQueryHandler
from domain.entities.question import Question
from domain.value_objects import QuestionContent, QuestionScale, QuestionId

class ModernQuestionCLI:
    """Moderni kysymysten hallinta CLI uuden arkkitehtuurin päällä"""
    
    def __init__(self, runtime_dir: str = "runtime"):
        self.runtime_dir = Path(runtime_dir)
        
        # UUSI ARKKITEHTUURI: Hae riippuvuudet containerista
        print("🔄 Alustetaan uusi arkkitehtuuri...")
        if not initialize_container(runtime_dir):
            print("❌ Dependency Containerin alustus epäonnistui")
            sys.exit(1)
            
        self.container = get_container(runtime_dir)
        self.question_service = self.container.get_question_service()
        self.query_handler = QuestionQueryHandler(self.question_service)
        
        print("✅ Modern Question CLI alustettu uudella arkkitehtuurilla")
    
    def submit_question(self, args):
        """Lähetä uusi kysymys - UUSI ARKKITEHTUURI"""
        try:
            # Lue kysymyksen sisältö
            if args.file:
                with open(args.file, 'r', encoding='utf-8') as f:
                    question_data = json.load(f)
            else:
                question_data = {
                    "content": {
                        "question": {
                            "fi": args.question_fi,
                            "en": args.question_en or args.question_fi,
                            "sv": args.question_sv or args.question_fi
                        }
                    },
                    "category": args.category,
                    "scale": args.scale,
                    "tags": args.tags or []
                }
            
            # UUSI ARKKITEHTUURI: Käytä Command/UseCase -mallia
            command = SubmitQuestionCommand(
                content=question_data["content"],
                category=question_data.get("category", "general"),
                scale=question_data.get("scale", "agree_disagree"),
                submitted_by=args.user_id or "cli_user",
                tags=question_data.get("tags", []),
                metadata=question_data.get("metadata", {})
            )
            
            use_case = SubmitQuestionUseCase(self.question_service)
            result = use_case.execute(command)
            
            if result.success:
                print(f"✅ Kysymys lähetetty onnistuneesti!")
                print(f"   Kysymys ID: {result.question_id}")
                print(f"   Jonossa: {result.queue_position}. sijalla")
                print(f"   Auto-synkronointi: {'KÄYTÖSSÄ' if result.auto_synced else 'POIS KÄYTÖSTÄ'}")
                
                # Näytä kysymyksen esikatselu
                question = self.query_handler.get_question_by_id(result.question_id)
                if question:
                    self._print_question_preview(question)
            else:
                print(f"❌ Kysymyksen lähetys epäonnistui: {result.message}")
                return 1
                
        except Exception as e:
            print(f"❌ Virhe kysymyksen lähetyksessä: {e}")
            return 1
        
        return 0
    
    def list_questions(self, args):
        """Listaa kysymykset - UUSI ARKKITEHTUURI"""
        try:
            # UUSI ARKKITEHTUURI: Käytä query handleria
            query = ListQuestionsCommand(
                limit=args.limit,
                offset=args.offset,
                category=args.category,
                tags=args.tags,
                sort_by=args.sort_by,
                sort_order=args.sort_order
            )
            
            questions = self.query_handler.list_questions(query)
            
            print(f"\n📋 KYSYMYKSET ({len(questions)} kpl)")
            print("=" * 80)
            
            for i, question in enumerate(questions, 1):
                self._print_question_summary(question, i)
                
            # Näytä tilastot
            stats = self.query_handler.get_question_stats()
            print(f"\n📊 Tilastot:")
            print(f"   Yhteensä: {stats['total_questions']} kysymystä")
            print(f"   Keskimääräinen rating: {stats['average_rating']:.1f}")
            print(f"   Kategoriat: {', '.join(stats['categories'])}")
            
        except Exception as e:
            print(f"❌ Virhe kysymysten listauksessa: {e}")
            return 1
        
        return 0
    
    def show_question(self, args):
        """Näytä yksittäinen kysymys - UUSI ARKKITEHTUURI"""
        try:
            # UUSI ARKKITEHTUURI: Käytä query handleria
            question = self.query_handler.get_question_by_id(args.question_id)
            
            if not question:
                print(f"❌ Kysymystä ei löydy ID:llä: {args.question_id}")
                return 1
            
            print(f"\n🔍 KYSYMYS: {args.question_id}")
            print("=" * 60)
            self._print_question_detail(question)
            
        except Exception as e:
            print(f"❌ Virhe kysymyksen näyttämisessä: {e}")
            return 1
        
        return 0
    
    def sync_questions(self, args):
        """Synkronoi kysymykset - UUSI ARKKITEHTUURI"""
        try:
            print("🔄 Synkronoidaan kysymyksiä...")
            
            # UUSI ARKKITEHTUURI: Käytä UseCase -mallia
            command = SyncQuestionsCommand(
                sync_type=args.sync_type,
                force=args.force,
                batch_size=args.batch_size
            )
            
            use_case = SyncQuestionsUseCase(
                question_service=self.question_service,
                ipfs_repository=self.container.ipfs_question_repo
            )
            
            result = use_case.execute(command)
            
            if result.success:
                print(f"✅ Synkronointi onnistui!")
                print(f"   Synkronoitu: {result.synced_count} kysymystä")
                print(f"   Viesti: {result.message}")
                
                if result.remaining_count > 0:
                    print(f"   Jäljellä: {result.remaining_count} kysymystä")
            else:
                print(f"❌ Synkronointi epäonnistui: {result.message}")
                return 1
                
        except Exception as e:
            print(f"❌ Virhe synkronoinnissa: {e}")
            return 1
        
        return 0
    
    def get_status(self, args):
        """Näytä kysymysjärjestelmän tila - UUSI ARKKITEHTUURI"""
        try:
            # UUSI ARKKITEHTUURI: Käytä question serviceä
            status = self.question_service.get_system_status()
            sync_status = self.question_service.get_sync_status()
            
            print("\n📊 KYSYMYSJÄRJESTELMÄN TILA - UUSI ARKKITEHTUURI")
            print("=" * 50)
            
            print(f"🏥 Terveystila: {'✅ TERVE' if status['healthy'] else '❌ ONGELMIA'}")
            print(f"📦 Kysymyksiä yhteensä: {status['total_questions']}")
            print(f"🔗 Synkronointi: {'✅ AKTIIVINEN' if status['sync_enabled'] else '❌ POIS KÄYTÖSTÄ'}")
            
            if sync_status:
                print(f"\n🔄 SYNKRONOINTITILA:")
                print(f"   Tmp-kysymyksiä: {sync_status.get('tmp_questions_count', 0)}")
                print(f"   New-kysymyksiä: {sync_status.get('new_questions_count', 0)}")
                print(f"   Pääkannan kysymyksiä: {sync_status.get('main_questions_count', 0)}")
                print(f"   Seuraava synkronointi: {sync_status.get('next_sync_time', 'N/A')}")
            
            # Näytä top-kysymykset
            top_questions = self.query_handler.get_top_questions(limit=3)
            if top_questions:
                print(f"\n🏆 TOP 3 KYSYMYSTÄ:")
                for i, question in enumerate(top_questions, 1):
                    content = question.content.get_text('fi')
                    rating = question.elo_rating.current_rating
                    print(f"   {i}. {rating:.1f} - {content[:50]}...")
            
            # Näytä arkkitehtuuritiedot
            print(f"\n🏗️  ARKKITEHTUURI:")
            print(f"   Tyyppi: MODERNI (domain/application/infrastructure)")
            print(f"   Container: ✅ ALUSTETTU")
            print(f"   Services: ✅ KÄYTÖSSÄ")
            
        except Exception as e:
            print(f"❌ Virhe tilan haussa: {e}")
            return 1
        
        return 0
    
    def export_questions(self, args):
        """Vie kysymykset tiedostoon - UUSI ARKKITEHTUURI"""
        try:
            # UUSI ARKKITEHTUURI: Käytä query handleria
            query = ListQuestionsCommand(
                limit=args.limit,
                category=args.category,
                tags=args.tags
            )
            
            questions = self.query_handler.list_questions(query)
            
            export_data = {
                "metadata": {
                    "exported_at": datetime.now(timezone.utc).isoformat(),
                    "total_questions": len(questions),
                    "export_format": "json",
                    "architecture": "modern",
                    "version": "2.0.0"
                },
                "questions": [question.to_dict() for question in questions]
            }
            
            output_file = Path(args.output_file)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, ensure_ascii=False)
            
            print(f"✅ Kysymykset viety tiedostoon: {output_file}")
            print(f"   Viettiin: {len(questions)} kysymystä")
            print(f"   Tiedostokoko: {output_file.stat().st_size} tavua")
            
        except Exception as e:
            print(f"❌ Virhe vientiä tehdessä: {e}")
            return 1
        
        return 0
    
    def _print_question_preview(self, question: Question):
        """Tulosta kysymyksen esikatselu"""
        content = question.content.get_text('fi')
        print(f"\n📝 KYSYMYS:")
        print(f"   {content}")
        print(f"   💫 Rating: {question.elo_rating.current_rating:.1f}")
        print(f"   🏷️  Kategoria: {question.category}")
        print(f"   📊 Asteikko: {question.scale}")
        print(f"   🔖 Tunnisteet: {', '.join(question.tags)}")
    
    def _print_question_summary(self, question: Question, index: int):
        """Tulosta kysymyksen yhteenveto"""
        content = question.content.get_text('fi')
        rating = question.elo_rating.current_rating
        comparisons = question.elo_rating.total_comparisons
        votes = question.elo_rating.total_votes
        
        print(f"{index:2d}. {rating:6.1f} | {comparisons:3d} vert. | {votes:3d} ääntä | {question.category:12} | {content[:50]}...")
    
    def _print_question_detail(self, question: Question):
        """Tulosta kysymyksen yksityiskohtaiset tiedot"""
        # Perustiedot
        print(f"📝 SISÄLTÖ:")
        for lang, text in question.content.texts.items():
            print(f"   {lang.upper()}: {text}")
        
        print(f"\n💫 ELO-LUOKITUS:")
        print(f"   Nykyinen rating: {question.elo_rating.current_rating:.1f}")
        print(f"   Perusrating: {question.elo_rating.base_rating}")
        print(f"   Vertailuja: {question.elo_rating.total_comparisons}")
        print(f"   Ääniä: {question.elo_rating.total_votes}")
        print(f"   Ylä-äänet: {question.elo_rating.up_votes}")
        print(f"   Ala-äänet: {question.elo_rating.down_votes}")
        
        print(f"\n🏷️  METATIEDOT:")
        print(f"   Kategoria: {question.category}")
        print(f"   Asteikko: {question.scale}")
        print(f"   Tunnisteet: {', '.join(question.tags)}")
        print(f"   Luotu: {question.timestamps.created_local}")
        print(f"   Päivitetty: {question.timestamps.modified_local}")
        
        if question.metadata:
            print(f"   Lisämetadata: {json.dumps(question.metadata, ensure_ascii=False, indent=2)}")

def main():
    """Pääohjelma - UUSI ARKKITEHTUURI"""
    parser = argparse.ArgumentParser(
        description="Kysymysten hallinta - Moderni arkkitehtuuri",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esimerkkejä:
  # Lähetä uusi kysymys
  python manage_questions.py submit "Mielipidekysymys" --category politics --user-id user123
  
  # Listaa kysymykset
  python manage_questions.py list --limit 10 --sort-by rating
  
  # Näytä yksittäinen kysymys
  python manage_questions.py show --question-id q123456
  
  # Synkronoi kysymykset
  python manage_questions.py sync --sync-type tmp_to_new
  
  # Vie kysymykset tiedostoon
  python manage_questions.py export --output-file questions_export.json
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Komennot')
    
    # Submit komento
    submit_parser = subparsers.add_parser('submit', help='Lähetä uusi kysymys')
    submit_parser.add_argument('question_fi', help='Kysymys suomeksi')
    submit_parser.add_argument('--question-en', help='Kysymys englanniksi')
    submit_parser.add_argument('--question-sv', help='Kysymys ruotsiksi')
    submit_parser.add_argument('--file', help='JSON-tiedosto kysymyksille')
    submit_parser.add_argument('--category', default='general', help='Kategoria')
    submit_parser.add_argument('--scale', default='agree_disagree', 
                              choices=['agree_disagree', 'importance', 'frequency'],
                              help='Vastaustyyppi')
    submit_parser.add_argument('--tags', nargs='+', help='Tunnisteet')
    submit_parser.add_argument('--user-id', required=True, help='Käyttäjän ID')
    
    # List komento
    list_parser = subparsers.add_parser('list', help='Listaa kysymykset')
    list_parser.add_argument('--limit', type=int, default=20, help='Näytettävien määrä')
    list_parser.add_argument('--offset', type=int, default=0, help='Aloituskohta')
    list_parser.add_argument('--category', help='Suodata kategorian mukaan')
    list_parser.add_argument('--tags', nargs='+', help='Suodata tunnisteiden mukaan')
    list_parser.add_argument('--sort-by', choices=['rating', 'created', 'comparisons'], 
                            default='rating', help='Lajitteluperuste')
    list_parser.add_argument('--sort-order', choices=['asc', 'desc'], 
                            default='desc', help='Lajittelujärjestys')
    
    # Show komento
    show_parser = subparsers.add_parser('show', help='Näytä yksittäinen kysymys')
    show_parser.add_argument('--question-id', required=True, help='Kysymyksen ID')
    
    # Sync komento
    sync_parser = subparsers.add_parser('sync', help='Synkronoi kysymykset')
    sync_parser.add_argument('--sync-type', choices=['tmp_to_new', 'new_to_main', 'all'],
                            default='tmp_to_new', help='Synkronointityyppi')
    sync_parser.add_argument('--force', action='store_true', help='Pakota synkronointi')
    sync_parser.add_argument('--batch-size', type=int, default=5, help='Erän koko')
    
    # Status komento
    subparsers.add_parser('status', help='Näytä järjestelmän tila')
    
    # Export komento
    export_parser = subparsers.add_parser('export', help='Vie kysymykset tiedostoon')
    export_parser.add_argument('--output-file', required=True, help='Kohdetiedosto')
    export_parser.add_argument('--limit', type=int, help='Vieittävien määrä')
    export_parser.add_argument('--category', help='Suodata kategorian mukaan')
    export_parser.add_argument('--tags', nargs='+', help='Suodata tunnisteiden mukaan')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        # Alusta CLI uudella arkkitehtuurilla
        cli = ModernQuestionCLI()
        
        # Suorita komento
        if args.command == 'submit':
            return cli.submit_question(args)
        elif args.command == 'list':
            return cli.list_questions(args)
        elif args.command == 'show':
            return cli.show_question(args)
        elif args.command == 'sync':
            return cli.sync_questions(args)
        elif args.command == 'status':
            return cli.get_status(args)
        elif args.command == 'export':
            return cli.export_questions(args)
        else:
            print(f"❌ Tuntematon komento: {args.command}")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️  Keskeytetty käyttäjän toimesta")
        return 1
    except Exception as e:
        print(f"❌ Odottamaton virhe: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    print("🚀 MODERN QUESTION MANAGER - UUSI ARKKITEHTUURI")
    print("=" * 50)
    sys.exit(main())
