# candidate_answers.py
import json
from datetime import datetime
from typing import Dict, List, Any

class CandidateAnswerManager:
    def __init__(self, ipfs, election_manager):
        self.ipfs = ipfs
        self.election_manager = election_manager
    
    def submit_answers(self, candidate_id: int, answers: List[Dict[str, Any]], private_key: str) -> str:
        """Lähettää ehdokkaan vastaukset allekirjoituksella"""
        candidate = self.election_manager.get_candidate(candidate_id)
        if not candidate:
            raise ValueError(f"Ehdokasta ID:llä {candidate_id} ei löydy")
        
        # Varmista että ehdokas on oikeutettu (allekirjoituksen tarkistus)
        if not self._verify_candidate_identity(candidate, private_key):
            raise ValueError("Virheellinen allekirjoitus")
        
        print(f"📝 Ehdokas {candidate['name']} lähettää {len(answers)} vastausta...")
        
        # Luo vastausdata
        answer_data = {
            "election_id": "test_election",
            "candidate_id": candidate_id,
            "candidate_name": candidate["name"],
            "candidate_public_key": candidate["public_key"],
            "answers": answers,
            "submission_timestamp": datetime.now().isoformat()
        }
        
        # Allekirjoita vastaukset
        answer_data["signature"] = self._sign_data(answer_data, private_key)
        answer_data["signed_data"] = json.dumps(answer_data, sort_keys=True)
        
        # Lisää integrity hash
        answer_data["integrity"] = self.election_manager._create_integrity_hash(answer_data)
        
        # Tallenna IPFS:ään
        result = self.ipfs.add_json(answer_data)
        answer_cid = result["Hash"]
        
        # Päivitä ehdokkaan tietoihin
        candidate["answer_cid"] = answer_cid
        candidate["last_answered"] = datetime.now().isoformat()
        self.election_manager.add_candidate(candidate)
        
        print(f"✅ Vastaukset tallennettu - CID: {answer_cid}")
        return answer_cid
    
    def _verify_candidate_identity(self, candidate: Dict[str, Any], private_key: str) -> bool:
        """Tarkistaa että ehdokas on oikeutettu lähettämään vastauksia"""
        # Toteuta allekirjoituksen tarkistus
        # (Käytä samaa logiikkaa kuin CandidateRegistration)
        return True  # Placeholder - toteuta oikea tarkistus
    
    def _sign_data(self, data: Dict[str, Any], private_key: str) -> str:
        """Allekirjoittaa datan"""
        # Toteuta allekirjoitus
        return "signature_placeholder"  # Placeholder - toteuta oikea allekirjoitus
    
    def get_candidate_answers(self, candidate_id: int) -> Dict[str, Any]:
        """Hakee ehdokkaan vastaukset"""
        candidate = self.election_manager.get_candidate(candidate_id)
        if not candidate or "answer_cid" not in candidate:
            return {}
        
        return self.ipfs.get_json(candidate["answer_cid"]) or {}
