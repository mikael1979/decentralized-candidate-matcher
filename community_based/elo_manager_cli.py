#!/usr/bin/env python3
"""
ELO Manager CLI - Refaktoroitu uudella arkkitehtuurilla
"""

import sys
from cli.cli_template import CLITemplate, main_template
from managers.unified_question_handler import UnifiedQuestionHandler

class ELOManagerCLI(CLITemplate):
    def __init__(self):
        super().__init__("ELO-laskenta")
        self.question_handler = UnifiedQuestionHandler()
    
    def _add_arguments(self, parser):
        """Lisää ELO-spesifiset argumentit"""
        subparsers = parser.add_subparsers(dest='command', help='Komennot')
        
        # Compare-komento
        compare_parser = subparsers.add_parser('compare', help='Käsittele kysymysvertailu')
        compare_parser.add_argument('--user-id', required=True, help='Käyttäjän ID')
        compare_parser.add_argument('--question-a', required=True, help='Kysymys A ID')
        compare_parser.add_argument('--question-b', required=True, help='Kysymys B ID') 
        compare_parser.add_argument('--result', choices=['a_wins', 'b_wins', 'tie'], required=True, help='Vertailun tulos')
        compare_parser.add_argument('--user-trust', default='regular_user', choices=['new_user', 'regular_user', 'trusted_user', 'validator'], help='Käyttäjän luottamustaso')
        
        # Vote-komento
        vote_parser = subparsers.add_parser('vote', help='Käsittele ääni')
        vote_parser.add_argument('--user-id', required=True, help='Käyttäjän ID')
        vote_parser.add_argument('--question-id', required=True, help='Kysymyksen ID')
        vote_parser.add_argument('--vote-type', choices=['upvote', 'downvote'], required=True, help='Äänen tyyppi')
        vote_parser.add_argument('--confidence', type=int, choices=range(1,6), default=3, help='Luottamus (1-5)')
        vote_parser.add_argument('--user-trust', default='regular_user', choices=['new_user', 'regular_user', 'trusted_user', 'validator'], help='Käyttäjän luottamustaso')
        
        # Stats-komento
        stats_parser = subparsers.add_parser('stats', help='Näytä kysymyksen tilastot')
        stats_parser.add_argument('--question-id', required=True, help='Kysymyksen ID')
    
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
            if args.command == 'compare':
                return self._handle_compare(args)
            elif args.command == 'vote':
                return self._handle_vote(args)
            elif args.command == 'stats':
                return self._handle_stats(args)
            else:
                print(f"❌ Tuntematon komento: {args.command}")
                return 1
        except Exception as e:
            print(f"❌ Odottamaton virhe: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    def _handle_compare(self, args):
        """Käsittele vertailu"""
        print(f"🔍 Käsitellään vertailua: {args.question_a} vs {args.question_b}")
        
        result = self.question_handler.handle_comparison(
            user_id=args.user_id,
            question_a_id=args.question_a,
            question_b_id=args.question_b,
            result=args.result,
            user_trust=args.user_trust
        )
        
        if result.get('success'):
            changes = result.get('changes', {})
            print("✅ Vertailu käsitelty onnistuneesti!")
            print(f"📊 Kysymys A: {changes.get('question_a', {}).get('old_rating')} → {changes.get('question_a', {}).get('new_rating')}")
            print(f"📊 Kysymys B: {changes.get('question_b', {}).get('old_rating')} → {changes.get('question_b', {}).get('new_rating')}")
            
            # Lokitus
            self.log_action(
                action_type="comparison_processed",
                description=f"Vertailu: {args.question_a} vs {args.question_b} - {args.result}",
                question_ids=[args.question_a, args.question_b],
                user_id=args.user_id,
                metadata={
                    "result": args.result,
                    "user_trust": args.user_trust,
                    "question_a_change": changes.get('question_a', {}).get('change'),
                    "question_b_change": changes.get('question_b', {}).get('change')
                }
            )
            return 0
        else:
            print(f"❌ Vertailu epäonnistui: {result.get('error')}")
            return 1
    
    def _handle_vote(self, args):
        """Käsittele ääni"""
        print(f"🗳️  Käsitellään ääntä: {args.vote_type} kysymykselle {args.question_id}")
        
        result = self.question_handler.handle_vote(
            user_id=args.user_id,
            question_id=args.question_id,
            vote_type=args.vote_type,
            confidence=args.confidence,
            user_trust=args.user_trust
        )
        
        if result.get('success'):
            change = result.get('change', {})
            print("✅ Ääni käsitelty onnistuneesti!")
            print(f"📊 Rating: {change.get('old_rating')} → {change.get('new_rating')}")
            
            # Lokitus
            self.log_action(
                action_type="vote_processed", 
                description=f"Ääni: {args.vote_type} kysymykselle {args.question_id}",
                question_ids=[args.question_id],
                user_id=args.user_id,
                metadata={
                    "vote_type": args.vote_type,
                    "confidence": args.confidence,
                    "user_trust": args.user_trust,
                    "rating_change": change.get('change')
                }
            )
            return 0
        else:
            print(f"❌ Äänestys epäonnistui: {result.get('error')}")
            return 1
    
    def _handle_stats(self, args):
        """Näytä kysymyksen tilastot"""
        print(f"📈 Haetaan tilastoja kysymykselle: {args.question_id}")
        
        result = self.question_handler.get_question_stats(args.question_id)
        
        if result.get('success'):
            print("✅ Kysymyksen tilastot:")
            print(f"   🔢 ID: {result.get('question_id')}")
            print(f"   📊 Nykyinen rating: {result.get('current_rating')}")
            print(f"   🎯 Perusrating: {result.get('base_rating')}")
            print(f"   ⚖️  Vertailumuutos: {result.get('comparison_delta')}")
            print(f"   🗳️  Äänimuutos: {result.get('vote_delta')}")
            print(f"   🔄 Vertailuja: {result.get('total_comparisons')}")
            print(f"   👍 Ääniä: {result.get('total_votes')} ({result.get('up_votes')}↑/{result.get('down_votes')}↓)")
            print(f"   📝 Esikatselu: {result.get('content_preview')}")
            return 0
        else:
            print(f"❌ Tilastojen haku epäonnistui: {result.get('error')}")
            return 1

if __name__ == "__main__":
    sys.exit(main_template(ELOManagerCLI))
