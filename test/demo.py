#!/usr/bin/env python3
"""
Final Improved Decentralized Candidate Matcher - Python Version
"""

import json
import os
import hashlib
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

class FinalJSONEditor:
    def __init__(self, data_dir: str = "test_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.loaded_data = {}
        
        # Default configuration
        self.default_elo_rating = 1500
        self.k_factor = 32
        self.auto_block_threshold = 0.7
        self.auto_block_min_votes = 10
        self.community_approval_threshold = 0.8
        
        self.default_files = {
            'meta.json': {
                "system": "Decentralized Candidate Matcher",
                "version": "1.0.0",
                "election": {
                    "id": "test_election_2024",
                    "country": "FI",
                    "type": "test",
                    "name": {"fi": "Test Vaalit 2024", "en": "Test Election 2024"},
                    "date": "2024-01-01",
                    "language": "fi"
                },
                "community_moderation": {
                    "enabled": True,
                    "thresholds": {
                        "auto_block_inappropriate": self.auto_block_threshold,
                        "auto_block_min_votes": self.auto_block_min_votes,
                        "community_approval": self.community_approval_threshold
                    }
                },
                "admins": [
                    {
                        "admin_id": "admin_1",
                        "public_key": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIadmin1",
                        "name": "Test Admin",
                        "role": "super_admin"
                    }
                ],
                "content": {}
            },
            'questions.json': {
                "election_id": "test_election_2024",
                "language": "fi",
                "questions": [
                    {
                        "id": 1,
                        "category": {
                            "fi": "Ympäristö",
                            "en": "Environment"
                        },
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
                        },
                        "elo_rating": {
                            "rating": 1500,
                            "total_matches": 0,
                            "wins": 0,
                            "losses": 0,
                            "last_updated": datetime.now().isoformat()
                        }
                    }
                ]
            },
            'newquestions.json': {
                "election_id": "test_election_2024",
                "language": "fi",
                "question_type": "user_submitted",
                "questions": []
            },
            'candidates.json': {
                "election_id": "test_election_2024",
                "language": "fi",
                "candidates": [
                    {
                        "id": 1,
                        "name": "Matti Meikäläinen",
                        "party": "Test Puolue",
                        "district": "Helsinki",
                        "public_key": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIcandidate1",
                        "key_fingerprint": "SHA256:candidate1",
                        "answer_cid": "test_data/answers/candidate_1.json"
                    }
                ]
            },
            'community_votes.json': {
                "election_id": "test_election_2024",
                "language": "fi",
                "question_votes": [],
                "user_votes": []
            }
        }
        
        # Counter for unique IDs
        self._id_counter = int(time.time() * 1000)
    
    def _generate_unique_id(self) -> str:
        """Generate truly unique ID with counter"""
        self._id_counter += 1
        return f"user_{self._id_counter}"
    
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
    
    def write_json(self, filename: str, data: Dict, create_backup: bool = True) -> bool:
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
            print(f"✓ Successfully wrote {filename}")
            return True
                
        except Exception as e:
            print(f"❌ Error writing {filename}: {e}")
            return False
    
    def create_default_file(self, filename: str) -> Dict:
        """Create default file structure"""
        default_data = self.default_files.get(filename, {})
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
        
        # Check for duplicate question IDs
        all_questions = self._get_all_questions()
        question_ids = [q['id'] for q in all_questions]
        if len(question_ids) != len(set(question_ids)):
            errors.append("Duplicate question IDs found")
        
        if not errors:
            print('✓ All data consistency checks passed')
            return True
        else:
            print('❌ Data consistency errors:')
            for error in errors:
                print(f"  - {error}")
            return False
    
    def _get_all_questions(self) -> List[Dict]:
        """Get all questions from both files"""
        all_questions = []
        for filename in ['questions.json', 'newquestions.json']:
            data = self.loaded_data.get(filename)
            if data and 'questions' in data:
                all_questions.extend(data['questions'])
        return all_questions
    
    def add_user_question(self, question_data: Dict) -> Optional[Dict]:
        """Add a new user-submitted question"""
        newquestions = self.loaded_data.get('newquestions.json')
        if not newquestions:
            print('❌ newquestions.json not loaded')
            return None
        
        # Generate truly unique ID
        question_id = self._generate_unique_id()
        
        # Create new question
        new_question = {
            'id': question_id,
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
                'rating': self.default_elo_rating,
                'total_matches': 0,
                'wins': 0,
                'losses': 0,
                'last_updated': datetime.now().isoformat()
            }
        }
        
        newquestions['questions'].append(new_question)
        question_text = new_question['question'].get('fi', 'New question')
        print(f"✓ Added question: {question_text[:50]}... (ID: {question_id})")
        return new_question
    
    def add_community_vote(self, question_id: str, vote_data: Dict) -> Optional[Dict]:
        """Add a community moderation vote"""
        votes_file = self.loaded_data.get('community_votes.json')
        if not votes_file:
            print('❌ community_votes.json not loaded')
            return None
        
        vote_id = f'vote_{self._generate_unique_id()}'
        
        vote = {
            'vote_id': vote_id,
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
        question_stats = None
        for q in votes_file['question_votes']:
            if q['question_id'] == question_id:
                question_stats = q
                break
        
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
        
        question = None
        for q in newquestions['questions']:
            if q['id'] == question_id:
                question = q
                break
        
        if not question:
            return
        
        # Update community moderation info
        if 'community_moderation' not in question:
            question['community_moderation'] = {}
        
        confidence = max(stats['appropriate_votes'], stats['inappropriate_votes']) / stats['total_votes']
        question['community_moderation'].update({
            'votes_received': stats['total_votes'],
            'inappropriate_ratio': stats['inappropriate_ratio'],
            'confidence_score': confidence,
            'last_vote_update': datetime.now().isoformat()
        })
        
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
    
    def update_elo_rating(self, question_a_id: str, question_b_id: str, winner: str):
        """Update Elo ratings after a question match"""
        print(f'\n🎯 Updating Elo ratings: {question_a_id} vs {question_b_id}')
        
        # Find questions in both files
        question_a = self._find_question(question_a_id)
        question_b = self._find_question(question_b_id)
        
        if not question_a or not question_b:
            print('✗ Questions not found for Elo update')
            return
        
        if question_a_id == question_b_id:
            print('✗ Cannot compare question with itself')
            return
        
        k_factor = self.k_factor
        
        # Calculate expected scores
        expected_a = 1 / (1 + 10 ** ((question_b['elo_rating']['rating'] - question_a['elo_rating']['rating']) / 400))
        expected_b = 1 / (1 + 10 ** ((question_a['elo_rating']['rating'] - question_b['elo_rating']['rating']) / 400))
        
        # Determine scores
        if winner == 'question_a':
            score_a, score_b = 1, 0
        elif winner == 'question_b':
            score_a, score_b = 0, 1
        else:
            score_a, score_b = 0.5, 0.5
        
        # Calculate rating changes
        change_a = round(k_factor * (score_a - expected_a))
        change_b = round(k_factor * (score_b - expected_b))
        
        # Update question A
        old_rating_a = question_a['elo_rating']['rating']
        question_a['elo_rating']['rating'] = old_rating_a + change_a
        question_a['elo_rating']['total_matches'] += 1
        if score_a == 1:
            question_a['elo_rating']['wins'] += 1
        elif score_a == 0:
            question_a['elo_rating']['losses'] += 1
        question_a['elo_rating']['last_updated'] = datetime.now().isoformat()
        
        # Update question B
        old_rating_b = question_b['elo_rating']['rating']
        question_b['elo_rating']['rating'] = old_rating_b + change_b
        question_b['elo_rating']['total_matches'] += 1
        if score_b == 1:
            question_b['elo_rating']['wins'] += 1
        elif score_b == 0:
            question_b['elo_rating']['losses'] += 1
        question_b['elo_rating']['last_updated'] = datetime.now().isoformat()
        
        print(f"✓ Elo updated:")
        print(f"  {question_a_id}: {old_rating_a} → {question_a['elo_rating']['rating']} ({change_a:+d})")
        print(f"  {question_b_id}: {old_rating_b} → {question_b['elo_rating']['rating']} ({change_b:+d})")
    
    def _find_question(self, question_id: str) -> Optional[Dict]:
        """Find question in either questions.json or newquestions.json"""
        # Try to find in newquestions first
        newquestions = self.loaded_data.get('newquestions.json')
        if newquestions:
            for question in newquestions['questions']:
                if question['id'] == question_id:
                    return question
        
        # Try to find in official questions
        questions = self.loaded_data.get('questions.json')
        if questions:
            for question in questions['questions']:
                if str(question['id']) == question_id:  # Handle both string and int IDs
                    return question
        
        return None
    
    def search_questions(self, query: str, field: str = 'question') -> List[Dict]:
        """Search questions by content with improved search"""
        all_questions = self._get_all_questions()
        
        results = []
        query_lower = query.lower()
        
        for question in all_questions:
            field_value = question.get(field, {})
            if isinstance(field_value, dict):
                # Search in all language versions
                for lang_text in field_value.values():
                    text_lower = str(lang_text).lower()
                    # Basic search
                    if query_lower in text_lower:
                        results.append(question)
                        break
                    # Handle Finnish word forms for common search terms
                    elif self._finnish_word_match(query_lower, text_lower):
                        results.append(question)
                        break
        
        return results
    
    def _finnish_word_match(self, query: str, text: str) -> bool:
        """Handle Finnish word forms for better search"""
        word_forms = {
            'kaupunkipyörä': ['kaupunkipyörä', 'kaupunkipyörät', 'kaupunkipyörän', 'kaupunkipyörien', 'kaupunkipyöriä'],
            'pyörä': ['pyörä', 'pyörät', 'pyörän', 'pyörien', 'pyöriä'],
            'bussi': ['bussi', 'bussit', 'bussin', 'bussien', 'busseja'],
            'juna': ['juna', 'junat', 'junan', 'junien', 'junia'],
            'koulu': ['koulu', 'koulut', 'koulun', 'koulujen', 'kouluja'],
            'terveys': ['terveys', 'terveyden', 'terveyttä'],
            'sairaala': ['sairaala', 'sairaalat', 'sairaalan', 'sairaaloiden', 'sairaaloita']
        }
        
        for base_word, forms in word_forms.items():
            if query in forms:
                return any(form in text for form in forms)
        
        return False
    
    def search_questions_by_tag(self, tag: str) -> List[Dict]:
        """Search questions by tag"""
        all_questions = self._get_all_questions()
        
        results = []
        tag_lower = tag.lower()
        
        for question in all_questions:
            tags = question.get('tags', {})
            for lang_tags in tags.values():
                if any(tag_lower == t.lower() for t in lang_tags):
                    results.append(question)
                    break
        
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
        all_questions = self._get_all_questions()
        
        rated_questions = [
            q for q in all_questions 
            if q.get('elo_rating', {}).get('rating')
        ]
        
        rated_questions.sort(key=lambda x: x['elo_rating']['rating'], reverse=True)
        
        return [
            {
                'id': q['id'],
                'question': q['question'].get('fi', 'Unknown'),
                'rating': q['elo_rating']['rating'],
                'matches': q['elo_rating']['total_matches'],
                'win_rate': q['elo_rating']['wins'] / max(q['elo_rating']['total_matches'], 1)
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

def run_final_demo():
    print("🚀 Decentralized Candidate Matcher - Final Improved Demo\n")
    
    # Initialize editor
    editor = FinalJSONEditor()
    
    # Load all data
    if not editor.load_all_data():
        print("⚠️  Some files failed to load, but continuing with demo...")
    
    # Validate consistency
    editor.validate_data_consistency()
    
    # Display initial stats
    editor.display_stats()
    
    # Demo: Add diverse user questions
    print('\n' + '='*50)
    print("📝 DEMO: Adding Diverse User Questions")
    print('='*50)
    
    demo_questions = [
        {
            'category': {'fi': 'Liikenne', 'en': 'Transportation'},
            'question': {
                'fi': 'Pitäisikö kaupunkipyörien määrää lisätä kesäkaudella?',
                'en': 'Should the number of city bikes be increased during summer season?'
            },
            'scale': {
                'min': -5, 'max': 5,
                'labels': {'fi': {'-5': 'Täysin eri mieltä', '0': 'Neutraali', '5': 'Täysin samaa mieltä'}}
            },
            'tags': {'fi': ['liikenne', 'kaupunkipyörät', 'kesä']},
            'user_comment': 'Kesäkaudella pyöräily on suosittua'
        },
        {
            'category': {'fi': 'Koulutus', 'en': 'Education'},
            'question': {
                'fi': 'Pitäisikö kaupungin tarjota ilmaisia ohjelmointikursseja nuorille?',
                'en': 'Should the city offer free programming courses for youth?'
            },
            'scale': {
                'min': -5, 'max': 5,
                'labels': {'fi': {'-5': 'Täysin eri mieltä', '0': 'Neutraali', '5': 'Täysin samaa mieltä'}}
            },
            'tags': {'fi': ['koulutus', 'ohjelmointi', 'nuoriso']},
            'user_comment': 'Digitaidot ovat tärkeitä tulevaisuuden työelämää varten'
        },
        {
            'category': {'fi': 'Terveys', 'en': 'Health'},
            'question': {
                'fi': 'Pitäisikö terveyskeskusten aukioloaikoja pidentää iltaan asti?',
                'en': 'Should health center opening hours be extended until evening?'
            },
            'scale': {
                'min': -5, 'max': 5,
                'labels': {'fi': {'-5': 'Täysin eri mieltä', '0': 'Neutraali', '5': 'Täysin samaa mieltä'}}
            },
            'tags': {'fi': ['terveys', 'terveyskeskukset', 'aukioloajat']},
            'user_comment': 'Pitäisi olla palvelut saatavilla myös työaikojen jälkeen'
        }
    ]
    
    added_questions = []
    for i, q_data in enumerate(demo_questions):
        question = editor.add_user_question(q_data)
        if question:
            added_questions.append(question)
            # Add small delay to ensure unique timestamps
            time.sleep(0.01)
    
    if len(added_questions) >= 2:
        # Demo: Add community votes
        print('\n' + '='*50)
        print("🗳️ DEMO: Community Voting")
        print('='*50)
        
        # Add votes for first question (city bikes)
        editor.add_community_vote(added_questions[0]['id'], {
            'vote': 'appropriate',
            'confidence': 0.8,
            'reasons': ['relevant', 'constructive'],
            'comments': 'Hyvä kysymys, liittyy ajankohtaiseen aiheeseen'
        })
        
        editor.add_community_vote(added_questions[0]['id'], {
            'vote': 'appropriate', 
            'confidence': 0.9,
            'reasons': ['clear_question', 'factual'],
            'comments': 'Erittäin hyvin muotoiltu kysymys'
        })
        
        editor.add_community_vote(added_questions[0]['id'], {
            'vote': 'inappropriate',
            'confidence': 0.3,
            'reasons': ['off_topic'],
            'comments': 'Ei liity tarpeeksi kunnallispolitiikkaan'
        })
        
        # Demo: Elo rating update
        print('\n' + '='*50)
        print("🎯 DEMO: Elo Rating System")
        print('='*50)
        
        # Compare different types of questions
        editor.update_elo_rating(added_questions[0]['id'], added_questions[1]['id'], 'question_a')  # bikes vs programming
        editor.update_elo_rating(added_questions[0]['id'], '1', 'question_a')  # bikes vs environment
        
        # Demo: Add more votes to trigger auto-moderation
        print('\n' + '='*50)
        print("🤖 DEMO: Auto-Moderation")
        print('='*50)
        
        for i in range(8):
            editor.add_community_vote(added_questions[0]['id'], {
                'vote': 'appropriate',
                'confidence': 0.7 + (i * 0.03),
                'reasons': ['relevant', 'constructive']
            })
    
    # Demo: Search functionality
    print('\n' + '='*50)
    print("🔍 DEMO: Search Functionality")
    print('='*50)
    
    # Search by content - now with improved Finnish word matching
    search_terms = ['kaupunkipyörä', 'ohjelmointi', 'terveys']
    
    for term in search_terms:
        search_results = editor.search_questions(term)
        print(f"Found {len(search_results)} questions about '{term}':")
        for q in search_results:
            status = q.get('community_moderation', {}).get('status', 'pending')
            print(f"  - {q['question']['fi']} ({status})")
        print()
    
    # Search by tag
    tag_results = editor.search_questions_by_tag('liikenne')
    print(f"Found {len(tag_results)} questions with tag 'liikenne':")
    for q in tag_results:
        status = q.get('community_moderation', {}).get('status', 'pending')
        print(f"  - {q['question']['fi']} ({status})")
    
    # Demo: Generate report
    print('\n' + '='*50)
    print("📈 DEMO: System Report")
    print('='*50)
    
    report = editor.generate_report()
    print("System Report:")
    print(f"- Total questions: {report['summary']['total_official_questions'] + report['summary']['total_user_questions']}")
    print(f"- Total votes: {report['summary']['total_votes']}")
    print(f"- Question statuses: {report['user_questions_by_status']}")
    print(f"- Vote distribution: {report['vote_distribution']}")
    print(f"- Average Elo rating: {report['average_elo']}")
    
    if report['top_questions']:
        print("\nTop Rated Questions:")
        for i, q in enumerate(report['top_questions'], 1):
            win_rate = f"{q['win_rate']:.1%}" if q['matches'] > 0 else "N/A"
            print(f"  {i}. {q['question'][:40]}... (Elo: {q['rating']}, Win Rate: {win_rate})")
    
    # Save all data
    print('\n' + '='*50)
    print("💾 DEMO: Saving Data")
    print('='*50)
    
    if editor.save_all_data():
        print("🎉 Demo completed successfully!")
        
        # Final validation
        print('\n' + '='*50)
        print("🔍 Final Data Validation")
        print('='*50)
        editor.validate_data_consistency()
        
        # Display final stats
        editor.display_stats()
    else:
        print("❌ Some files failed to save")

if __name__ == "__main__":
    run_final_demo()
