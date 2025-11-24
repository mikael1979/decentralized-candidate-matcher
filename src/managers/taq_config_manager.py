# src/managers/taq_config_manager.py
"""
TAQ-pohjainen config-päivitysten hallinta – TÄYSIN TOIMIVA KORJATTU VERSIO
"""
import hashlib
import json
import copy
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from core.config_manager import ConfigManager

class TAQConfigManager:
    def __init__(self, election_id: str):
        self.election_id = election_id
        self.config_path = Path(f"config/elections/{election_id}/election_config.json")
        self.proposals_path = Path(f"data/taq/config_proposals/{election_id}.json")
        self.proposals_path.parent.mkdir(parents=True, exist_ok=True)

    def propose_config_update(self, changes: Dict, update_type: str,
                            justification: str, proposer_node_id: str) -> str:
        """Ehdotta uutta config-päivitystä TAQ-kvoorumille - KORJATTU"""
        
        # KORJATTU: Lisää config_update_-etuliite tässä
        full_update_type = f"config_update_{update_type}"
        
        if full_update_type not in ["config_update_minor", "config_update_major", "config_update_emergency"]:
            raise ValueError(f"Tuntematon update_type: {full_update_type}")

        proposal_id = self._generate_proposal_id(changes, proposer_node_id)
        current_config = self._load_current_config()

        proposed_config = self._apply_changes_to_config(current_config, changes)

        proposal = {
            "proposal_id": proposal_id,
            "type": full_update_type,  # Käytä täyttä tyyppiä
            "changes": changes,
            "current_config_hash": self._calculate_config_hash(current_config),
            "proposed_config_hash": self._calculate_config_hash(proposed_config),
            "proposed_config": proposed_config,
            "justification": justification,
            "proposer_node_id": proposer_node_id,
            "created_at": datetime.now().isoformat(),
            "timeout_at": (datetime.now() + timedelta(hours=72)).isoformat(),
            "status": "pending",
            "votes": {},
            "taq_parameters": self._calculate_taq_parameters(full_update_type, changes),  # Käytä täyttä tyyppiä
            "media_bonus_applied": False
        }

        self._save_proposal(proposal)
        print(f"✅ CONFIG-PÄIVITYS EHOTETTU: {proposal_id}")
        print(f"📊 Tyyppi: {full_update_type}")
        print(f"📝 Perustelu: {justification[:60]}...")
        print(f"🔑 Muutos: {list(changes.keys())[0]} = {list(changes.values())[0]}")
        return proposal_id

    def cast_vote_on_config(self, proposal_id: str, node_id: str, vote: str,
                          weight: float = 1.0, justification: str = "") -> bool:
        """Äänestä config-päivitysehdotuksesta"""
        proposal = self._load_proposal(proposal_id)
        if not proposal or proposal["status"] != "pending":
            return False

        if node_id in proposal["votes"]:
            return False

        proposal["votes"][node_id] = {
            "vote": vote,
            "weight": weight,
            "justification": justification,
            "timestamp": datetime.now().isoformat()
        }

        # Tarkista onko kvoorumi saavutettu
        if self._check_quorum_reached(proposal):
            proposal["status"] = "approved" if self._is_approved(proposal) else "rejected"
            if proposal["status"] == "approved":
                self._apply_approved_update(proposal)

        self._save_proposal(proposal, overwrite=True)
        return True

    def _check_quorum_reached(self, proposal: Dict) -> bool:
        """Tarkista onko kvoorumi saavutettu"""
        params = proposal["taq_parameters"]
        total_weight = sum(v["weight"] for v in proposal["votes"].values())
        approve_weight = sum(v["weight"] for v in proposal["votes"].values() if v["vote"] == "approve")

        if total_weight == 0:
            return False

        current_ratio = approve_weight / total_weight
        threshold = params.get("time_adjusted_threshold", params["base_threshold"])

        return current_ratio >= threshold

    def _is_approved(self, proposal: Dict) -> bool:
        """Tarkista onko ehdotus hyväksytty"""
        total = sum(v["weight"] for v in proposal["votes"].values())
        approve = sum(v["weight"] for v in proposal["votes"].values() if v["vote"] == "approve")
        return approve / total >= 0.51  # lopullinen varmistus

    def _apply_approved_update(self, proposal: Dict):
        """Toteuta hyväksytty config-päivitys"""
        config_mgr = ConfigManager(self.election_id)
        success = config_mgr.apply_approved_config_update(proposal, self.election_id)
        if success:
            print(f"✅ CONFIG PÄIVITETTY LOPULLISESTI: {proposal['proposal_id']}")
        else:
            proposal["status"] = "failed_application"
            self._save_proposal(proposal, overwrite=True)

    def _generate_proposal_id(self, changes: Dict, node_id: str) -> str:
        """Generoi uniikki proposal-ID"""
        raw = f"{self.election_id}{node_id}{json.dumps(changes,sort_keys=True)}{datetime.now().isoformat()}"
        return hashlib.sha256(raw.encode()).hexdigest()[:24]

    def _load_current_config(self) -> Dict:
        """Lataa nykyinen config"""
        return ConfigManager(self.election_id).get_election_config()

    def _apply_changes_to_config(self, current: Dict, changes: Dict) -> Dict:
        """Toteuta muutokset config-objektiin"""
        new = copy.deepcopy(current)
        for key_path, value in changes.items():
            keys = key_path.split(".")
            d = new
            for k in keys[:-1]:
                d = d[k]
            d[keys[-1]] = value
        return new

    def _calculate_config_hash(self, config: Dict) -> str:
        """Laske config-tiedoston tiiviste"""
        s = json.dumps(config, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(s.encode()).hexdigest()

    def _calculate_taq_parameters(self, update_type: str, changes: Dict) -> Dict:
        """Laske TAQ-parametrit config-päivitykselle"""
        base = {
            "config_update_minor": {"base_threshold": 0.51, "min_approvals": 2},
            "config_update_major": {"base_threshold": 0.75, "min_approvals": 5},
            "config_update_emergency": {"base_threshold": 0.40, "min_approvals": 2},
        }[update_type]

        # Kriittiset avaimet → pakotetaan major-tasolle
        critical = ["max_candidates", "security_measures", "crypto_settings", "network_config"]
        if any(k.split(".")[0] in critical for k in changes):
            base["base_threshold"] = max(base["base_threshold"], 0.80)
            base["min_approvals"] = max(base["min_approvals"], 5)

        base["time_adjusted_threshold"] = base["base_threshold"]  # myöhemmin aikalisäys
        return base

    def _save_proposal(self, proposal: Dict, overwrite: bool = False):
        """Tallenna proposal tiedostoon"""
        proposals = []
        if self.proposals_path.exists():
            try:
                proposals = json.loads(self.proposals_path.read_text(encoding="utf-8"))
            except:
                proposals = []

        if overwrite:
            proposals = [p for p in proposals if p["proposal_id"] != proposal["proposal_id"]]
        proposals.append(proposal)

        self.proposals_path.write_text(json.dumps(proposals, indent=2, ensure_ascii=False), encoding="utf-8")

    def _load_proposal(self, proposal_id: str) -> Optional[Dict]:
        """Lataa proposal ID:n perusteella"""
        if not self.proposals_path.exists():
            return None
        proposals = json.loads(self.proposals_path.read_text(encoding="utf-8"))
        return next((p for p in proposals if p["proposal_id"] == proposal_id), None)

    def get_all_proposals(self) -> List[Dict]:
        """Hae kaikki proposalit"""
        if not self.proposals_path.exists():
            return []
        try:
            return json.loads(self.proposals_path.read_text(encoding="utf-8"))
        except:
            return []

    def _load_all_proposals(self) -> List[Dict]:
        """Lataa kaikki proposalit - tämä metodi puuttui!"""
        return self.get_all_proposals()
    
    def get_proposal_status(self, proposal_id: str) -> Optional[Dict]:
        """Hae proposalin tila"""
        return self._load_proposal(proposal_id)
    
    def list_proposals(self, status_filter: str = None) -> List[Dict]:
        """Listaa proposalit"""
        proposals = self.get_all_proposals()
        if status_filter:
            proposals = [p for p in proposals if p.get("status") == status_filter]
        return proposals
