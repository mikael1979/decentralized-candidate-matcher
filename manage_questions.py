#!/usr/bin/env python3
"""
Manage Questions CLI - Refaktoroitu uudella arkkitehtuurilla
Kysymysten hallinta unified_question_handlerin kautta
"""

import sys
from cli.cli_template import CLITemplate, main_template
from managers.unified_question_handler import UnifiedQuestionHandler

class ManageQuestionsCLI(CLITemplate):
    def __init__(self):
        super().__init__("Kysymysten hallinta")
        self.question_handler = UnifiedQuestionHandler()
    
    def _add_arguments(self, parser):
        """Lisää kysymysten hallinnan spesifiset argumentit"""
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
    
    def run(self):
        """Suorita CLI-ohjelma"""
        if not self.initialized:
            print("❌ Järjestelmää ei ole alustettu")
            return 1
        
        args = self.parser.parse_args()
        
        if not args.command:
            self.parser.print_help()
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
            }
        }
        
        result = self.question_handler.submit_question(question_data, args.user_id)
        
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
        result = self.question_handler.list_questions(args.limit, args.category)
        
        if result.get('success'):
            questions = result.get('questions', [])
            print(f"📋 KYSYMYSLISTA ({len(questions)}/{result.get('total_count', 0)} kysymystä)")
            print("=" * 60)
            
            for i, question in enumerate(questions, 1):
                content = question.get('content', {}).get('question', {}).get('fi', 'Ei nimeä')
                rating = question.get('elo_rating', {}).get('current_rating', 0)
                category = question.get('content', {}).get('category', {}).get('fi', 'tuntematon')
                
                print(f"{i:2d}. {rating:6.1f} | {category:12} | {content[:45]}...")
            
            # Lokitus
            self.log_action(
                action_type="questions_listed",
                description=f"Listattu {len(questions)} kysymystä",
                user_id="cli_user",
                metadata={"limit": args.limit, "category": args.category}
            )
            
            return 0
        else:
            print(f"❌ Listaus epäonnistui: {result.get('error', 'Tuntematon virhe')}")
            return 1
    
    def _handle_sync(self, args):
        """Käsittele synkronointi"""
        print(f"🔄 Synkronoidaan kysymyksiä ({args.type})...")
        
        if args.type == 'tmp_to_new' or args.type == 'all':
            result = self.question_handler.sync_tmp_to_new(args.force)
            if result.get('success'):
                print(f"✅ Tmp → New: {result.get('synced_count', 0)} kysymystä")
                if result.get('remaining_in_tmp', 0) > 0:
                    print(f"📊 Jäljellä tmp:ssä: {result.get('remaining_in_tmp')}")
            else:
                print(f"❌ Tmp → New epäonnistui: {result.get('error')}")
                if args.type == 'all':
                    return 1
        
        if args.type == 'new_to_main' or args.type == 'all':
            result = self.question_handler.sync_new_to_main(args.force)
            if result.get('success'):
                print(f"✅ New → Main: {result.get('synced_count', 0)} kysymystä")
            else:
                print(f"❌ New → Main epäonnistui: {result.get('error')}")
                return 1
        
        # Lokitus
        self.log_action(
            action_type="questions_synced",
            description=f"Kysymyksiä synkronoitu: {args.type}",
            user_id="cli_user",
            metadata={"sync_type": args.type, "forced": args.force}
        )
        
        return 0
    
    def _handle_status(self, args):
        """Näytä kysymysten tila"""
        result = self.question_handler.get_sync_status()
        
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
