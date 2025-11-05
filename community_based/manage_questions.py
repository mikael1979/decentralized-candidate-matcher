#!/usr/bin/env python3
"""
manage_questions.py - REFAKTOROITU VERSIO
Käyttää uutta modulaarista arkkitehtuuria
"""

import argparse
import sys
from cli.cli_template import CLITemplate, main_template

class ManageQuestionsCLI(CLITemplate):
    """Kysymysten hallinta - uusi modulaarinen versio"""
    
    def __init__(self):
        super().__init__("Kysymysten hallinta")
        self.parser = self._create_parser()
    
    def _create_parser(self):
        """Luo komentoriviparser"""
        parser = argparse.ArgumentParser(description=self.description)
        subparsers = parser.add_subparsers(dest='command', help='Komennot')
        
        # Submit komento
        submit_parser = subparsers.add_parser('submit', help='Lähetä uusi kysymys')
        submit_parser.add_argument('--question-fi', required=True, help='Kysymys suomeksi')
        submit_parser.add_argument('--user-id', required=True, help='Käyttäjän ID')
        submit_parser.add_argument('--category', default='general', help='Kysymyksen kategoria')
        
        # Listaa komento
        list_parser = subparsers.add_parser('list', help='Listaa kysymykset')
        list_parser.add_argument('--limit', type=int, default=10, help='Näytettävien määrä')
        
        # Synkronoi komento
        sync_parser = subparsers.add_parser('sync', help='Synkronoi kysymykset')
        sync_parser.add_argument('--type', choices=['tmp_to_new', 'new_to_main', 'all'], 
                                default='tmp_to_new', help='Synkronointityyppi')
        
        # Status komento
        subparsers.add_parser('status', help='Näytä järjestelmän tila')
        
        return parser
    
    def run(self):
        """Suorita ohjelma"""
        args = self.parser.parse_args()
        
        if not args.command:
            self.parser.print_help()
            return 1
        
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
            return self.handle_error(e, f"suoritettaessa komentoa '{args.command}'")
    
    def _handle_submit(self, args):
        """Lähetä kysymys käyttäen uutta handleria"""
        question_data = {
            "content": {
                "question": {
                    "fi": args.question_fi,
                    "en": args.question_fi,  # Käännä tarvittaessa
                    "sv": args.question_fi
                }
            },
            "category": args.category,
            "scale": "agree_disagree"
        }
        
        result = self.question_handler.submit_question(question_data, args.user_id)
        
        if result.get('success'):
            self.print_success("Kysymys lähetetty onnistuneesti!", {
                "Kysymys ID": result.get('question_id'),
                "Jonossa": f"{result.get('queue_position', '?')}. sijalla",
                "Auto-synkronointi": "✅ KÄYTÖSSÄ" if result.get('auto_synced') else "❌ POIS KÄYTÖSTÄ"
            })
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
        """Synkronoi kysymykset"""
        result = self.question_handler.sync_questions(args.type)
        
        if result.get('success'):
            synced_count = result.get('synced_count', 0)
            self.print_success("Synkronointi onnistui!", {
                "Synkronoitu": f"{synced_count} kysymystä",
                "Tyyppi": args.type,
                "Viesti": result.get('message', '')
            })
            return 0
        else:
            print(f"❌ Synkronointi epäonnistui: {result.get('error', 'Tuntematon virhe')}")
            return 1
    
    def _handle_status(self, args):
        """Näytä järjestelmän tila"""
        status = self.question_handler.get_system_status()
        
        print("\n📊 JÄRJESTELMÄN TILA - UUSI ARKKITEHTUURI")
        print("=" * 50)
        print(f"🏗️  Arkkitehtuuri: MODERNI (managers + utils)")
        print(f"🔗 System Chain: {'✅ KÄYTÖSSÄ' if self.system_chain else '❌ POIS KÄYTÖSTÄ'}")
        print(f"❓ Question Handler: {'✅ KÄYTÖSSÄ' if self.question_handler else '❌ POIS KÄYTÖSTÄ'}")
        
        if status.get('sync_status'):
            sync = status['sync_status']
            print(f"\n🔄 SYNKRONOINTITILA:")
            print(f"   Tmp-kysymyksiä: {sync.get('tmp_questions_count', 0)}")
            print(f"   New-kysymyksiä: {sync.get('new_questions_count', 0)}")
            print(f"   Pääkannan kysymyksiä: {sync.get('main_questions_count', 0)}")
        
        print(f"\n🎯 MANAGERIT KÄYTÖSSÄ:")
        for manager, available in status.get('managers_available', {}).items():
            print(f"   {manager}: {'✅' if available else '❌'}")
        
        return 0

if __name__ == "__main__":
    sys.exit(main_template(ManageQuestionsCLI))
