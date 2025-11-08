#!/usr/bin/env python3
"""
Active Questions Manager - Hallitsee aktiivisia kysymyksiä vaaleihin
"""

import json
import sys
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Dict, List, Optional
import shutil

class ActiveQuestionsManager:
    """Hallinnoi aktiivisia kysymyksiä ja niiden synkronointia"""
    
    def __init__(self, runtime_dir: str = "runtime"):
        self.runtime_dir = Path(runtime_dir)
        self.base_file = self.runtime_dir / "active_questions.base.json"
        self.active_file = self.runtime_dir / "active_questions.json"
        self.questions_file = self.runtime_dir / "questions.json"
        
        # Varmista että base-template on olemassa
        self._ensure_base_template()
    
    def _ensure_base_template(self):
        """Varmista että base-template on olemassa"""
        if not self.base_file.exists():
            self._create_base_template()
    
    def _create_base_template(self):
        """Luo base-template tiedosto"""
        base_template = {
            "metadata": {
                "election_id": "default_election",
                "created": datetime.now(timezone.utc).isoformat(),
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "question_limit": 15,
                "min_rating": 800,
                "sync_enabled": True,
                "submission_locked": False
            },
            "sync_rules": {
                "auto_sync": True,
                "sync_interval_hours": 24,
                "max_questions": 15,
                "min_comparisons": 5,
                "min_votes": 3,
                "rating_weight": 0.7,
                "activity_weight": 0.3
            },
            "questions": []
        }
        
        with open(self.base_file, 'w', encoding='utf-8') as f:
            json.dump(base_template, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Luotu: {self.base_file}")
    
    def sync_active_questions(self, election_id: str = None) -> Dict:
        """
        Synkronoi parhaat kysymykset questions.json -> active_questions.json
        
        Args:
            election_id: Tietyn vaalin ID (jos None, käytä oletusta)
            
        Returns:
            Synkronoinnin tulos
        """
        try:
            # Lataa konfiguraatio
            with open(self.base_file, 'r', encoding='utf-8') as f:
                base_config = json.load(f)
            
            # Lataa kaikki kysymykset
            with open(self.questions_file, 'r', encoding='utf-8') as f:
                questions_data = json.load(f)
            
            # Suodata ja pisteytä kysymykset
            scored_questions = self._score_questions(
                questions_data.get('questions', []), 
                base_config['sync_rules']
            )
            
            # Valitse parhaat kysymykset
            selected_questions = self._select_top_questions(
                scored_questions, 
                base_config['sync_rules']['max_questions']
            )
            
            # Päivitä aktiiviset kysymykset
            active_data = {
                "metadata": {
                    **base_config["metadata"],
                    "election_id": election_id or base_config["metadata"]["election_id"],
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "total_questions": len(selected_questions),
                    "sync_timestamp": datetime.now(timezone.utc).isoformat()
                },
                "sync_rules": base_config["sync_rules"],
                "questions": selected_questions
            }
            
            # Tallenna
            with open(self.active_file, 'w', encoding='utf-8') as f:
                json.dump(active_data, f, indent=2, ensure_ascii=False)
            
            # Kirjaa system_chainiin
            self._log_sync_to_chain(len(selected_questions))
            
            return {
                "success": True,
                "synced_questions": len(selected_questions),
                "total_available": len(scored_questions),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def _score_questions(self, questions: List[Dict], rules: Dict) -> List[Dict]:
        """Pisteytä kysymykset valintakriteerien mukaan"""
        scored = []
        
        for question in questions:
            elo = question.get('elo_rating', {})
            
            # Perustarkistukset
            current_rating = elo.get('current_rating', 0)
            comparisons = elo.get('total_comparisons', 0)
            votes = elo.get('total_votes', 0)
            
            # Tarkista minimivaatimukset
            if (current_rating < rules.get('min_rating', 0) or 
                comparisons < rules.get('min_comparisons', 0) or
                votes < rules.get('min_votes', 0)):
                continue
            
            # Laske pistemäärä
            rating_score = (current_rating / 1000) * rules.get('rating_weight', 0.7)
            
            # Aktiviteettipisteet (vertailut + äänet)
            activity_score = min(
                (comparisons + votes) / 50,  # Normalisoi
                1.0
            ) * rules.get('activity_weight', 0.3)
            
            total_score = rating_score + activity_score
            
            scored.append({
                **question,
                "_score": total_score,
                "_rating_score": rating_score,
                "_activity_score": activity_score
            })
        
        return sorted(scored, key=lambda x: x['_score'], reverse=True)
    
    def _select_top_questions(self, scored_questions: List[Dict], max_questions: int) -> List[Dict]:
        """Valitse parhaat kysymykset"""
        selected = []
        
        for question in scored_questions[:max_questions]:
            # Poista laskentakentät
            clean_question = {k: v for k, v in question.items() if not k.startswith('_')}
            selected.append(clean_question)
        
        return selected
    
    def _log_sync_to_chain(self, question_count: int):
        """Kirjaa synkronointi system_chainiin"""
        try:
            from system_chain_manager import log_action
            log_action(
                action_type="active_questions_sync",
                description=f"Synkronoitu {question_count} aktiivista kysymystä",
                question_ids=[],
                user_id="active_questions_manager",
                metadata={"question_count": question_count}
            )
        except ImportError:
            pass  # System chain ei saatavilla
    
    def lock_submissions(self, election_id: str = None) -> bool:
        """Lukitse kysymysten lähettäminen"""
        try:
            with open(self.base_file, 'r', encoding='utf-8') as f:
                base_config = json.load(f)
            
            base_config["metadata"]["submission_locked"] = True
            base_config["metadata"]["lock_timestamp"] = datetime.now(timezone.utc).isoformat()
            base_config["metadata"]["election_id"] = election_id or base_config["metadata"]["election_id"]
            
            with open(self.base_file, 'w', encoding='utf-8') as f:
                json.dump(base_config, f, indent=2, ensure_ascii=False)
            
            # Kirjaa system_chainiin
            self._log_lock_to_chain()
            
            return True
            
        except Exception as e:
            print(f"❌ Lukitus epäonnistui: {e}")
            return False
    
    def unlock_submissions(self) -> bool:
        """Avaa kysymysten lähettäminen"""
        try:
            with open(self.base_file, 'r', encoding='utf-8') as f:
                base_config = json.load(f)
            
            base_config["metadata"]["submission_locked"] = False
            base_config["metadata"]["unlock_timestamp"] = datetime.now(timezone.utc).isoformat()
            
            with open(self.base_file, 'w', encoding='utf-8') as f:
                json.dump(base_config, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"❌ Avaus epäonnistui: {e}")
            return False
    
    def _log_lock_to_chain(self):
        """Kirjaa lukitus system_chainiin"""
        try:
            from system_chain_manager import log_action
            log_action(
                action_type="submissions_locked",
                description="Kysymysten lähettäminen lukittu",
                question_ids=[],
                user_id="active_questions_manager"
            )
        except ImportError:
            pass
    
    def get_status(self) -> Dict:
        """Hae aktiivisten kysymysten tila"""
        try:
            with open(self.base_file, 'r', encoding='utf-8') as f:
                base_config = json.load(f)
            
            active_count = 0
            if self.active_file.exists():
                with open(self.active_file, 'r', encoding='utf-8') as f:
                    active_data = json.load(f)
                    active_count = len(active_data.get('questions', []))
            
            return {
                "submission_locked": base_config["metadata"]["submission_locked"],
                "sync_enabled": base_config["metadata"]["sync_enabled"],
                "question_limit": base_config["metadata"]["question_limit"],
                "active_questions": active_count,
                "last_updated": base_config["metadata"]["last_updated"]
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def print_status(self):
        """Tulosta status"""
        status = self.get_status()
        
        print("\n🔒 AKTIIVISET KYSYMYKSET - TILA")
        print("=" * 50)
        
        if "error" in status:
            print(f"❌ Virhe: {status['error']}")
            return
        
        lock_status = "🔒 LUKITTU" if status['submission_locked'] else "🔓 AVOINNA"
        sync_status = "✅ KÄYTÖSSÄ" if status['sync_enabled'] else "❌ POIS KÄYTTÖSTÄ"
        
        print(f"Lähetyksen tila: {lock_status}")
        print(f"Synkronointi: {sync_status}")
        print(f"Kysymysraja: {status['question_limit']}")
        print(f"Aktiivisia kysymyksiä: {status['active_questions']}")
        print(f"Viimeisin päivitys: {status['last_updated'][:19]}")

def main():
    """Pääohjelma"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Aktiivisten kysymysten hallinta")
    parser.add_argument('action', choices=['sync', 'lock', 'unlock', 'status', 'init'],
                       help='Toiminto')
    parser.add_argument('--election-id', help='Vaalien ID')
    parser.add_argument('--runtime-dir', default='runtime', help='Runtime hakemisto')
    
    args = parser.parse_args()
    
    manager = ActiveQuestionsManager(args.runtime_dir)
    
    if args.action == 'init':
        print("✅ Base-template varmistettu")
        
    elif args.action == 'sync':
        result = manager.sync_active_questions(args.election_id)
        if result['success']:
            print(f"✅ Synkronoitu {result['synced_questions']} kysymystä")
        else:
            print(f"❌ Synkronointi epäonnistui: {result['error']}")
            
    elif args.action == 'lock':
        if manager.lock_submissions(args.election_id):
            print("✅ Kysymysten lähettäminen lukittu")
        else:
            print("❌ Lukitus epäonnistui")
            
    elif args.action == 'unlock':
        if manager.unlock_submissions():
            print("✅ Kysymysten lähettäminen avattu")
        else:
            print("❌ Avaus epäonnistui")
            
    elif args.action == 'status':
        manager.print_status()

if __name__ == "__main__":
    main()
