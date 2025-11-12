#!/usr/bin/env python3
"""
Nodejen välinen data-synkronointi
"""
import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

class NetworkSyncManager:
    def __init__(self, election_id: str = "Jumaltenvaalit2026"):
        self.election_id = election_id
        self.sync_file = Path(f"data/nodes/{election_id}_network_sync.json")
        self.sync_file.parent.mkdir(parents=True, exist_ok=True)
    
    def sync_with_nodes(self, target_nodes: List[Dict]) -> Dict:
        """Synkronoi data muiden nodejen kanssa"""
        print(f"🔄 Synkronoidaan {len(target_nodes)} noden kanssa...")
        
        sync_results = {
            "election_id": self.election_id,
            "sync_timestamp": datetime.now().isoformat(),
            "target_nodes": len(target_nodes),
            "successful_syncs": 0,
            "failed_syncs": 0,
            "node_results": []
        }
        
        for node in target_nodes:
            node_result = self._sync_with_single_node(node)
            sync_results["node_results"].append(node_result)
            
            if node_result["status"] == "success":
                sync_results["successful_syncs"] += 1
            else:
                sync_results["failed_syncs"] += 1
        
        # Tallenna synkronointitulokset
        self._save_sync_results(sync_results)
        
        print(f"✅ Synkronointi valmis: {sync_results['successful_syncs']}/{sync_results['target_nodes']}")
        return sync_results
    
    def _sync_with_single_node(self, node: Dict) -> Dict:
        """Synkronoi yhden noden kanssa (mock-toteutus)"""
        try:
            # Mock-synkronointi - oikeassa järjestelmässä verrattaisiin IPFS-CID:itä
            node_result = {
                "node_id": node["node_id"],
                "node_name": node["node_name"],
                "sync_timestamp": datetime.now().isoformat(),
                "status": "success",
                "data_consistent": True,
                "message": "Mock sync completed successfully"
            }
            
            # Simuloi data-vertailu
            if node["node_id"] in ["node_zeus", "node_athena"]:
                node_result["data_consistent"] = True
                node_result["message"] = "Data consistent with trusted node"
            else:
                node_result["data_consistent"] = True  # Oletus mock-tilassa
                node_result["message"] = "Data verification completed"
            
            return node_result
            
        except Exception as e:
            return {
                "node_id": node["node_id"],
                "node_name": node["node_name"], 
                "sync_timestamp": datetime.now().isoformat(),
                "status": "failed",
                "error": str(e),
                "message": f"Sync failed: {e}"
            }
    
    def _save_sync_results(self, sync_results: Dict):
        """Tallenna synkronointitulokset"""
        with open(self.sync_file, 'w', encoding='utf-8') as f:
            json.dump(sync_results, f, indent=2, ensure_ascii=False)
    
    def get_sync_status(self) -> Optional[Dict]:
        """Hae viimeisin synkronointitila"""
        if self.sync_file.exists():
            with open(self.sync_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
