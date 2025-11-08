#!/usr/bin/env python3
"""
Manage Questions CLI - Refaktoroitu uudella arkkitehtuurilla
Kysymysten hallinta unified_question_handlerin kautta
"""
import sys
from cli.cli_template import CLITemplate, main_template

class ManageQuestionsCLI(CLITemplate):
    def __init__(self):
        super().__init__("Kysymysten hallinta", "runtime")
    
    def create_parser(self):
        """Luo parser kysymysten hallinnan komennoille"""
        parser = super().create_parser()
        subparsers = parser.add_subparsers(dest='command', help='Komennot')
        
        # Submit-komento
        submit_parser = subparsers.add_parser('submit', help='Lähetä uusi kysymys')
        submit_parser.add_argument('--question-fi', required=True, help='Kysymys suomeksi')
        submit_parser.add_argument('--question-en', help='Kysymys englanniksi')
        submit_parser.add_argument('--question-sv', help='Kysymys ruotsiksi')
        submit_parser.add_argument('--category', default='Yleinen', help='Kysymyksen kategoria')
        submit_parser.add_argument('--user-id', required=True, help='Käyttäjän ID')
        
        # List-komento
        list_parser = subparsers.add_parser('list', help='Listaa kysymykset')
        list_parser.add_argument('--limit', type=int, default=10, help='Näytettävien kysymysten määrä')
        list_parser.add_argument('--category', help='Suodata kategorian mukaan')
        
        # Sync-komento
        sync_parser = subparsers.add_parser('sync', help='Synkronoi kysymykset')
        sync_parser.add_argument('--type', choices=['tmp_to_new', 'new_to_main', 'all'], required=True, help='Synkronoinnin tyyppi')
        sync_parser.add_argument('--force', action='store_true', help='Pakota synkronointi')
        
        # Status-komento
        subparsers.add_parser('status', help='Näytä kysymysten tila')
        
        return parser
    
    def run(self):
        """Suorita CLI-ohjelma"""
        parser = self.create_parser()
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            return 1
        
        # Käsittele komennot
        try:
            if args.command == 'submit':
                return self._handle_submit(args)
            elif args.command == 'list':
                return self._handle_list(args)
            elif args.command == 'sync':
                return self._handle_sync(args)
            elif args.command == 'status':
                return self._handle_status(args)
            else:
                print(f"❌ Tuntematon komento: {args.command}")
                return 1
        except Exception as e:
            print(f"❌ Odottamaton virhe: {e}")
            import traceback
            traceback.print_exc()
            return 1

    def _handle_submit(self, args):
        """Käsittele kysymyksen lähetys"""
        print("📝 Lähetetään uusi kysymys...")
        
        # Luo kysymysdata
        question_data = {
            "content": {
                "question": {
                    "fi": args.question_fi,
                    "en": args.question_en or args.question_fi,
                    "sv": args.question_sv or args.question_fi
                },
                "category": {
                    "fi": args.category,
                    "en": args.category,
                    "sv": args.category
                }
            },
            "category": args.category,
            "tags": []
        }
        
        # Check available methods for submission
        if hasattr(self.question_handler, 'submit_question'):
            result = self.question_handler.submit_question(question_data, args.user_id)
        else:
            print("❌ submit_question method not available in question_handler")
            available_methods = [method for method in dir(self.question_handler) if not method.startswith('_')]
            print(f"💡 Available methods: {available_methods}")
            return 1
        
        if result.get('success'):
            print("✅ Kysymys lähetetty onnistuneesti!")
            print(f"📋 Kysymys ID: {result.get('question_id')}")
            print(f"📊 Jonossa: {result.get('queue_position')}.")
            print(f"🔄 Automaattinen synkronointi: {'✅' if result.get('auto_synced') else '❌'}")
            
            if result.get('auto_synced'):
                sync_result = result.get('sync_result', {})
                print(f"📦 Synkronoitu: {sync_result.get('synced_count', 0)} kysymystä")
            
            # Lokitus
            self.log_action(
                action_type="question_submitted",
                description=f"Uusi kysymys lähetetty: {args.question_fi[:50]}...",
                question_ids=[result.get('question_id')],
                user_id=args.user_id,
                metadata={
                    "category": args.category,
                    "queue_position": result.get('queue_position'),
                    "auto_synced": result.get('auto_synced')
                }
            )
            return 0
        else:
            print(f"❌ Lähetys epäonnistui: {result.get('error', 'Tuntematon virhe')}")
            return 1

    def _handle_list(self, args):
        """Listaa kysymykset"""
        print("🔍 Haetaan kysymyksiä...")
        
        result = self.question_handler.list_questions(args.limit, args.category)
        
        if result.get('success'):
            questions = result.get('questions', [])
            sources = result.get('sources', {})
            
            print(f"📋 KYSYMYSLISTA ({len(questions)}/{result.get('total_count', 0)} kysymystä)")
            print(f"   📚 ELO Manager: {sources.get('elo_manager', 0)}")
            print(f"   🆕 New questions: {sources.get('new_questions', 0)}") 
            print(f"   📝 Tmp questions: {sources.get('tmp_questions', 0)}")
            print("=" * 60)
            
            if not questions:
                print("ℹ️  Ei kysymyksiä saatavilla")
                return 0
                
            for i, question in enumerate(questions, 1):
                # Hae sisältö
                content_obj = question.get('content', {})
                question_texts = content_obj.get('question', {})
                category_obj = content_obj.get('category', {})
                
                content = (question_texts.get('fi') or 
                          question_texts.get('en') or 
                          question_texts.get('sv') or 'Ei nimeä')
                
                category = (category_obj.get('fi') or 
                           category_obj.get('en') or 
                           category_obj.get('sv') or 'tuntematon')
                
                rating_obj = question.get('elo_rating', {})
                rating = rating_obj.get('current_rating', 0)
                question_id = question.get('local_id', 'N/A')
                
                # Tarkista mistä tiedostosta kysymys tulee
                source = "questions.json"
                if question_id.startswith('tmp_'):
                    source = "tmp"
                elif 'new_questions' in str(question):
                    source = "new"
                
                print(f"{i:2d}. {rating:6.1f} | {category:12} | {content[:45]}... [{source}]")
            
            # Lokitus
            self.log_action(
                action_type="questions_listed",
                description=f"Listattu {len(questions)} kysymystä",
                user_id="cli_user",
                metadata={
                    "limit": args.limit, 
                    "category": args.category,
                    "sources": sources
                }
            )
            
            return 0
        else:
            print(f"❌ Listaus epäonnistui: {result.get('error', 'Tuntematon virhe')}")
            return 1

    def _handle_sync(self, args):
        """Käsittele synkronointi"""
        print(f"🔄 Synkronoidaan kysymyksiä ({args.type})...")
        
        success = True
        
        if args.type == 'tmp_to_new' or args.type == 'all':
            if hasattr(self.question_handler, 'sync_tmp_to_new'):
                result = self.question_handler.sync_tmp_to_new(args.force)
                if result.get('success'):
                    print(f"✅ Tmp → New: {result.get('synced_count', 0)} kysymystä")
                    if result.get('remaining_in_tmp', 0) > 0:
                        print(f"📊 Jäljellä tmp:ssä: {result.get('remaining_in_tmp')}")
                else:
                    print(f"❌ Tmp → New epäonnistui: {result.get('error')}")
                    success = False
                    if args.type == 'all':
                        return 1
            else:
                print("❌ sync_tmp_to_new method not available")
                success = False
        
        if args.type == 'new_to_main' or args.type == 'all':
            if hasattr(self.question_handler, 'sync_new_to_main'):
                result = self.question_handler.sync_new_to_main(args.force)
                if result.get('success'):
                    print(f"✅ New → Main: {result.get('synced_count', 0)} kysymystä")
                else:
                    print(f"❌ New → Main epäonnistui: {result.get('error')}")
                    success = False
                    return 1
            else:
                print("❌ sync_new_to_main method not available")
                success = False
        
        if success:
            # Lokitus
            self.log_action(
                action_type="questions_synced",
                description=f"Kysymyksiä synkronoitu: {args.type}",
                user_id="cli_user",
                metadata={"sync_type": args.type, "forced": args.force}
            )
        
        return 0 if success else 1

    def _handle_status(self, args):
        """Näytä kysymysten tila"""
        if hasattr(self.question_handler, 'get_sync_status'):
            result = self.question_handler.get_sync_status()
        elif hasattr(self.question_handler, 'get_system_status'):
            result = self.question_handler.get_system_status()
        else:
            print("❌ get_sync_status or get_system_status method not available")
            return 1
        
        if 'error' in result:
            print(f"❌ Tilahaun virhe: {result['error']}")
            return 1
        
        print("📊 KYSYMYSTEN TILA")
        print("=" * 50)
        print(f"📝 Tmp-kysymyksiä: {result.get('tmp_questions_count', 0)}")
        print(f"🆕 New-kysymyksiä: {result.get('new_questions_count', 0)}")
        print(f"📚 Pääkannan kysymyksiä: {result.get('main_questions_count', 0)}")
        print(f"📦 Eräkoko: {result.get('batch_size_progress', 'N/A')}")
        print(f"🔄 Automaattinen synkronointi: {'✅' if result.get('auto_sync_enabled') else '❌'}")
        print(f"⏰ Seuraava synkronointi: {result.get('next_sync_time', 'N/A')}")
        print(f"⏳ Aikaa synkronointiin: {result.get('time_until_sync', 'N/A')}")
        
        # Näytä ajanvarauksen tila jos saatavilla
        if result.get('use_schedule'):
            schedule_status = result.get('schedule_status', {})
            print(f"📅 Ajanvaraus: ✅ KÄYTÖSSÄ")
            print(f"   Tulevat varaukset: {schedule_status.get('upcoming', 0)}")
        
        return 0

if __name__ == "__main__":
    sys.exit(main_template(ManageQuestionsCLI))
