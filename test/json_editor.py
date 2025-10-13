import json
import os
import hashlib
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

from config import config
from models import *

class JSONEditor:
    def __init__(self, data_dir: str = config.DATA_DIR):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.loaded_data: Dict[str, Any] = {}
        
    def calculate_hash(self, data: Dict) -> str:
        """Calculate SHA256 hash of data excluding integrity field"""
        data_copy = data.copy()
        if 'integrity' in data_copy:
            del data_copy['integrity']
        
        # Sort keys for consistent hashing
        json_str = json.dumps(data_copy, sort_keys=True, separators=(',', ':'))
        return f"sha256:{hashlib.sha256(json_str.encode()).hexdigest()}"
    
    def update_integrity(self, data: Dict) -> Dict:
        """Update integrity hash in data"""
        hash_value = self.calculate_hash(data)
        data['integrity'] = {
            'algorithm': 'sha256',
            'hash': hash_value,
            'computed': datetime.now().isoformat()
        }
        return data
    
    def read_json(self, filename: str) -> Optional[Dict]:
        """Read JSON file with error handling"""
        try:
            filepath = self.data_dir / filename
            if not filepath.exists():
                print(f"⚠️  File {filename} not found, creating default")
                return self.create_default_file(filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.loaded_data[filename] = data
                return data
                
        except Exception as e:
            print(f"❌ Error reading {filename}: {e}")
            return None
    
    def write_json(self, filename: str, data: Dict, create_backup: bool = config.BACKUP_ENABLED) -> bool:
        """Write JSON file with backup option"""
        try:
            filepath = self.data_dir / filename
            
            # Create backup
            if create_backup and filepath.exists():
                backup_path = filepath.with_suffix(f'.backup-{int(datetime.now().timestamp())}.json')
                shutil.copy2(filepath, backup_path)
            
            # Write file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.loaded_data[filename] = data
            
            # Verify write
            verify_data = self.read_json(filename)
            if verify_data and self.calculate_hash(data) == self.calculate_hash(verify_data):
                print(f"✓ Successfully wrote {filename}")
                return True
            else:
                print(f"❌ Write verification failed for {filename}")
                return False
                
        except Exception as e:
            print(f"❌ Error writing {filename}: {e}")
            return False
    
    def create_default_file(self, filename: str) -> Dict:
        """Create default file structure"""
        default_data = config.DEFAULT_FILES.get(filename, {})
        if default_data:
            self.write_json(filename, self.update_integrity(default_data), False)
        return default_data
    
    def load_all_data(self) -> bool:
        """Load all JSON files"""
        print("📁 Loading all JSON files...")
        
        files = ['meta.json', 'questions.json', 'newquestions.json', 'candidates.json', 'community_votes.json']
        success_count = 0
        
        for filename in files:
            data = self.read_json(filename)
            if data is not None:
                success_count += 1
            else:
                print(f"⚠️  Failed to load: {filename}")
        
        print(f"✓ Loaded {success_count}/{len(files)} files successfully")
        return success_count == len(files)
    
    def save_all_data(self) -> bool:
        """Save all loaded data with updated integrity hashes"""
        print("\n💾 Saving all JSON files...")
        
        success_count = 0
        for filename, data in self.loaded_data.items():
            updated_data = self.update_integrity(data)
            if self.write_json(filename, updated_data):
                success_count += 1
        
        print(f"✓ Saved {success_count}/{len(self.loaded_data)} files successfully")
        return success_count == len(self.loaded_data)
    
    def validate_data_consistency(self) -> bool:
        """Validate consistency across all loaded data"""
        print('\n🔍 Validating data consistency...')
        errors = []
        
        # Check election IDs
        election_ids = set()
        for filename, data in self.loaded_data.items():
            if 'election_id' in data:
                election_ids.add(data['election_id'])
        
        if len(election_ids) > 1:
            errors.append(f"Multiple election IDs found: {', '.join(election_ids)}")
        
        # Validate integrity hashes
        for filename, data in self.loaded_data.items():
            if 'integrity' in data:
                computed_hash = self.calculate_hash(data)
                if computed_hash != data['integrity']['hash']:
                    errors.append(f"Integrity hash mismatch in {filename}")
        
        if not errors:
            print('✓ All data consistency checks passed')
            return True
        else:
            print('❌ Data consistency errors:')
            for error in errors:
                print(f"  - {error}")
            return False
    
    def add_user_question(self, question_data: Dict) -> Optional[Dict]:
        """Add a new user-submitted question"""
        newquestions = self.loaded_data.get('newquestions.json')
        if not newquestions:
            print('❌ newquestions.json not loaded')
            return None
        
        # Required fields validation
        required_fields = ['category', 'question', 'scale']
        missing_fields = [field for field in required_fields if field not in question_data]
        if missing_fields:
            print(f'❌ Missing required fields: {", ".join(missing_fields)}')
            return None
        
        # Create new question
        new_question = {
            'id': f'user_{int(datetime.now().timestamp() * 1000)}',
            'original_id': len(newquestions['questions']) + 1001,
            **question_data,
            'submission': {
                'user_public_key': question_data.get('user_public_key', f'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIuser_{int(datetime.now().timestamp())}'),
                'timestamp': datetime.now().isoformat(),
                'status': 'pending',
                'upvotes': 0,
                'downvotes': 0,
                'user_comment': question_data.get('user_comment', '')
            },
            'moderation': {
                'moderated': False,
                'approved': None,
                'blocked': False
            },
            'community_moderation': {
                'status': 'pending',
                'votes_received': 0,
                'inappropriate_ratio': 0.0,
                'confidence_score': 0.0,
                'community_approved': False,
                'auto_moderated': False,
                'requires_admin_review': False
            },
            'elo_rating': {
                'rating': config.DEFAULT_ELO_RATING,
                'total_matches': 0,
                'wins': 0,
                'losses': 0,
                'last_updated': datetime.now().isoformat()
            }
        }
        
        newquestions['questions'].append(new_question)
        question_text = new_question['question'].get('fi', 'New question')
        print(f"✓ Added question: {question_text[:50]}...")
        return new_question
    
    def add_community_vote(self, question_id: str, vote_data: Dict) -> Optional[Dict]:
        """Add a community moderation vote"""
        votes_file = self.loaded_data.get('community_votes.json')
        if not votes_file:
            print('❌ community_votes.json not loaded')
            return None
        
        vote = {
            'vote_id': f'vote_{int(datetime.now().timestamp() * 1000)}',
            'question_id': question_id,
            'voter_public_key': vote_data.get('voter_public_key', f'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIvoter_{int(datetime.now().timestamp())}'),
            'vote': vote_data['vote'],  # 'appropriate' or 'inappropriate'
            'confidence': vote_data.get('confidence', 0.5),
            'reasons': vote_data.get('reasons', []),
            'comments': vote_data.get('comments', ''),
            'timestamp': datetime.now().isoformat(),
            'voter_trust_score': vote_data.get('voter_trust_score', 0.5)
        }
        
        votes_file['user_votes'].append(vote)
        self._update_question_vote_stats(question_id, vote)
        
        print(f"✓ Added {vote['vote']} vote for question {question_id}")
        return vote
    
    def _update_question_vote_stats(self, question_id: str, vote: Dict):
        """Update question vote statistics"""
        votes_file = self.loaded_data['community_votes.json']
        
        # Find or create question stats
        question_stats = next((q for q in votes_file['question_votes'] if q['question_id'] == question_id), None)
        if not question_stats:
            question_stats = {
                'question_id': question_id,
                'total_votes': 0,
                'appropriate_votes': 0,
                'inappropriate_votes': 0,
                'inappropriate_ratio': 0.0,
                'confidence_score': 0.0,
                'status': 'pending',
                'auto_moderated': False,
                'last_updated': datetime.now().isoformat()
            }
            votes_file['question_votes'].append(question_stats)
        
        # Update stats
        question_stats['total_votes'] += 1
        if vote['vote'] == 'appropriate':
            question_stats['appropriate_votes'] += 1
        else:
            question_stats['inappropriate_votes'] += 1
        
        question_stats['inappropriate_ratio'] = question_stats['inappropriate_votes'] / question_stats['total_votes']
        question_stats['last_updated'] = datetime.now().isoformat()
        
        # Update question moderation status
        self._update_question_moderation_status(question_id, question_stats)
    
    def _update_question_moderation_status(self, question_id: str, stats: Dict):
        """Update question moderation status based on vote statistics"""
        newquestions = self.loaded_data.get('newquestions.json')
        if not newquestions:
            return
        
        question = next((q for q in newquestions['questions'] if q['id'] == question_id), None)
        if not question:
            return
        
        # Update community moderation info
        question['community_moderation'] = {
            **question.get('community_moderation', {}),
            'votes_received': stats['total_votes'],
            'inappropriate_ratio': stats['inappropriate_ratio'],
            'confidence_score': max(stats['appropriate_votes'], stats['inappropriate_votes']) / stats['total_votes'],
            'last_vote_update': datetime.now().isoformat()
        }
        
        # Auto-moderation logic
        thresholds = self.loaded_data['meta.json']['community_moderation']['thresholds']
        if stats['total_votes'] >= thresholds['auto_block_min_votes']:
            if stats['inappropriate_ratio'] >= thresholds['auto_block_inappropriate']:
                question['community_moderation'].update({
                    'status': 'blocked',
                    'auto_moderated': True,
                    'requires_admin_review': True
                })
                question['submission']['status'] = 'blocked'
                question['moderation']['blocked'] = True
                print(f"🚫 Question {question_id} auto-blocked by community")
            elif stats['inappropriate_ratio'] <= (1 - thresholds['community_approval']):
                question['community_moderation'].update({
                    'status': 'approved',
                    'community_approved': True,
                    'auto_moderated': True
                })
                question['submission']['status'] = 'approved'
                question['moderation']['approved'] = True
                print(f"✅ Question {question_id} auto-approved by community")
    
    def update_elo_rating(self, question_id: str, opponent_id: str, winner: str):
        """Update Elo ratings after a question match"""
        print('\n🎯 Updating Elo ratings...')
        
        # Find questions in both files
        question = self._find_question(question_id)
        opponent = self._find_question(opponent_id)
        
        if not question or not opponent:
            print('✗ Questions not found for Elo update')
            return
        
        k_factor = config.K_FACTOR
        
        # Calculate expected scores
        expected_a = 1 / (1 + 10 ** ((opponent['elo_rating']['rating'] - question['elo_rating']['rating']) / 400))
        expected_b = 1 / (1 + 10 ** ((question['elo_rating']['rating'] - opponent['elo_rating']['rating']) / 400))
        
        # Determine scores
        if winner == 'question_a':
            score_a, score_b = 1, 0
        elif winner == 'question_b':
            score_a, score_b = 0, 1
        else:
            score_a, score_b = 0.5, 0.5
        
        # Calculate new ratings
        new_rating_a = round(question['elo_rating']['rating'] + k_factor * (score_a - expected_a))
        new_rating_b = round(opponent['elo_rating']['rating'] + k_factor * (score_b - expected_b))
        
        # Update question A
        question['elo_rating']['rating'] = new_rating_a
        question['elo_rating']['total_matches'] += 1
        if score_a == 1:
            question['elo_rating']['wins'] += 1
        elif score_a == 0:
            question['elo_rating']['losses'] += 1
        question['elo_rating']['last_updated'] = datetime.now().isoformat()
        
        # Update opponent
        opponent['elo_rating']['rating'] = new_rating_b
        opponent['elo_rating']['total_matches'] += 1
        if score_b == 1:
            opponent['elo_rating']['wins'] += 1
        elif score_b == 0:
            opponent['elo_rating']['losses'] += 1
        opponent['elo_rating']['last_updated'] = datetime.now().isoformat()
        
        print(f"✓ Elo updated: {question_id} {new_rating_a} (+{new_rating_a - question['elo_rating']['rating']}), "
              f"{opponent_id} {new_rating_b} ({new_rating_b - opponent['elo_rating']['rating']})")
    
    def _find_question(self, question_id: str) -> Optional[Dict]:
        """Find question in either questions.json or newquestions.json"""
        for filename in ['questions.json', 'newquestions.json']:
            data = self.loaded_data.get(filename)
            if data:
                question = next((q for q in data['questions'] if q['id'] == question_id), None)
                if question:
                    return question
        return None
    
    def search_questions(self, query: str, field: str = 'question') -> List[Dict]:
        """Search questions by content"""
        all_questions = []
        for filename in ['questions.json', 'newquestions.json']:
            data = self.loaded_data.get(filename)
            if data and 'questions' in data:
                all_questions.extend(data['questions'])
        
        results = []
        for question in all_questions:
            field_value = question.get(field, {})
            if isinstance(field_value, dict):
                # Search in all language versions
                for lang_text in field_value.values():
                    if query.lower() in str(lang_text).lower():
                        results.append(question)
                        break
            elif query.lower() in str(field_value).lower():
                results.append(question)
        
        return results
    
    def generate_report(self) -> Dict:
        """Generate system statistics report"""
        questions = self.loaded_data.get('questions.json', {}).get('questions', [])
        user_questions = self.loaded_data.get('newquestions.json', {}).get('questions', [])
        votes = self.loaded_data.get('community_votes.json', {}).get('user_votes', [])
        candidates = self.loaded_data.get('candidates.json', {}).get('candidates', [])
        
        # Status counts
        status_counts = {}
        for q in user_questions:
            status = q.get('community_moderation', {}).get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Vote distribution
        vote_distribution = {}
        for vote in votes:
            vote_type = vote['vote']
            vote_distribution[vote_type] = vote_distribution.get(vote_type, 0) + 1
        
        return {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_official_questions': len(questions),
                'total_user_questions': len(user_questions),
                'total_candidates': len(candidates),
                'total_votes': len(votes)
            },
            'user_questions_by_status': status_counts,
            'vote_distribution': vote_distribution,
            'average_elo': self._calculate_average_elo(questions + user_questions),
            'top_questions': self._get_top_rated_questions(5)
        }
    
    def _calculate_average_elo(self, questions: List[Dict]) -> float:
        """Calculate average Elo rating"""
        rated_questions = [q for q in questions if q.get('elo_rating', {}).get('rating')]
        if not rated_questions:
            return 0.0
        
        total = sum(q['elo_rating']['rating'] for q in rated_questions)
        return round(total / len(rated_questions))
    
    def _get_top_rated_questions(self, limit: int = 10) -> List[Dict]:
        """Get top rated questions by Elo"""
        all_questions = []
        for filename in ['questions.json', 'newquestions.json']:
            data = self.loaded_data.get(filename)
            if data:
                all_questions.extend(data['questions'])
        
        rated_questions = [
            q for q in all_questions 
            if q.get('elo_rating', {}).get('rating') and q['elo_rating']['total_matches'] > 0
        ]
        
        rated_questions.sort(key=lambda x: x['elo_rating']['rating'], reverse=True)
        
        return [
            {
                'id': q['id'],
                'question': q['question'].get('fi', 'Unknown'),
                'rating': q['elo_rating']['rating'],
                'matches': q['elo_rating']['total_matches'],
                'win_rate': q['elo_rating']['wins'] / q['elo_rating']['total_matches']
            }
            for q in rated_questions[:limit]
        ]
    
    def display_stats(self):
        """Display system statistics"""
        questions = self.loaded_data.get('questions.json', {}).get('questions', [])
        user_questions = self.loaded_data.get('newquestions.json', {}).get('questions', [])
        candidates = self.loaded_data.get('candidates.json', {}).get('candidates', [])
        votes = self.loaded_data.get('community_votes.json', {}).get('user_votes', [])
        
        print('\n📊 System Statistics:')
        print(f"- Official questions: {len(questions)}")
        print(f"- User questions: {len(user_questions)}")
        print(f"- Candidates: {len(candidates)}")
        print(f"- Community votes: {len(votes)}")
        
        if user_questions:
            print('\nUser Questions:')
            for q in user_questions:
                status = q.get('community_moderation', {}).get('status', 'pending')
                votes_received = q.get('community_moderation', {}).get('votes_received', 0)
                elo = q.get('elo_rating', {}).get('rating', 1500)
                question_text = q['question'].get('fi', 'Unknown')[:30]
                print(f"  {q['id']}: \"{question_text}...\" | {status} | Votes: {votes_received} | Elo: {elo}")
