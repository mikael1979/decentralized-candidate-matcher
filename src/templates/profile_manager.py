#!/usr/bin/env python3
"""
Profiilien hallinta ja datan käsittely
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class ProfileManager:
    """Profiilien hallintaluokka"""
    
    def __init__(self, election_id: str = "Jumaltenvaalit2026"):
        self.election_id = election_id
        self.output_dir = Path("output/profiles")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = Path("data/runtime/profiles_metadata.json")
        self.metadata_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _get_party_candidates(self, party_id: str) -> List[Dict]:
        """Hae puolueen ehdokkaat"""
        candidates_file = Path("data/runtime/candidates.json")
        if candidates_file.exists():
            with open(candidates_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [c for c in data.get("candidates", []) 
                       if c["basic_info"].get("party") == party_id]
        return []
    
    def _load_questions(self) -> List[Dict]:
        """Lataa kysymykset"""
        questions_file = Path("data/runtime/questions.json")
        if questions_file.exists():
            with open(questions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("questions", [])
        return []
    
    def generate_candidate_cards(self, candidates: List[Dict]) -> str:
        """Generoi ehdokaskortit"""
        if not candidates:
            return '<p class="text-center">Ei ehdokkaita</p>'
        
        cards = []
        for candidate in candidates:
            card = f"""
            <div class="member-card">
                <div class="member-name">{candidate['basic_info']['name']['fi']}</div>
                <div class="member-domain">{candidate['basic_info'].get('domain', 'Ei aluetta')}</div>
                <div class="member-answers">{len(candidate.get('answers', []))} vastausta</div>
                <a href="/output/profiles/candidate_{candidate['candidate_id']}.html" class="data-link" style="margin-top: 0.5rem; padding: 0.5rem;">
                    👤 Näytä profiili
                </a>
            </div>
            """
            cards.append(card)
        
        return '\n'.join(cards)
    
    def generate_answer_cards(self, answers: List[Dict]) -> str:
        """Generoi vastauskortit"""
        if not answers:
            return '<p class="text-center">Ei vastauksia</p>'
        
        # Lataa kysymykset nimeä varten
        questions = self._load_questions()
        question_map = {q["local_id"]: q["content"]["question"]["fi"] for q in questions}
        
        answer_cards = []
        for answer in answers:
            question_text = question_map.get(answer["question_id"], answer["question_id"])
            explanation = answer.get("explanation", {}).get("fi", "")
            confidence = answer.get("confidence", 3)
            
            card = f"""
            <div class="answer-item">
                <div class="answer-value">{answer['answer_value']}/5</div>
                <div class="answer-question">{question_text}</div>
                {f'<div class="answer-explanation">{explanation}</div>' if explanation else ''}
                <div class="confidence">Varmuus: {confidence}/5</div>
            </div>
            """
            answer_cards.append(card)
        
        return '\n'.join(answer_cards)
    
    def _get_ipfs_cids(self) -> Dict:
        """Hae IPFS-CID:t datatiedostoille"""
        ipfs_sync_file = Path("data/runtime/ipfs_sync.json")
        if ipfs_sync_file.exists():
            with open(ipfs_sync_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("ipfs_cids", {})
        return {}
    
    def _load_metadata(self) -> Dict:
        """Lataa profiilien metadata"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Alusta uusi metadata
        return {
            "metadata": {
                "version": "1.0.0",
                "created": datetime.now().isoformat(),
                "election_id": self.election_id,
                "description": "Profiilisivujen metadata ja linkit"
            },
            "profiles": {},
            "last_updated": datetime.now().isoformat()
        }
    
    def _update_profile_metadata(self, profile_metadata: Dict):
        """Päivitä profiilien metadatatiedosto"""
        metadata = self._load_metadata()
        
        profile_key = f"{profile_metadata['entity_type']}_{profile_metadata['entity_id']}"
        metadata["profiles"][profile_key] = profile_metadata
        metadata["last_updated"] = datetime.now().isoformat()
        
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def get_base_json(self) -> Dict:
        """Hae base.json data kaikista profiileista ja linkeistä"""
        metadata = self._load_metadata()
        
        # Lataa IPFS-synkronointitiedot
        ipfs_cids = self._get_ipfs_cids()
        
        base_data = {
            "metadata": {
                "election_id": self.election_id,
                "generated_at": datetime.now().isoformat(),
                "version": "1.0.0",
                "description": "Jumaltenvaalit 2026 - Base data kaikista resursseista"
            },
            "links": {
                "parties_json": "/data/runtime/parties.json",
                "candidates_json": "/data/runtime/candidates.json", 
                "questions_json": "/data/runtime/questions.json",
                "meta_json": "/data/runtime/meta.json",
                "ipfs_sync_json": "/data/runtime/ipfs_sync.json",
                "profiles_metadata": "/data/runtime/profiles_metadata.json"
            },
            "ipfs_cids": ipfs_cids,
            "profiles": metadata["profiles"],
            "statistics": {
                "total_profiles": len(metadata["profiles"]),
                "party_profiles": len([p for p in metadata["profiles"].values() if p["entity_type"] == "party"]),
                "candidate_profiles": len([p for p in metadata["profiles"].values() if p["entity_type"] == "candidate"])
            }
        }
        
        return base_data
    
    def save_base_json(self) -> str:
        """Tallenna base.json tiedosto"""
        base_data = self.get_base_json()
        base_file = Path("output/base.json")
        base_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(base_file, 'w', encoding='utf-8') as f:
            json.dump(base_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ base.json tallennettu: {base_file}")
        return str(base_file)
