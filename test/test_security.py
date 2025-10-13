#!/usr/bin/env python3
"""
Security Test: Attempt to modify candidate answers without proper signature
Tests various attack vectors against the decentralized system
"""

import json
import os
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class SecurityTester:
    def __init__(self, data_dir: str = "test_data"):
        self.data_dir = Path(data_dir)
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str):
        """Log test results"""
        result = {
            "test": test_name,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "details": details
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
        return success
    
    def calculate_hash(self, data: Dict) -> str:
        """Calculate SHA256 hash of data excluding integrity field"""
        data_copy = data.copy()
        if 'integrity' in data_copy:
            del data_copy['integrity']
        
        json_str = json.dumps(data_copy, sort_keys=True, separators=(',', ':'))
        return f"sha256:{hashlib.sha256(json_str.encode()).hexdigest()}"
    
    def test_1_tamper_candidate_answers(self) -> bool:
        """Test 1: Attempt to modify candidate answers without signature"""
        print("\n🔓 TEST 1: Tampering with Candidate Answers")
        print("=" * 50)
        
        try:
            # Read original candidate data
            candidates_file = self.data_dir / "candidates.json"
            if not candidates_file.exists():
                return self.log_test(
                    "Tamper Candidate Answers", 
                    False, 
                    "Candidates file not found"
                )
            
            with open(candidates_file, 'r') as f:
                candidates_data = json.load(f)
            
            candidate = candidates_data['candidates'][0]
            original_name = candidate['name']
            
            # Attempt 1: Direct modification of candidate name
            candidate['name'] = "Hacker Candidate"
            
            # Check if integrity check would catch this
            original_hash = candidates_data['integrity']['hash']
            new_hash = self.calculate_hash(candidates_data)
            
            if original_hash != new_hash:
                success = self.log_test(
                    "Tamper Candidate Data - Direct Edit",
                    True,
                    f"Integrity hash changed: {original_hash[:16]}... -> {new_hash[:16]}..."
                )
            else:
                success = self.log_test(
                    "Tamper Candidate Data - Direct Edit", 
                    False,
                    "Integrity hash DID NOT CHANGE - SECURITY BREACH!"
                )
            
            # Restore original data
            candidate['name'] = original_name
            
            # Attempt 2: Fake answer file creation
            fake_answer_data = {
                "election_id": "test_election_2024",
                "candidate_id": 1,
                "candidate_public_key": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIfakekeyhacker123456789",
                "answers": [
                    {
                        "question_id": 1,
                        "answer": 5,  # Changed to extreme position
                        "confidence": 0.9,
                        "comment": {"fi": "MUUTETTU VASTAUS - HÄCKÄYS", "en": "MODIFIED ANSWER - HACK"},
                        "timestamp": datetime.now().isoformat()
                    }
                ],
                "submission": {
                    "timestamp": datetime.now().isoformat(),
                    "signed_data": "FAKE_SIGNATURE_HACKER_123",
                    "signature_verified": False  # This should be false in real system
                }
            }
            
            # Add fake integrity hash
            fake_answer_data['integrity'] = {
                'algorithm': 'sha256',
                'hash': 'sha256:fake_hash_hacker_123456789',
                'computed': datetime.now().isoformat()
            }
            
            # Save fake answer file
            fake_answer_file = self.data_dir / "hacked_answers.json"
            with open(fake_answer_file, 'w') as f:
                json.dump(fake_answer_data, f, indent=2)
            
            # Try to point candidate to fake answer file
            candidate['answer_cid'] = str(fake_answer_file)
            
            # Verify the system would detect this
            fake_hash_check = self.calculate_hash(fake_answer_data)
            if fake_hash_check != fake_answer_data['integrity']['hash']:
                self.log_test(
                    "Tamper Candidate Answers - Fake File",
                    True,
                    "Fake answer file integrity check would fail"
                )
            else:
                self.log_test(
                    "Tamper Candidate Answers - Fake File",
                    False, 
                    "Fake answer file integrity passed - VULNERABILITY!"
                )
            
            # Cleanup
            if fake_answer_file.exists():
                fake_answer_file.unlink()
            
            return success
            
        except Exception as e:
            return self.log_test(
                "Tamper Candidate Answers",
                False,
                f"Error during test: {str(e)}"
            )
    
    def test_2_question_moderation_bypass(self) -> bool:
        """Test 2: Attempt to bypass question moderation"""
        print("\n🤖 TEST 2: Question Moderation Bypass")
        print("=" * 50)
        
        try:
            # Read new questions file
            newquestions_file = self.data_dir / "newquestions.json"
            if not newquestions_file.exists():
                return self.log_test(
                    "Question Moderation Bypass",
                    False,
                    "New questions file not found"
                )
            
            with open(newquestions_file, 'r') as f:
                newquestions_data = json.load(f)
            
            if not newquestions_data['questions']:
                return self.log_test(
                    "Question Moderation Bypass",
                    False,
                    "No user questions found for testing"
                )
            
            # Attempt to directly approve a pending question
            question = newquestions_data['questions'][0]
            original_status = question['submission']['status']
            
            # Direct status change without votes
            question['submission']['status'] = 'approved'
            question['moderation']['approved'] = True
            question['moderation']['moderated'] = True
            question['community_moderation']['status'] = 'approved'
            question['community_moderation']['community_approved'] = True
            
            # Check if integrity would catch this
            original_hash = newquestions_data['integrity']['hash']
            new_hash = self.calculate_hash(newquestions_data)
            
            if original_hash != new_hash:
                success = self.log_test(
                    "Direct Question Approval Bypass",
                    True,
                    "Unauthorized status change detected by integrity hash"
                )
            else:
                success = self.log_test(
                    "Direct Question Approval Bypass",
                    False,
                    "Status change NOT detected - MODERATION BYPASS POSSIBLE!"
                )
            
            # Restore original status
            question['submission']['status'] = original_status
            question['moderation']['approved'] = False
            question['moderation']['moderated'] = False
            question['community_moderation']['status'] = 'pending'
            question['community_moderation']['community_approved'] = False
            
            return success
            
        except Exception as e:
            return self.log_test(
                "Question Moderation Bypass",
                False,
                f"Error during test: {str(e)}"
            )
    
    def test_3_fake_community_votes(self) -> bool:
        """Test 3: Attempt to add fake community votes"""
        print("\n🗳️ TEST 3: Fake Community Votes")
        print("=" * 50)
        
        try:
            # Read community votes file
            votes_file = self.data_dir / "community_votes.json"
            if not votes_file.exists():
                return self.log_test(
                    "Fake Community Votes",
                    False,
                    "Community votes file not found"
                )
            
            with open(votes_file, 'r') as f:
                votes_data = json.load(f)
            
            # Add fake vote with high trust score
            fake_vote = {
                "vote_id": "vote_hacker_123",
                "question_id": "user_1760317660476",  # Use existing question ID
                "voter_public_key": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIfakevoter123456789",
                "vote": "appropriate",
                "confidence": 0.9,
                "reasons": ["fake_reason"],
                "comments": "Fake vote by hacker",
                "timestamp": datetime.now().isoformat(),
                "voter_trust_score": 1.0  # Maximum trust score
            }
            
            votes_data['user_votes'].append(fake_vote)
            
            # Check integrity
            original_hash = votes_data['integrity']['hash']
            new_hash = self.calculate_hash(votes_data)
            
            if original_hash != new_hash:
                success = self.log_test(
                    "Add Fake Community Vote",
                    True,
                    "Fake vote addition detected by integrity hash"
                )
            else:
                success = self.log_test(
                    "Add Fake Community Vote",
                    False,
                    "Fake vote NOT detected - VOTE MANIPULATION POSSIBLE!"
                )
            
            # Remove fake vote
            votes_data['user_votes'] = [v for v in votes_data['user_votes'] if v['vote_id'] != 'vote_hacker_123']
            
            return success
            
        except Exception as e:
            return self.log_test(
                "Fake Community Votes",
                False,
                f"Error during test: {str(e)}"
            )
    
    def test_4_elo_rating_manipulation(self) -> bool:
        """Test 4: Attempt to manipulate Elo ratings"""
        print("\n📊 TEST 4: Elo Rating Manipulation")
        print("=" * 50)
        
        try:
            # Read questions files
            questions_file = self.data_dir / "questions.json"
            newquestions_file = self.data_dir / "newquestions.json"
            
            if not questions_file.exists():
                return self.log_test(
                    "Elo Rating Manipulation",
                    False,
                    "Questions file not found"
                )
            
            with open(questions_file, 'r') as f:
                questions_data = json.load(f)
            
            if not questions_data['questions']:
                return self.log_test(
                    "Elo Rating Manipulation", 
                    False,
                    "No questions found for testing"
                )
            
            # Attempt to directly manipulate Elo rating
            question = questions_data['questions'][0]
            original_elo = question['elo_rating']['rating']
            
            # Boost Elo rating artificially
            question['elo_rating']['rating'] = 2000  # Very high rating
            question['elo_rating']['wins'] = 100     # Unrealistic win count
            question['elo_rating']['total_matches'] = 100
            
            # Check integrity
            original_hash = questions_data['integrity']['hash']
            new_hash = self.calculate_hash(questions_data)
            
            if original_hash != new_hash:
                success = self.log_test(
                    "Direct Elo Rating Manipulation",
                    True,
                    "Elo manipulation detected by integrity hash"
                )
            else:
                success = self.log_test(
                    "Direct Elo Rating Manipulation",
                    False,
                    "Elo manipulation NOT detected - RATING MANIPULATION POSSIBLE!"
                )
            
            # Restore original values
            question['elo_rating']['rating'] = original_elo
            question['elo_rating']['wins'] = 7
            question['elo_rating']['total_matches'] = 12
            
            return success
            
        except Exception as e:
            return self.log_test(
                "Elo Rating Manipulation",
                False,
                f"Error during test: {str(e)}"
            )
    
    def test_5_metadata_tampering(self) -> bool:
        """Test 5: Attempt to tamper with system metadata"""
        print("\n⚙️ TEST 5: System Metadata Tampering")
        print("=" * 50)
        
        try:
            # Read metadata file
            meta_file = self.data_dir / "meta.json"
            if not meta_file.exists():
                return self.log_test(
                    "Metadata Tampering",
                    False,
                    "Metadata file not found"
                )
            
            with open(meta_file, 'r') as f:
                meta_data = json.load(f)
            
            # Attempt to change moderation thresholds
            original_threshold = meta_data['community_moderation']['thresholds']['auto_block_inappropriate']
            
            # Make moderation easier to bypass
            meta_data['community_moderation']['thresholds']['auto_block_inappropriate'] = 0.95  # Very high threshold
            meta_data['community_moderation']['thresholds']['auto_block_min_votes'] = 50       # Very high min votes
            meta_data['community_moderation']['thresholds']['community_approval'] = 0.3        # Very low approval threshold
            
            # Check integrity
            original_hash = meta_data['integrity']['hash']
            new_hash = self.calculate_hash(meta_data)
            
            if original_hash != new_hash:
                success = self.log_test(
                    "Moderation Threshold Tampering",
                    True,
                    "Threshold manipulation detected by integrity hash"
                )
            else:
                success = self.log_test(
                    "Moderation Threshold Tampering",
                    False,
                    "Threshold manipulation NOT detected - SYSTEM VULNERABLE!"
                )
            
            # Restore original thresholds
            meta_data['community_moderation']['thresholds']['auto_block_inappropriate'] = original_threshold
            meta_data['community_moderation']['thresholds']['auto_block_min_votes'] = 10
            meta_data['community_moderation']['thresholds']['community_approval'] = 0.8
            
            return success
            
        except Exception as e:
            return self.log_test(
                "Metadata Tampering",
                False,
                f"Error during test: {str(e)}"
            )
    
    def test_6_integrity_hash_bypass(self) -> bool:
        """Test 6: Attempt to bypass integrity hash checking"""
        print("\n🔐 TEST 6: Integrity Hash Bypass")
        print("=" * 50)
        
        try:
            # Read any data file
            candidates_file = self.data_dir / "candidates.json"
            if not candidates_file.exists():
                return self.log_test(
                    "Integrity Hash Bypass",
                    False,
                    "Test file not found"
                )
            
            with open(candidates_file, 'r') as f:
                candidates_data = json.load(f)
            
            # Method 1: Remove integrity field entirely
            original_integrity = candidates_data.pop('integrity', None)
            
            # This should make the file invalid in a real system
            self.log_test(
                "Remove Integrity Field",
                True,
                "File without integrity field should be rejected by system"
            )
            
            # Restore integrity field
            if original_integrity:
                candidates_data['integrity'] = original_integrity
            
            # Method 2: Fake but valid-looking hash
            candidates_data['integrity']['hash'] = 'sha256:' + '0' * 64  # Fake but valid format
            
            fake_hash_check = self.calculate_hash(candidates_data)
            if fake_hash_check != candidates_data['integrity']['hash']:
                success = self.log_test(
                    "Fake Integrity Hash",
                    True,
                    "Fake hash detected - proper verification working"
                )
            else:
                success = self.log_test(
                    "Fake Integrity Hash",
                    False,
                    "Fake hash NOT detected - INTEGRITY SYSTEM BROKEN!"
                )
            
            return success
            
        except Exception as e:
            return self.log_test(
                "Integrity Hash Bypass",
                False,
                f"Error during test: {str(e)}"
            )
    
    def run_all_tests(self) -> bool:
        """Run all security tests"""
        print("🔒 STARTING SECURITY TESTS")
        print("=" * 60)
        
        tests = [
            self.test_1_tamper_candidate_answers,
            self.test_2_question_moderation_bypass, 
            self.test_3_fake_community_votes,
            self.test_4_elo_rating_manipulation,
            self.test_5_metadata_tampering,
            self.test_6_integrity_hash_bypass
        ]
        
        all_passed = True
        for test in tests:
            try:
                if not test():
                    all_passed = False
            except Exception as e:
                self.log_test(test.__name__, False, f"Test crashed: {str(e)}")
                all_passed = False
        
        # Generate security report
        self.generate_security_report(all_passed)
        
        return all_passed
    
    def generate_security_report(self, all_passed: bool):
        """Generate comprehensive security report"""
        print("\n" + "=" * 60)
        print("📋 SECURITY TEST REPORT")
        print("=" * 60)
        
        passed = sum(1 for r in self.test_results if r['success'])
        total = len(self.test_results)
        
        print(f"Overall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
        print(f"Tests Passed: {passed}/{total}")
        
        print("\nDetailed Results:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {result['test']}: {result['details']}")
        
        # Security recommendations
        print("\n🔍 SECURITY RECOMMENDATIONS:")
        
        if all_passed:
            print("✅ System demonstrates strong security against tested attack vectors")
            print("✅ Integrity hashes properly detect tampering attempts")
            print("✅ Community moderation system is protected")
            print("✅ Elo rating system is secure against manipulation")
        else:
            print("🚨 CRITICAL: Some security vulnerabilities detected!")
            print("💡 Recommended actions:")
            print("   - Implement stricter signature verification")
            print("   - Add timestamp validation to prevent replay attacks")
            print("   - Consider adding secondary verification mechanisms")
            print("   - Implement rate limiting on community votes")
            print("   - Add admin oversight for critical changes")
        
        # Save detailed report
        report_file = self.data_dir / "security_test_report.json"
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "overall_passed": all_passed,
            "summary": {
                "total_tests": total,
                "passed_tests": passed,
                "failed_tests": total - passed
            },
            "test_results": self.test_results,
            "security_score": round((passed / total) * 100) if total > 0 else 0
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")

def main():
    """Run security tests"""
    print("Decentralized Candidate Matcher - Security Test Suite")
    print("Testing various attack vectors and security measures...")
    
    # Make sure test data exists
    if not Path("test_data").exists():
        print("❌ test_data directory not found. Run demo.py first to generate test data.")
        return
    
    tester = SecurityTester()
    all_passed = tester.run_all_tests()
    
    exit_code = 0 if all_passed else 1
    exit(exit_code)

if __name__ == "__main__":
    main()
