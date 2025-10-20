import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional

class ElectionDataManager:
    """
    Korkeamman tason wrapperi vaalikonedatan hallintaan MockIPFS:n päällä
    """
    
    def __init__(self, ipfs):
        self.ipfs = ipfs
        self.root_cid = None
        
    def _create_integrity_hash(self, data: Any) -> Dict[str, Any]:
        """Luo integrity hashin datalle"""
        # Kopioi data ettei muokata alkuperäistä
        data_to_hash = data.copy() if isinstance(data, dict) else {"data": data}
        
        # Poista nykyinen integrity hash jos on olemassa
        if 'integrity' in data_to_hash:
            del data_to_hash['integrity']
        
        # Järjestä avaimet ja käytä kompaktia JSON-muotoa
        json_str = json.dumps(data_to_hash, sort_keys=True, separators=(',', ':'))
        hash_value = hashlib.sha256(json_str.encode()).hexdigest()
        
        return {
            "algorithm": "sha256",
            "hash": f"sha256:{hash_value}",
            "computed": datetime.now().isoformat()
        }
    
    def _add_data_with_integrity(self, data: Dict[str, Any]) -> str:
        """Lisää data IPFS:ään integrity hashilla"""
        data_with_integrity = {
            **data,
            "integrity": self._create_integrity_hash(data)
        }
        result = self.ipfs.add_json(data_with_integrity)
        return result["Hash"]
    
    def initialize_election(self, meta_data: Dict[str, Any]) -> str:
        """Alustaa uuden vaalin"""
        print("🔧 Alustetaan uusi vaali...")
        
        # 1. Lisää meta.json integrity hashilla
        meta_cid = self._add_data_with_integrity(meta_data)
        print(f"   ✅ meta.json lisätty: {meta_cid}")
        
        # 2. Alusta tyhjät datasetit integrity hasheilla
        questions_data = {
            "election_id": meta_data["election"]["id"],
            "language": "fi",
            "questions": []
        }
        questions_cid = self._add_data_with_integrity(questions_data)
        print(f"   ✅ questions.json alustettu: {questions_cid}")
        
        candidates_data = {
            "election_id": meta_data["election"]["id"],
            "language": "fi",
            "candidates": []
        }
        candidates_cid = self._add_data_with_integrity(candidates_data)
        print(f"   ✅ candidates.json alustettu: {candidates_cid}")
        
        new_questions_data = {
            "election_id": meta_data["election"]["id"],
            "language": "fi",
            "question_type": "user_submitted",
            "questions": []
        }
        new_questions_cid = self._add_data_with_integrity(new_questions_data)
        print(f"   ✅ newquestions.json alustettu: {new_questions_cid}")
        
        community_votes_data = {
            "election_id": meta_data["election"]["id"],
            "language": "fi",
            "question_votes": [],
            "user_votes": []
        }
        community_votes_cid = self._add_data_with_integrity(community_votes_data)
        print(f"   ✅ community_votes.json alustettu: {community_votes_cid}")
        
        # 3. Luo root index
        root_index = {
            "election_id": meta_data["election"]["id"],
            "files": {
                "meta.json": meta_cid,
                "questions.json": questions_cid,
                "candidates.json": candidates_cid,
                "newquestions.json": new_questions_cid,
                "community_votes.json": community_votes_cid
            },
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        
        self.root_cid = self._add_data_with_integrity(root_index)
        self.ipfs.pin_add(self.root_cid)
        
        print(f"🎉 Vaali alustettu onnistuneesti! Root CID: {self.root_cid}")
        return self.root_cid
    
    def _update_file(self, file_key: str, update_function) -> str:
        """Apufunktio tiedoston päivittämiseen"""
        if not self.root_cid:
            raise ValueError("Vaalia ei ole alustettu. Kutsu initialize_election() ensin.")
        
        # Hae root data
        root_data = self.ipfs.get_json(self.root_cid)
        if not root_data:
            raise ValueError("Root dataa ei löydy")
        
        # Hae nykyinen tiedosto
        file_cid = root_data["files"][file_key]
        file_data = self.ipfs.get_json(file_cid)
        if not file_data:
            raise ValueError(f"Tiedostoa {file_key} ei löydy")
        
        # Päivitä data
        updated_data = update_function(file_data)
        
        # Lisää integrity hash
        updated_data["integrity"] = self._create_integrity_hash(updated_data)
        
        # Tallenna uusi versio
        new_cid = self.ipfs.add_json(updated_data)["Hash"]
        
        # Päivitä root
        root_data["files"][file_key] = new_cid
        root_data["timestamp"] = datetime.now().isoformat()
        root_data["integrity"] = self._create_integrity_hash(root_data)
        
        self.root_cid = self.ipfs.add_json(root_data)["Hash"]
        
        return new_cid
    
    def add_question(self, question_data: Dict[str, Any], is_official: bool = True) -> str:
        """Lisää kysymyksen"""
        file_key = "questions.json" if is_official else "newquestions.json"
        question_type = "virallinen" if is_official else "käyttäjän"
        
        print(f"📝 Lisätään {question_type} kysymys: {question_data['question']['fi'][:50]}...")
        
        def update_questions(data):
            data["questions"].append(question_data)
            return data
        
        new_cid = self._update_file(file_key, update_questions)
        print(f"   ✅ Kysymys lisätty - CID: {new_cid}")
        return new_cid
    
    def add_candidate(self, candidate_data: Dict[str, Any]) -> str:
        """Lisää ehdokkaan"""
        print(f"👤 Lisätään ehdokas: {candidate_data['name']}")
        
        def update_candidates(data):
            # Tarkista ettei ehdokas ole jo olemassa
            for existing_candidate in data["candidates"]:
                if existing_candidate["id"] == candidate_data["id"]:
                    # Päivitä olemassa oleva ehdokas
                    existing_candidate.update(candidate_data)
                    return data
            
            # Lisää uusi ehdokas
            data["candidates"].append(candidate_data)
            return data
        
        new_cid = self._update_file("candidates.json", update_candidates)
        print(f"   ✅ Ehdokas lisätty/päivitetty - CID: {new_cid}")
        return new_cid
    
    def add_user_question_vote(self, vote_data: Dict[str, Any]) -> str:
        """Lisää käyttäjän äänen kysymykselle"""
        print(f"🗳️ Lisätään ääni kysymykselle: {vote_data['question_id']}")
        
        def update_votes(data):
            data["user_votes"].append(vote_data)
            
            # Päivitä kysymyksen tilastot
            question_id = vote_data["question_id"]
            question_votes = [v for v in data["user_votes"] if v["question_id"] == question_id]
            
            total_votes = len(question_votes)
            appropriate_votes = sum(1 for v in question_votes if v["vote"] == "appropriate")
            inappropriate_ratio = 1 - (appropriate_votes / total_votes) if total_votes > 0 else 0
            
            # Päivitä tai lisää question_votes
            for qv in data["question_votes"]:
                if qv["question_id"] == question_id:
                    qv.update({
                        "total_votes": total_votes,
                        "appropriate_votes": appropriate_votes,
                        "inappropriate_votes": total_votes - appropriate_votes,
                        "inappropriate_ratio": inappropriate_ratio,
                        "confidence_score": appropriate_votes / total_votes if total_votes > 0 else 0,
                        "status": "approved" if inappropriate_ratio < 0.3 else "pending",
                        "last_updated": datetime.now().isoformat()
                    })
                    return data
            
            # Lisää uusi question_votes entry
            data["question_votes"].append({
                "question_id": question_id,
                "total_votes": total_votes,
                "appropriate_votes": appropriate_votes,
                "inappropriate_votes": total_votes - appropriate_votes,
                "inappropriate_ratio": inappropriate_ratio,
                "confidence_score": appropriate_votes / total_votes if total_votes > 0 else 0,
                "status": "approved" if inappropriate_ratio < 0.3 else "pending",
                "auto_moderated": total_votes >= 5,
                "last_updated": datetime.now().isoformat()
            })
            
            return data
        
        new_cid = self._update_file("community_votes.json", update_votes)
        print(f"   ✅ Ääni lisätty - CID: {new_cid}")
        return new_cid
    
    def get_election_data(self, file_name: str) -> Optional[Dict[str, Any]]:
        """Hakee vaalidataa tiedostonimellä"""
        if not self.root_cid:
            print("❌ Vaalia ei ole alustettu")
            return None
        
        root_data = self.ipfs.get_json(self.root_cid)
        if not root_data:
            print("❌ Root dataa ei löydy")
            return None
        
        if file_name not in root_data["files"]:
            print(f"❌ Tiedostoa {file_name} ei löydy")
            return None
        
        file_cid = root_data["files"][file_name]
        return self.ipfs.get_json(file_cid)
    
    def get_all_questions(self) -> List[Dict[str, Any]]:
        """Hakee kaikki kysymykset (viralliset + käyttäjien)"""
        official_questions = self.get_election_data("questions.json")
        user_questions = self.get_election_data("newquestions.json")
        
        all_questions = []
        if official_questions:
            all_questions.extend(official_questions.get("questions", []))
        if user_questions:
            all_questions.extend(user_questions.get("questions", []))
        
        return all_questions
    
    def get_candidate(self, candidate_id: int) -> Optional[Dict[str, Any]]:
        """Hakee ehdokkaan ID:llä"""
        candidates_data = self.get_election_data("candidates.json")
        if not candidates_data:
            return None
        
        for candidate in candidates_data.get("candidates", []):
            if candidate["id"] == candidate_id:
                return candidate
        return None
    
    def verify_integrity(self, data: Dict[str, Any]) -> bool:
        """Tarkistaa datan eheyden"""
        if 'integrity' not in data:
            return False
        
        stored_hash = data['integrity']['hash']
        
        # Luo uusi hash ilman integrity fieldiä
        data_without_integrity = {k: v for k, v in data.items() if k != 'integrity'}
        calculated_hash = self._create_integrity_hash(data_without_integrity)['hash']
        
        return stored_hash == calculated_hash
    
    def get_election_status(self) -> Dict[str, Any]:
        """Palauttaa vaalin tilastot"""
        if not self.root_cid:
            return {"status": "not_initialized"}
        
        root_data = self.ipfs.get_json(self.root_cid)
        if not root_data:
            return {"status": "root_not_found"}
        
        status = {
            "status": "active",
            "election_id": root_data["election_id"],
            "root_cid": self.root_cid,
            "last_updated": root_data.get("timestamp", "unknown"),
            "files": {}
        }
        
        # Kerää tilastot jokaisesta tiedostosta
        for file_name, file_cid in root_data["files"].items():
            file_data = self.ipfs.get_json(file_cid)
            if file_data:
                if file_name == "questions.json":
                    status["files"][file_name] = {
                        "questions_count": len(file_data.get("questions", [])),
                        "integrity_ok": self.verify_integrity(file_data)
                    }
                elif file_name == "newquestions.json":
                    status["files"][file_name] = {
                        "user_questions_count": len(file_data.get("questions", [])),
                        "integrity_ok": self.verify_integrity(file_data)
                    }
                elif file_name == "candidates.json":
                    status["files"][file_name] = {
                        "candidates_count": len(file_data.get("candidates", [])),
                        "integrity_ok": self.verify_integrity(file_data)
                    }
                elif file_name == "community_votes.json":
                    votes_data = file_data
                    status["files"][file_name] = {
                        "total_votes": len(votes_data.get("user_votes", [])),
                        "questions_with_votes": len(votes_data.get("question_votes", [])),
                        "integrity_ok": self.verify_integrity(votes_data)
                    }
                elif file_name == "meta.json":
                    status["files"][file_name] = {
                        "election_name": file_data.get("election", {}).get("name", {}),
                        "integrity_ok": self.verify_integrity(file_data)
                    }
        
        return status
    
    def list_all_files(self) -> Dict[str, str]:
        """Listaa kaikki tiedostot ja niiden CIDs"""
        if not self.root_cid:
            return {}
        
        root_data = self.ipfs.get_json(self.root_cid)
        return root_data.get("files", {})
