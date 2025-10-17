# search_engine.py
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

class SearchEngine:
    """
    Hakualgoritmi joka löytää parhaat ehdokkaat käyttäjän vastausten perusteella
    """
    
    def __init__(self, ipfs, election_manager):
        self.ipfs = ipfs
        self.election_manager = election_manager
    
    def find_matching_candidates(self, user_answers: Dict[str, int], top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Etsii parhaiten vastaavat ehdokkaat
        
        Args:
            user_answers: {question_id: answer} käyttäjän vastaukset
            top_n: Kuinka monta parasta ehdokasta palautetaan
        
        Returns:
            Lista ehdokkaista match_percentage ja match_details kenttinä
        """
        print(f"🔍 Etsitään ehdokkaita {len(user_answers)} vastauksen perusteella...")
        
        # Hae kaikki ehdokkaat
        candidates_data = self.election_manager.get_election_data("candidates.json")
        if not candidates_data:
            print("❌ Ehdokkaita ei löytynyt")
            return []
        
        matches = []
        
        for candidate in candidates_data.get("candidates", []):
            # Hae ehdokkaan vastaukset
            candidate_answers = self._get_candidate_answers(candidate)
            if not candidate_answers:
                continue
            
            # Laske yhteensopivuus
            match_result = self._calculate_match(user_answers, candidate_answers)
            
            matches.append({
                "candidate": candidate,
                "match_percentage": match_result["percentage"],
                "match_score": match_result["score"],
                "max_possible_score": match_result["max_possible_score"],
                "matched_questions": match_result["matched_questions"],
                "match_details": match_result["details"]
            })
        
        # Järjestä parhaimman yhteensopivuuden mukaan
        matches.sort(key=lambda x: x["match_percentage"], reverse=True)
        
        # Palauta top_n parasta
        top_matches = matches[:top_n]
        
        print(f"✅ Löydetty {len(top_matches)} ehdokasta")
        return top_matches
    
    def _get_candidate_answers(self, candidate: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Hakee ehdokkaan vastaukset"""
        if "answer_cid" not in candidate:
            return None
        
        return self.ipfs.get_json(candidate["answer_cid"])
    
    def _calculate_match(self, user_answers: Dict[str, int], candidate_answers: Dict[str, Any]) -> Dict[str, Any]:
        """
        Laskee käyttäjän ja ehdokkaan vastausten yhteensopivuuden
        
        Käyttää kaavaa: 5 - abs(user_answer - candidate_answer)
        Maksimipisteet per kysymys: 5
        """
        total_score = 0
        max_possible_score = len(user_answers) * 5
        matched_questions = 0
        details = []
        
        for q_id, user_answer in user_answers.items():
            candidate_answer = self._find_candidate_answer(candidate_answers, q_id)
            
            if candidate_answer is not None:
                # Laske samankaltaisuus (-5 - 5 asteikolla)
                distance = abs(candidate_answer - user_answer)
                similarity = 5 - distance  # 0-10 asteikolla
                score = max(0, similarity)  # Varmistetaan ettei mene negatiiviseksi
                
                total_score += score
                matched_questions += 1
                
                details.append({
                    "question_id": q_id,
                    "user_answer": user_answer,
                    "candidate_answer": candidate_answer,
                    "similarity": similarity,
                    "score": score
                })
            else:
                # Ehdokas ei vastannut tähän kysymykseen
                details.append({
                    "question_id": q_id,
                    "user_answer": user_answer,
                    "candidate_answer": None,
                    "similarity": 0,
                    "score": 0
                })
        
        # Laske prosenttiosuus
        percentage = (total_score / max_possible_score) * 100 if max_possible_score > 0 else 0
        
        return {
            "score": total_score,
            "max_possible_score": max_possible_score,
            "percentage": percentage,
            "matched_questions": matched_questions,
            "details": details
        }
    
    def _find_candidate_answer(self, candidate_answers: Dict[str, Any], question_id: str) -> Optional[int]:
        """Etsii ehdokkaan vastauksen tiettyyn kysymykseen"""
        for answer in candidate_answers.get("answers", []):
            # Tarkista sekä string että int muodot
            if (str(answer.get("question_id")) == str(question_id) or 
                answer.get("question_id") == question_id):
                return answer.get("answer")
        return None
    
    def get_question_text(self, question_id: str) -> str:
        """Hakee kysymystekstin ID:llä"""
        # Hae viralliset kysymykset
        questions_data = self.election_manager.get_election_data("questions.json")
        if questions_data:
            for q in questions_data.get("questions", []):
                if str(q.get("id")) == str(question_id):
                    return q.get("question", {}).get("fi", f"Kysymys {question_id}")
        
        # Hae käyttäjien kysymykset
        new_questions_data = self.election_manager.get_election_data("newquestions.json")
        if new_questions_data:
            for q in new_questions_data.get("questions", []):
                if str(q.get("id")) == str(question_id):
                    return q.get("question", {}).get("fi", f"Kysymys {question_id}")
        
        return f"Kysymys {question_id}"
    
    def get_candidate_profile_url(self, candidate: Dict[str, Any]) -> str:
        """Luo IPFS-URL:n ehdokkaan profiiliin"""
        if "profile_html_cid" in candidate:
            return f"https://ipfs.io/ipfs/{candidate['profile_html_cid']}"
        return ""
    
    def print_match_results(self, matches: List[Dict[str, Any]]):
        """Tulostaa hakutulokset siististi"""
        print(f"\n🎯 HAKUTULOKSET ({len(matches)} EHDOKASTA)")
        print("=" * 50)
        
        for i, match in enumerate(matches, 1):
            candidate = match["candidate"]
            percentage = match["match_percentage"]
            score = match["match_score"]
            max_score = match["max_possible_score"]
            matched_q = match["matched_questions"]
            
            print(f"{i}. {candidate['name']} ({candidate['party']})")
            print(f"   Yhteensopivuus: {percentage:.1f}% ({score:.1f}/{max_score} pistettä)")
            print(f"   Vastattuja kysymyksiä: {matched_q}/{len(match['match_details'])}")
            
            # Näytä profiililinkki jos saatavilla
            profile_url = self.get_candidate_profile_url(candidate)
            if profile_url:
                print(f"   Profiili: {profile_url}")
            
            print()
