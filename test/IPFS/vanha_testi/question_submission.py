# question_submission.py
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from difflib import SequenceMatcher

class QuestionSubmission:
    def __init__(self, ipfs, election_manager):
        self.ipfs = ipfs
        self.election_manager = election_manager
    
    def validate_question(self, question_data: Dict[str, Any]) -> List[str]:
        """Validoi kysymyksen ja palauttaa mahdolliset virheet"""
        errors = []
        
        # Tarkista pakolliset kentät
        if not question_data.get('question', {}).get('fi'):
            errors.append("Kysymyksen teksti (suomeksi) on pakollinen")
        
        if not question_data.get('tags', {}).get('fi'):
            errors.append("Vähintään yksi tagi on pakollinen")
        elif len(question_data['tags']['fi']) == 0:
            errors.append("Vähintään yksi tagi on pakollinen")
        
        # Tarkista asteikon pakollisuus ja kelvollisuus
        if 'scale' not in question_data:
            errors.append("Asteikko on pakollinen")
        else:
            scale = question_data.get('scale', {})
            if scale.get('min', 0) >= scale.get('max', 0):
                errors.append("Asteikon minimin tulee olla pienempi kuin maksimin")
            if scale.get('min') is None or scale.get('max') is None:
                errors.append("Asteikon min ja max arvot ovat pakollisia")
        
        return errors
    
    def find_similar_questions(self, question_text: str, tags: List[str], similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Etsii vastaavia kysymyksiä tekstin ja tagien perusteella"""
        all_questions = self.election_manager.get_all_questions()
        similar_questions = []
        
        for question in all_questions:
            similarity_score = self._calculate_similarity(
                question_text, 
                question.get('question', {}).get('fi', '')
            )
            
            # Tarkista tagien yhteensopivuus
            tag_overlap = self._calculate_tag_overlap(
                tags, 
                question.get('tags', {}).get('fi', [])
            )
            
            # Yhdistetty pistemäärä
            combined_score = (similarity_score * 0.7) + (tag_overlap * 0.3)
            
            if combined_score >= similarity_threshold:
                similar_questions.append({
                    'question': question,
                    'similarity_score': combined_score,
                    'text_similarity': similarity_score,
                    'tag_overlap': tag_overlap
                })
        
        # Järjestä parhaimman vastaavuuden mukaan
        return sorted(similar_questions, key=lambda x: x['similarity_score'], reverse=True)
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Laskee kahden tekstin välisen samankaltaisuuden"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def _calculate_tag_overlap(self, tags1: List[str], tags2: List[str]) -> float:
        """Laskee tagien päällekkäisyyden"""
        if not tags1 or not tags2:
            return 0.0
        
        set1 = set(tag.lower() for tag in tags1)
        set2 = set(tag.lower() for tag in tags2)
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def get_available_tags(self) -> List[str]:
        """Palauttaa kaikki käytössä olevat tagit"""
        all_questions = self.election_manager.get_all_questions()
        tags = set()
        
        for question in all_questions:
            tags.update(question.get('tags', {}).get('fi', []))
        
        return sorted(list(tags))
    
    def submit_question(self, question_data: Dict[str, Any], force: bool = False) -> Dict[str, Any]:
        """Lähettää uuden kysymyksen tarkistuksen jälkeen"""
        # Validoi kysymys
        errors = self.validate_question(question_data)
        if errors:
            return {
                'success': False,
                'errors': errors,
                'similar_questions': []
            }
        
        # Etsi vastaavat kysymykset
        question_text = question_data['question']['fi']
        tags = question_data['tags']['fi']
        
        similar_questions = self.find_similar_questions(question_text, tags)
        
        # Jos löytyy vastaavia eikä käyttäjä pakota lähetystä
        if similar_questions and not force:
            return {
                'success': False,
                'errors': ["Löytyi vastaavia kysymyksiä. Tarkista alla olevat."],
                'similar_questions': similar_questions,
                'requires_force': True
            }
        
        # Lisää kysymys
        try:
            # Generoi UUID ID
            all_questions = self.election_manager.get_all_questions()
            existing_ids = [q.get('id') for q in all_questions if q.get('id')]
            
            # Käytä UUID:a ID:nä
            new_id = str(uuid.uuid4())
            question_data['id'] = new_id
            
            # Lisää timestamp
            question_data['submission_timestamp'] = datetime.now().isoformat()
            question_data['status'] = 'pending'
            
            # Lähetä kysymys
            cid = self.election_manager.add_question(question_data, is_official=False)
            
            return {
                'success': True,
                'cid': cid,
                'question_id': new_id,
                'similar_questions': []
            }
            
        except Exception as e:
            return {
                'success': False,
                'errors': [f"Lähetys epäonnistui: {str(e)}"],
                'similar_questions': []
            }

class QuestionSearch:
    """Kysymysten hakutoiminnallisuus sumealla haulla"""
    
    def __init__(self, election_manager):
        self.election_manager = election_manager
    
    def search_questions(self, query: str = None, tags: List[str] = None, category: str = None, similarity_threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Hakee kysymyksiä hakusanan, tagien tai kategorian perusteella sumealla haulla"""
        all_questions = self.election_manager.get_all_questions()
        results = []
        
        for question in all_questions:
            score = 0
            
            # SUMEA HAKU: Tekstin perusteella
            if query:
                text = question.get('question', {}).get('fi', '')
                # Tarkista tarkka osuma
                if query.lower() in text.lower():
                    score += 2
                else:
                    # Sumea samankaltaisuus
                    similarity = self._calculate_similarity(query, text)
                    if similarity > similarity_threshold:
                        score += int(similarity * 2)  # Painotettu pistemäärä
            
            # Haku tagien perusteella
            if tags:
                question_tags = [tag.lower() for tag in question.get('tags', {}).get('fi', [])]
                search_tags = [tag.lower() for tag in tags]
                if any(tag in question_tags for tag in search_tags):
                    score += 2
            
            # Haku kategorian perusteella
            if category:
                question_category = question.get('category', {}).get('fi', '').lower()
                if category.lower() in question_category:
                    score += 1
            
            if score > 0:
                results.append({
                    'question': question,
                    'relevance_score': score,
                    'matched_by': self._get_match_reason(score, query, tags, category)
                })
        
        # Järjestä relevanssin mukaan
        return sorted(results, key=lambda x: x['relevance_score'], reverse=True)
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Laskee kahden tekstin välisen samankaltaisuuden (sama kuin QuestionSubmissionissa)"""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def _get_match_reason(self, score: int, query: str, tags: List[str], category: str) -> List[str]:
        """Palauttaa listan syistä miksi kysymys vastasi hakua"""
        reasons = []
        
        if query and score >= 2:
            reasons.append("tekstihaku")
        if tags and score >= 2:
            reasons.append("tagit")
        if category and score >= 1:
            reasons.append("kategoria")
        
        return reasons
    
    def fuzzy_search(self, query: str, threshold: float = 0.3) -> List[Dict[str, Any]]:
        """Puhdas sumea haku ilman muita suodattimia"""
        all_questions = self.election_manager.get_all_questions()
        results = []
        
        for question in all_questions:
            text = question.get('question', {}).get('fi', '')
            similarity = self._calculate_similarity(query, text)
            
            if similarity > threshold:
                results.append({
                    'question': question,
                    'similarity_score': similarity,
                    'matched_by': ['sumea haku']
                })
        
        return sorted(results, key=lambda x: x['similarity_score'], reverse=True)
