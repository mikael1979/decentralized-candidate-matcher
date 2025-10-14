class SearchEngine:
    def __init__(self, ipfs, election_manager):
        self.ipfs = ipfs
        self.manager = election_manager
    
    def find_matching_candidates(self, user_answers: Dict[str, int], top_n: int = 5) -> List[Dict]:
        """Etsii parhaiten vastaavat ehdokkaat käyttäjän vastausten perusteella"""
        candidates_data = self.manager.get_election_data("candidates.json")
        matches = []
        
        for candidate in candidates_data["candidates"]:
            if "answer_cid" not in candidate:
                continue
                
            candidate_answers = self.ipfs.get_json(candidate["answer_cid"])
            if not candidate_answers:
                continue
            
            score = self._calculate_match_score(user_answers, candidate_answers)
            matches.append({
                "candidate": candidate,
                "match_score": score,
                "match_percentage": (score / (len(user_answers) * 5)) * 100
            })
        
        return sorted(matches, key=lambda x: x["match_score"], reverse=True)[:top_n]
    
    def _calculate_match_score(self, user_answers: Dict, candidate_answers: Dict) -> float:
        """Laskee vastausten yhteensopivuuden"""
        score = 0
        for q_id, user_answer in user_answers.items():
            for candidate_answer in candidate_answers.get("answers", []):
                if str(candidate_answer["question_id"]) == str(q_id):
                    # Laske etäisyys -5 - 5 asteikolla
                    distance = abs(candidate_answer["answer"] - user_answer)
                    similarity = 5 - distance  # 0-10 asteikolla
                    score += max(0, similarity)
                    break
        return score
