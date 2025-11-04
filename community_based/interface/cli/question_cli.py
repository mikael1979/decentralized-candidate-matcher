#!/usr/bin/env python3
"""
Question CLI - Command-line interface for question management using new architecture
"""

import argparse
import sys
from typing import Optional

from core.dependency_container import get_container
from infrastructure.services.legacy_integration import LegacyIntegrationService
from application.commands import (
    SubmitQuestionCommand, SyncQuestionsCommand, 
    ProcessComparisonCommand, ProcessVoteCommand
)
from application.queries import (
    GetQuestionStatusQuery, GetActiveQuestionsQuery,
    GetQuestionStatsQuery, FindQuestionsQuery
)
from domain.value_objects import MultilingualText, Category, Scale, UserId

class QuestionCLI:
    """Command-line interface for question management"""
    
    def __init__(self, runtime_dir: str = "runtime"):
        self.runtime_dir = runtime_dir
        self.container = get_container(runtime_dir=runtime_dir)
        self.integration = LegacyIntegrationService(runtime_dir)
        
        # Initialize system
        self.container.initialize()
    
    def handle_submit(self, args) -> int:
        """Handle question submission"""
        try:
            # Create multilingual content
            content = MultilingualText(
                fi=args.question_fi,
                en=args.question_en or args.question_fi,
                sv=args.question_sv or args.question_fi
            )
            
            # Create category
            category = Category(
                name=MultilingualText(
                    fi=args.category_fi,
                    en=args.category_en or args.category_fi,
                    sv=args.category_sv or args.category_fi
                )
            )
            
            # Create scale
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
            
            # Create command
            command = SubmitQuestionCommand(
                content=content,
                category=category,
                scale=scale,
                submitted_by=UserId(args.user_id),
                tags=args.tags.split(",") if args.tags else [],
                metadata={
                    "source": "cli",
                    "category_custom": args.category_fi
                }
            )
            
            # Execute use case
            result = self.container.question_service.submit_question(command)
            
            if result.success:
                print(f"✅ Question submitted successfully!")
                print(f"   Question ID: {result.data['question_id']}")
                print(f"   Queue position: {result.data['queue_position']}")
                
                if result.data['auto_synced']:
                    print(f"   🔄 Auto-synced to new questions")
                
                return 0
            else:
                print(f"❌ Failed to submit question: {result.message}")
                return 1
                
        except Exception as e:
            print(f"❌ Error submitting question: {e}")
            return 1
    
    def handle_sync(self, args) -> int:
        """Handle question synchronization"""
        try:
            command = SyncQuestionsCommand(
                sync_type=args.sync_type,
                batch_size=args.batch_size,
                force=args.force,
                requested_by=UserId("cli_user")
            )
            
            result = self.container.question_service.sync_questions(command)
            
            if result.success:
                print(f"✅ Sync completed successfully!")
                print(f"   Synced: {result.data['synced_count']} questions")
                print(f"   Remaining: {result.data['remaining_count']} questions")
                print(f"   Type: {result.data['sync_type']}")
                
                if result.data.get('batch_id'):
                    print(f"   Batch ID: {result.data['batch_id']}")
                
                return 0
            else:
                print(f"❌ Sync failed: {result.message}")
                return 1
                
        except Exception as e:
            print(f"❌ Error during sync: {e}")
            return 1
    
    def handle_status(self, args) -> int:
        """Handle status query"""
        try:
            query = GetQuestionStatusQuery(
                election_id=args.election_id,
                include_stats=True
            )
            
            result = self.container.question_service.get_question_status(query)
            
            if result.success:
                data = result.data
                print("\n📊 QUESTION SYSTEM STATUS")
                print("=" * 50)
                print(f"Temporary questions: {data.get('temporary_questions', 0)}")
                print(f"New questions: {data.get('new_questions', 0)}")
                print(f"Active questions: {data.get('active_questions', 0)}")
                print(f"Total questions: {data.get('total_questions', 0)}")
                print(f"Average rating: {data.get('average_rating', 0):.1f}")
                
                # Show recent activity if available
                recent = data.get('recent_activity', {})
                if recent:
                    print(f"\n📈 RECENT ACTIVITY (24h)")
                    print(f"   Questions modified: {recent.get('questions_modified_24h', 0)}")
                
                return 0
            else:
                print(f"❌ Failed to get status: {result.error}")
                return 1
                
        except Exception as e:
            print(f"❌ Error getting status: {e}")
            return 1
    
    def handle_migrate(self, args) -> int:
        """Handle legacy migration"""
        try:
            print("🔄 Starting legacy migration...")
            
            result = self.integration.migrate_legacy_questions()
            
            if result["success"]:
                stats = result["stats"]
                print(f"✅ Migration completed!")
                print(f"   Files processed: {stats['files_processed']}")
                print(f"   Questions migrated: {stats['total_migrated']}")
                
                if stats['errors']:
                    print(f"   Errors: {len(stats['errors'])}")
                
                return 0
            else:
                print(f"❌ Migration failed: {result['error']}")
                return 1
                
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            return 1
    
    def handle_system_status(self, args) -> int:
        """Handle system status query"""
        try:
            status = self.container.get_system_status()
            
            print("\n🔧 SYSTEM STATUS")
            print("=" * 50)
            
            # Dependencies status
            print("📦 DEPENDENCIES:")
            deps = status["dependencies"]
            for dep_name, available in deps.items():
                status_icon = "✅" if available else "❌"
                print(f"   {status_icon} {dep_name}: {available}")
            
            # Configuration
            print(f"\n⚙️  CONFIGURATION:")
            config = status["configuration"]
            for key, value in config.items():
                print(f"   {key}: {value}")
            
            # Repository stats
            if "repository_stats" in status:
                repo_stats = status["repository_stats"]
                print(f"\n💾 REPOSITORY:")
                print(f"   Total questions: {repo_stats.get('total_questions', 0)}")
                print(f"   Average rating: {repo_stats.get('average_rating', 0):.1f}")
                print(f"   Storage type: {repo_stats.get('storage_type', 'unknown')}")
            
            # IPFS stats
            if "ipfs_stats" in status:
                ipfs_stats = status["ipfs_stats"]
                print(f"\n🌐 IPFS:")
                print(f"   Client type: {ipfs_stats.get('client_type', 'unknown')}")
                print(f"   CIDs stored: {ipfs_stats.get('total_cids', 0)}")
                print(f"   Uploads: {ipfs_stats.get('upload_count', 0)}")
            
            return 0
            
        except Exception as e:
            print(f"❌ Error getting system status: {e}")
            return 1


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Question Management CLI")
    parser.add_argument('--runtime-dir', default='runtime', help='Runtime directory')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Submit command
    submit_parser = subparsers.add_parser('submit', help='Submit a new question')
    submit_parser.add_argument('--question-fi', required=True, help='Question text (Finnish)')
    submit_parser.add_argument('--question-en', help='Question text (English)')
    submit_parser.add_argument('--question-sv', help='Question text (Swedish)')
    submit_parser.add_argument('--category-fi', required=True, help='Category (Finnish)')
    submit_parser.add_argument('--category-en', help='Category (English)')
    submit_parser.add_argument('--category-sv', help='Category (Swedish)')
    submit_parser.add_argument('--user-id', required=True, help='User ID')
    submit_parser.add_argument('--tags', help='Comma-separated tags')
    
    # Sync command
    sync_parser = subparsers.add_parser('sync', help='Sync questions')
    sync_parser.add_argument('--sync-type', choices=['tmp_to_new', 'new_to_main', 'update_active'], 
                           required=True, help='Sync type')
    sync_parser.add_argument('--batch-size', type=int, help='Batch size')
    sync_parser.add_argument('--force', action='store_true', help='Force sync')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Get system status')
    status_parser.add_argument('--election-id', help='Election ID')
    
    # Migrate command
    subparsers.add_parser('migrate', help='Migrate from legacy system')
    
    # System status command
    subparsers.add_parser('system-status', help='Get detailed system status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        cli = QuestionCLI(runtime_dir=args.runtime_dir)
        
        if args.command == 'submit':
            return cli.handle_submit(args)
        elif args.command == 'sync':
            return cli.handle_sync(args)
        elif args.command == 'status':
            return cli.handle_status(args)
        elif args.command == 'migrate':
            return cli.handle_migrate(args)
        elif args.command == 'system-status':
            return cli.handle_system_status(args)
        else:
            print(f"Unknown command: {args.command}")
            return 1
            
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
