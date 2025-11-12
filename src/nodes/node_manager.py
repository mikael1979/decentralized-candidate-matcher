#!/usr/bin/env python3
"""
Multi-node hallinta Jumaltenvaaleille
"""
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

class NodeManager:
    def __init__(self, election_id: str = "Jumaltenvaalit2026"):
        self.election_id = election_id
        self.nodes_file = Path(f"data/nodes/{election_id}_nodes.json")
        self.nodes_file.parent.mkdir(parents=True, exist_ok=True)
        self.nodes = self._load_nodes()
    
    def _load_nodes(self) -> Dict:
        """Lataa nodejen tiedot"""
        if self.nodes_file.exists():
            with open(self.nodes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"nodes": {}, "metadata": {"election_id": self.election_id}}
    
    def register_node(self, node_id: str, node_data: Dict) -> bool:
        """Rekisteröi uusi node"""
        # Yksinkertaistettu versio ilman crypto_manager riippuvuutta
        if "public_key" not in node_data:
            return False
        
        # Laske julkisen avaimen tunniste (yksinkertaistettu)
        key_fingerprint = hashlib.sha256(node_data["public_key"].encode()).hexdigest()[:16]
        
        node_info = {
            "node_id": node_id,
            "public_key": node_data["public_key"],
            "key_fingerprint": key_fingerprint,
            "node_name": node_data.get("node_name", f"Node_{node_id}"),
            "domain": node_data.get("domain", "general"),
            "capabilities": node_data.get("capabilities", ["voting", "verification"]),
            "registration_timestamp": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
            "status": "active",
            "trust_score": node_data.get("trust_score", 10)
        }
        
        self.nodes["nodes"][node_id] = node_info
        self._save_nodes()
        
        print(f"✅ Node rekisteröity: {node_id} ({node_info['node_name']})")
        return True
    
    def get_active_nodes(self) -> List[Dict]:
        """Hae aktiiviset nodet"""
        active_nodes = []
        for node_id, node_info in self.nodes["nodes"].items():
            if node_info.get("status") == "active":
                active_nodes.append(node_info)
        return active_nodes
    
    def update_node_status(self, node_id: str, status: str) -> bool:
        """Päivitä noden tila"""
        if node_id in self.nodes["nodes"]:
            self.nodes["nodes"][node_id]["status"] = status
            self.nodes["nodes"][node_id]["last_seen"] = datetime.now().isoformat()
            self._save_nodes()
            return True
        return False
    
    def _save_nodes(self):
        """Tallenna nodejen tiedot"""
        with open(self.nodes_file, 'w', encoding='utf-8') as f:
            json.dump(self.nodes, f, indent=2, ensure_ascii=False)
    
    def get_quorum_nodes(self, min_trust_score: int = 5) -> List[Dict]:
        """Hae nodet jotka kelpaavat kvoorumiin"""
        quorum_nodes = []
        for node_info in self.get_active_nodes():
            if node_info.get("trust_score", 0) >= min_trust_score:
                quorum_nodes.append(node_info)
        return quorum_nodes
    
    def calculate_quorum_threshold(self) -> int:
        """Laske kvoorumin kynnysarvo"""
        quorum_nodes = self.get_quorum_nodes()
        return max(2, len(quorum_nodes) // 2 + 1)  # Vähintään 2, yli puolet

# Esimääritellyt Olympolaiset
OLYMPIAN_NODES = {
    "node_zeus": {
        "node_name": "Zeus",
        "domain": "sky_thunder",
        "capabilities": ["voting", "verification", "leadership"],
        "trust_score": 15
    },
    "node_athena": {
        "node_name": "Athena", 
        "domain": "wisdom_warfare",
        "capabilities": ["voting", "verification", "strategy"],
        "trust_score": 15
    },
    "node_poseidon": {
        "node_name": "Poseidon",
        "domain": "sea_earthquakes", 
        "capabilities": ["voting", "verification"],
        "trust_score": 12
    },
    "node_aphrodite": {
        "node_name": "Aphrodite",
        "domain": "love_beauty",
        "capabilities": ["voting", "verification"],
        "trust_score": 10
    },
    "node_ares": {
        "node_name": "Ares",
        "domain": "war_strategy", 
        "capabilities": ["voting", "verification"],
        "trust_score": 8
    }
}
