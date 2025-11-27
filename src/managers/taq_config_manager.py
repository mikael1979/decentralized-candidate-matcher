#!/usr/bin/env python3
"""
TAQ-pohjainen config-päivitysten hallinta – PÄIVITETTY UUDELLE CONFIG-RAKENTEELLE
"""
import hashlib
import json
import copy
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

# PÄIVITETTY IMPORT - käytä uutta modulaarista rakennetta
from core.config import ConfigManager


class TAQConfigManager:
    def __init__(self, election_id: str):
        self.election_id = election_id
        self.config_path = Path(f"config/elections/{election_id}/election_config.json")
        self.proposals_path = Path(f"data/elections/{election_id}/config_proposals.json")
        self.voting_period_hours = 24  # 24 tuntia äänestysaikaa

    def propose_config_update(self, changes: Dict, update_type: str, 
                            justification: str, proposer_node: str) -> str:
        """Ehdotta config-päivitystä - KORJATTU VERSIO"""
        
        # Tarkista muutosten kelvollisuus
        if not changes or not isinstance(changes, dict):
            raise ValueError("Muutosten täytyy olla ei-tyhjä sanakirja")
        
        # Luo proposal
        proposal_id = self._generate_proposal_id()
        proposal = {
            "proposal_id": proposal_id,
            "election_id": self.election_id,
            "changes": changes,
            "update_type": update_type,
            "justification": justification,
            "proposer_node": proposer_node,
            "created_at": datetime.now().isoformat(),
            "voting_deadline": (datetime.now() + timedelta(hours=self.voting_period_hours)).isoformat(),
            "status": "active",
            "votes": {}
        }
        
        # Tallenna proposal
        self._save_proposal(proposal)
        
        print(f"✅ CONFIG-PÄIVITYS EHDOTETTU: {proposal_id}")
        print(f"📊 Muutokset: {len(changes)} kohdetta")
        print(f"⏰ Äänestysaikaa: {self.voting_period_hours}h")
        print(f"🔍 Tarkista status: python src/cli/manage_config.py status --proposal-id {proposal_id}")
        
        return proposal_id

    def vote_on_proposal(self, proposal_id: str, node_id: str, vote: bool, 
                        justification: str = "") -> bool:
        """Äänestä config-päivitysehdotusta"""
        
        proposal = self._load_proposal(proposal_id)
        if not proposal:
            raise ValueError(f"Proposalia ei löydy: {proposal_id}")
        
        # Tarkista äänestysaika
        deadline = datetime.fromisoformat(proposal["voting_deadline"])
        if datetime.now() > deadline:
            raise ValueError("Äänestysaika on päättynyt")
        
        # Tallenna ääni
        proposal["votes"][node_id] = {
            "vote": vote,
            "justification": justification,
            "timestamp": datetime.now().isoformat()
        }
        
        # Päivitä status tarvittaessa
        self._update_proposal_status(proposal)
        
        # Tallenna
        self._save_proposal(proposal)
        
        print(f"✅ ÄÄNI ANNETTU: {'✅ Kyllä' if vote else '❌ Ei'}")
        return True

    def get_proposal_status(self, proposal_id: str) -> Dict:
        """Hae ehdotuksen tila"""
        proposal = self._load_proposal(proposal_id)
        if not proposal:
            raise ValueError(f"Proposalia ei löydy: {proposal_id}")
        
        return {
            "proposal_id": proposal_id,
            "status": proposal["status"],
            "votes": proposal["votes"],
            "created_at": proposal["created_at"],
            "voting_deadline": proposal["voting_deadline"],
            "changes": proposal["changes"],
            "update_type": proposal["update_type"],
            "justification": proposal["justification"]
        }

    def calculate_voting_consensus(self, proposal_id: str) -> Dict:
        """Laske äänestyskonsensus"""
        proposal = self._load_proposal(proposal_id)
        if not proposal:
            raise ValueError(f"Proposalia ei löydy: {proposal_id}")
        
        votes = proposal["votes"]
        yes_votes = sum(1 for vote in votes.values() if vote["vote"])
        no_votes = sum(1 for vote in votes.values() if not vote["vote"])
        total_votes = len(votes)
        
        consensus_threshold = 0.6  # 60% tarvitaan hyväksymiseen
        
        return {
            "total_votes": total_votes,
            "yes_votes": yes_votes,
            "no_votes": no_votes,
            "consensus_required": consensus_threshold,
            "current_consensus": yes_votes / total_votes if total_votes > 0 else 0,
            "reached_consensus": (yes_votes / total_votes >= consensus_threshold) if total_votes > 0 else False
        }

    def process_config_proposals(self) -> List[Dict]:
        """Käsittele vanhentuneet ehdotukset"""
        proposals = self._load_all_proposals()
        processed = []
        
        for proposal in proposals:
            if proposal["status"] == "active":
                deadline = datetime.fromisoformat(proposal["voting_deadline"])
                if datetime.now() > deadline:
                    # Päivitä vanhentuneet ehdotukset
                    consensus = self.calculate_voting_consensus(proposal["proposal_id"])
                    if consensus["reached_consensus"]:
                        proposal["status"] = "approved"
                    else:
                        proposal["status"] = "rejected"
                    
                    self._save_proposal(proposal)
                    processed.append(proposal)
        
        return processed

    def _generate_proposal_id(self) -> str:
        """Luo uniikki proposal-ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_hash = hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:8]
        return f"config_prop_{timestamp}_{random_hash}"

    def _save_proposal(self, proposal: Dict):
        """Tallenna proposal tiedostoon"""
        self.proposals_path.parent.mkdir(parents=True, exist_ok=True)
        
        proposals = self._load_all_proposals()
        
        # Korvaa tai lisää proposal
        existing_index = next((i for i, p in enumerate(proposals) 
                             if p["proposal_id"] == proposal["proposal_id"]), -1)
        if existing_index >= 0:
            proposals[existing_index] = proposal
        else:
            proposals.append(proposal)
        
        with open(self.proposals_path, 'w', encoding='utf-8') as f:
            json.dump(proposals, f, indent=2, ensure_ascii=False)

    def _load_proposal(self, proposal_id: str) -> Optional[Dict]:
        """Lataa proposal tiedostosta"""
        proposals = self._load_all_proposals()
        return next((p for p in proposals if p["proposal_id"] == proposal_id), None)

    def _load_all_proposals(self) -> List[Dict]:
        """Lataa kaikki proposalit"""
        if not self.proposals_path.exists():
            return []
        
        try:
            with open(self.proposals_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []

    def _update_proposal_status(self, proposal: Dict):
        """Päivitä proposalin status äänestysten perusteella"""
        consensus = self.calculate_voting_consensus(proposal["proposal_id"])
        
        if consensus["reached_consensus"]:
            proposal["status"] = "approved"
        elif consensus["total_votes"] >= 3:  # Vähintään 3 ääntä
            proposal["status"] = "rejected"

    def _apply_changes_to_config(self, current_config: Dict, changes: Dict) -> Dict:
        """Toteuta muutokset config-objektiin (apumetodi)"""
        import copy
        updated_config = copy.deepcopy(current_config)
        
        for key, new_value in changes.items():
            self._set_nested_value(updated_config, key, new_value)
            
        return updated_config

    def _set_nested_value(self, config: Dict, key: str, value: Any):
        """Aseta arvo nested-rakenteeseen piste-erotellulla avaimella"""
        keys = key.split('.')
        current = config
        
        # Navigoi viimeiseen tasoon asti
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # Aseta arvo
        current[keys[-1]] = value

    def get_election_config(self) -> Dict:
        """Hae vaalikonfiguraatio - PÄIVITETTY"""
        return ConfigManager(self.election_id).get_election_config()
