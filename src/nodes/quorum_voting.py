#!/usr/bin/env python3
"""
Hajautettu kvoorumi-äänestys multi-node järjestelmässä
"""
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

class QuorumVoting:
    def __init__(self, election_id: str = "Jumaltenvaalit2026"):
        self.election_id = election_id
        self.votes_file = Path(f"data/nodes/{election_id}_votes.json")
        self.votes_file.parent.mkdir(parents=True, exist_ok=True)
    
    def start_vote(self, proposal_id: str, proposal_data: Dict, 
                   min_approvals: int = 3, timeout_hours: int = 24) -> Dict:
        """Aloita uusi kvoorumi-äänestys"""
        
        vote_session = {
            "proposal_id": proposal_id,
            "proposal_data": proposal_data,
            "min_approvals": min_approvals,
            "timeout": (datetime.now() + timedelta(hours=timeout_hours)).isoformat(),
            "votes": {},
            "status": "active",
            "created": datetime.now().isoformat()
        }
        
        # Lataa nykyiset äänestykset
        votes_data = self._load_votes()
        votes_data[proposal_id] = vote_session
        self._save_votes(votes_data)
        
        print(f"✅ Äänestys aloitettu: {proposal_id}")
        print(f"📊 Vaadittuja hyväksymisiä: {min_approvals}")
        print(f"⏰ Aikaraja: {timeout_hours}h")
        
        return vote_session
    
    def cast_vote(self, proposal_id: str, node_id: str, 
                  vote: str, node_public_key: str, justification: str = "") -> bool:
        """Äänestä proposalin puolesta tai vastaan"""
        
        votes_data = self._load_votes()
        
        if proposal_id not in votes_data:
            print(f"❌ Äänestystä ei löydy: {proposal_id}")
            return False
        
        vote_session = votes_data[proposal_id]
        
        # Tarkista aikaraja
        timeout = datetime.fromisoformat(vote_session["timeout"])
        if datetime.now() > timeout:
            print("❌ Äänestys on päättynyt")
            vote_session["status"] = "timeout"
            self._save_votes(votes_data)
            return False
        
        # Tarkista onko node jo äänestänyt
        if node_id in vote_session["votes"]:
            print(f"❌ Node {node_id} on jo äänestänyt")
            return False
        
        # Tallenna ääni
        vote_record = {
            "node_id": node_id,
            "vote": vote,  # "approve", "reject", "abstain"
            "justification": justification,
            "timestamp": datetime.now().isoformat(),
            "public_key_fingerprint": self._calculate_key_fingerprint(node_public_key)
        }
        
        vote_session["votes"][node_id] = vote_record
        
        # Tarkista onko kvoorumi saavutettu
        self._check_quorum(vote_session)
        
        self._save_votes(votes_data)
        
        print(f"✅ Ääni annettu: {node_id} → {vote}")
        return True
    
    def _check_quorum(self, vote_session: Dict) -> bool:
        """Tarkista onko kvoorumi saavutettu"""
        approve_count = sum(1 for vote in vote_session["votes"].values() 
                          if vote["vote"] == "approve")
        
        if approve_count >= vote_session["min_approvals"]:
            vote_session["status"] = "approved"
            vote_session["decided_at"] = datetime.now().isoformat()
            print(f"🎉 Proposal hyväksytty! {approve_count}/{vote_session['min_approvals']} ääntä")
            return True
        
        # Tarkista hylkäys (yli puolet hylkää)
        total_votes = len(vote_session["votes"])
        reject_count = sum(1 for vote in vote_session["votes"].values() 
                         if vote["vote"] == "reject")
        
        if reject_count > total_votes / 2 and total_votes >= 3:
            vote_session["status"] = "rejected"
            vote_session["decided_at"] = datetime.now().isoformat()
            print(f"❌ Proposal hylätty! {reject_count}/{total_votes} ääntä")
            return True
        
        return False
    
    def get_vote_status(self, proposal_id: str) -> Optional[Dict]:
        """Hae äänestyksen tila"""
        votes_data = self._load_votes()
        return votes_data.get(proposal_id)
    
    def _calculate_key_fingerprint(self, public_key: str) -> str:
        """Laske julkisen avaimen tunniste"""
        return hashlib.sha256(public_key.encode()).hexdigest()[:16]
    
    def _load_votes(self) -> Dict:
        """Lataa äänestystiedot"""
        if self.votes_file.exists():
            with open(self.votes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_votes(self, votes_data: Dict):
        """Tallenna äänestystiedot"""
        with open(self.votes_file, 'w', encoding='utf-8') as f:
            json.dump(votes_data, f, indent=2, ensure_ascii=False)
