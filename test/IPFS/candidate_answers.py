class CandidateAnswerManager:
    def __init__(self, ipfs, election_manager):
        self.ipfs = ipfs
        self.manager = election_manager
    
    def submit_answers(self, candidate_id: int, answers: List[Dict]) -> str:
        """Lähettää ehdokkaan vastaukset"""
        answer_data = {
            "election_id": "test_election_2024",
            "candidate_id": candidate_id,
            "answers": answers,
            "submission_timestamp": datetime.now().isoformat(),
            "integrity": self.manager._create_integrity_hash(answers)
        }
        
        # Tallenna vastaukset IPFS:ään
        answer_cid = self.ipfs.add_json(answer_data)["Hash"]
        
        # Päivitä ehdokkaan tietoihin
        candidates_data = self.manager.get_election_data("candidates.json")
        for candidate in candidates_data["candidates"]:
            if candidate["id"] == candidate_id:
                candidate["answer_cid"] = answer_cid
                break
        
        # Päivitä candidates.json
        self.manager.add_candidate(candidate)  # Tämä korvaa vanhan
        
        return answer_cid
    
    def get_candidate_answers(self, candidate_id: int) -> Optional[Dict]:
        """Hakee ehdokkaan vastaukset"""
        candidates_data = self.manager.get_election_data("candidates.json")
        for candidate in candidates_data["candidates"]:
            if candidate["id"] == candidate_id and "answer_cid" in candidate:
                return self.ipfs.get_json(candidate["answer_cid"])
        return None
