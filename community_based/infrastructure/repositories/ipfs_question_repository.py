#!/usr/bin/env python3
"""
IPFS Question Repository - LOPULLINEN KORJATTU VERSIO
"""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from datetime import timezone

from domain.repositories.question_repository import QuestionRepository
from domain.entities.question import Question
from domain.value_objects import QuestionId, QuestionContent, QuestionScale, CreationTimestamps

class IPFSQuestionRepository(QuestionRepository):
    """Question repository that stores questions in IPFS and local JSON cache"""
    
    def __init__(self, ipfs_client, block_manager=None, namespace: str = "default"):
        self.ipfs_client = ipfs_client
        self.block_manager = block_manager
        self.namespace = namespace
        self.questions_file = Path("runtime/ipfs_questions.json")
        self.questions_file.parent.mkdir(exist_ok=True)
        self._ensure_questions_file()
    
    def _ensure_questions_file(self):
        """Varmista että ipfs_questions.json tiedosto on olemassa"""
        if not self.questions_file.exists():
            # Luo tyhjä ipfs_questions.json tiedosto
            initial_data = {
                "metadata": {
                    "version": "2.0.0",
                    "created": datetime.now(timezone.utc).isoformat(),
                    "total_questions": 0,
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "ipfs_synced": False
                },
                "questions": []
            }
            
            with open(self.questions_file, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, indent=2, ensure_ascii=False)
    
    def _load_questions(self) -> List[Dict[str, Any]]:
        """Lataa kysymykset JSON-tiedostosta"""
        try:
            with open(self.questions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('questions', [])
        except Exception as e:
            print(f"❌ Virhe ladattaessa IPFS-kysymyksiä: {e}")
            return []
    
    def _save_questions(self, questions: List[Dict[str, Any]]):
        """Tallenna kysymykset JSON-tiedostoon"""
        try:
            data = {
                "metadata": {
                    "version": "2.0.0",
                    "created": datetime.now(timezone.utc).isoformat(),
                    "total_questions": len(questions),
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "ipfs_synced": True
                },
                "questions": questions
            }
            
            with open(self.questions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Virhe tallentaessa IPFS-kysymyksiä: {e}")
    
    def _dict_to_question(self, question_dict: Dict[str, Any]) -> Question:
        """Muunna dictionary Question-entiteetiksi"""
        return Question(
            question_id=QuestionId(question_dict.get('local_id', '')),
            content=QuestionContent(
                question=question_dict.get('content', {}).get('question', {}),
                category=question_dict.get('content', {}).get('category', {}),
                tags=question_dict.get('content', {}).get('tags', []),
                scale=question_dict.get('content', {}).get('scale', {})
            ),
            elo_rating=question_dict.get('elo_rating', {}),
            timestamps=CreationTimestamps(
                created=question_dict.get('timestamps', {}).get('created_local'),
                modified=question_dict.get('timestamps', {}).get('modified_local')
            ),
            metadata=question_dict.get('metadata', {})
        )
    
    def _question_to_dict(self, question: Question) -> Dict[str, Any]:
        """Muunna Question-entiteetti dictionaryksi"""
        return {
            "local_id": str(question.question_id),
            "source": "ipfs",
            "content": {
                "question": question.content.question,
                "category": question.content.category,
                "tags": question.content.tags,
                "scale": question.content.scale
            },
            "elo_rating": question.elo_rating,
            "timestamps": {
                "created_local": str(question.timestamps.created),
                "modified_local": str(question.timestamps.modified)
            },
            "metadata": question.metadata
        }
    
    def find_by_id(self, question_id: QuestionId) -> Optional[Question]:
        """Etsi kysymys ID:llä"""
        questions_data = self._load_questions()
        
        for question_dict in questions_data:
            if question_dict.get('local_id') == str(question_id):
                return self._dict_to_question(question_dict)
        
        return None
    
    def find_all(self) -> List[Question]:
        """Hae kaikki kysymykset"""
        questions_data = self._load_questions()
        return [self._dict_to_question(q) for q in questions_data]
    
    def save(self, question: Question) -> bool:
        """Tallenna kysymys"""
        try:
            questions_data = self._load_questions()
            
            # Tarkista onko kysymys jo olemassa
            existing_index = None
            for i, q_dict in enumerate(questions_data):
                if q_dict.get('local_id') == str(question.question_id):
                    existing_index = i
                    break
            
            question_dict = self._question_to_dict(question)
            
            if existing_index is not None:
                # Päivitä olemassa oleva kysymys
                questions_data[existing_index] = question_dict
            else:
                # Lisää uusi kysymys
                questions_data.append(question_dict)
            
            self._save_questions(questions_data)
            return True
            
        except Exception as e:
            print(f"❌ Virhe tallentaessa IPFS-kysymystä: {e}")
            return False
    
    def delete(self, question_id: QuestionId) -> bool:
        """Poista kysymys"""
        try:
            questions_data = self._load_questions()
            
            # Poista kysymys
            original_count = len(questions_data)
            questions_data = [q for q in questions_data if q.get('local_id') != str(question_id)]
            
            if len(questions_data) < original_count:
                self._save_questions(questions_data)
                return True
            else:
                return False  # Kysymystä ei löytynyt
                
        except Exception as e:
            print(f"❌ Virhe poistaessa IPFS-kysymystä: {e}")
            return False
    
    def count(self) -> int:
        """Laske kysymysten määrä"""
        questions_data = self._load_questions()
        return len(questions_data)
