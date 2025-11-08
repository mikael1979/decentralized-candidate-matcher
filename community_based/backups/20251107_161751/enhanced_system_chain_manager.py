#!/usr/bin/env python3
# enhanced_system_chain_manager.py
"""
Enhanced System Chain Manager - Laajennettu system chain IPFS-lohkojen kanssa
Käyttö:
  from enhanced_system_chain_manager import log_action_with_blocks
  log_action_with_blocks("comparison", "A voittaa", ["q1", "q2"], "user123", ipfs_client, "election_2024")
"""

import json
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import List, Optional, Dict, Any
import hashlib

class EnhancedSystemChainManager:
    """Laajennettu system chain manager IPFS-lohkojen integraatiolla"""
    
    def __init__(self, chain_file: str = "runtime/system_chain.json", ipfs_client=None):
        self.chain_file = Path(chain_file)
        self.chain_file.parent.mkdir(exist_ok=True)
        self.ipfs_client = ipfs_client
        
    def log_action_with_blocks(self, action_type: str, description: str, 
                             question_ids: Optional[List[str]] = None,
                             user_id: Optional[str] = None,
                             metadata: Optional[Dict[str, Any]] = None,
                             election_id: str = None,
                             node_id: str = None,
                             priority: str = "normal") -> Dict:
        """
        Kirjaa toiminto system_chainiin JA IPFS-lohkoon
        
        Returns:
            Dictionary joka sisältää molemmat entry ID:t
        """
        
        # 1. Kirjaa perinteiseen system_chainiin
        chain_result = self.log_action(
            action_type, description, question_ids, user_id, metadata
        )
        
        # 2. Kirjaa IPFS-lohkoon
        block_result = None
        if self.ipfs_client and election_id:
            try:
                from ipfs_block_manager import IPFSBlockManager
                block_manager = IPFSBlockManager(self.ipfs_client, election_id, node_id or "unknown_node")
                
                block_data = {
                    "action_type": action_type,
                    "description": description,
                    "question_ids": question_ids or [],
                    "user_id": user_id,
                    "metadata": metadata or {},
                    "system_chain_block_id": chain_result.get("block_id"),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                block_entry_id = block_manager.write_to_block(
                    "active" if priority == "normal" else "urgent",
                    block_data,
                    f"system_chain_{action_type}",
                    priority
                )
                
                block_result = {
                    "entry_id": block_entry_id,
                    "block_written": True
                }
                
            except Exception as e:
                block_result = {
                    "entry_id": None,
                    "block_written": False,
                    "error": str(e)
                }
                print(f"⚠️  Ei voitu kirjata IPFS-lohkoon: {e}")
        
        return {
            "system_chain": chain_result,
            "ipfs_blocks": block_result,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def log_action(self, action_type: str, description: str, 
                  question_ids: Optional[List[str]] = None,
                  user_id: Optional[str] = None,
                  metadata: Optional[Dict[str, Any]] = None) -> Dict:
        """
        Perinteinen system_chain kirjaus (yhteensopivuus)
        """
        try:
            # Lataa nykyinen ketju
            chain_data = self._load_chain()
            
            # Luo uusi lohko
            new_block = self._create_block(
                action_type=action_type,
                description=description,
                question_ids=question_ids or [],
                user_id=user_id,
                metadata=metadata or {}
            )
            
            # Lisää lohko ketjuun
            chain_data["blocks"].append(new_block)
            
            # Päivitä nykytila
            chain_data["current_state"]["last_updated"] = new_block["timestamp"]
            chain_data["current_state"]["total_blocks"] = len(chain_data["blocks"])
            
            # Laske hash edellisestä lohkosta
            if len(chain_data["blocks"]) > 1:
                previous_block = chain_data["blocks"][-2]
                new_block["previous_hash"] = self._calculate_block_hash(previous_block)
            
            # Laske uusi hash
            new_block["block_hash"] = self._calculate_block_hash(new_block)
            
            # Tallenna
            self._save_chain(chain_data)
            
            return {
                "success": True,
                "block_id": new_block["block_id"],
                "timestamp": new_block["timestamp"]
            }
            
        except Exception as e:
            print(f"❌ Virhe kirjattaessa system_chainiin: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def recover_chain_from_blocks(self, election_id: str, node_id: str) -> Dict:
        """Palauta system_chain IPFS-lohkoista"""
        
        if not self.ipfs_client:
            return {"success": False, "error": "IPFS-asiakas puuttuu"}
        
        try:
            from ipfs_block_manager import IPFSBlockManager
            block_manager = IPFSBlockManager(self.ipfs_client, election_id, node_id)
            
            # Kerää kaikki system_chain merkinnät lohkoista
            all_chain_entries = []
            
            for block_name in ["urgent", "sync", "active", "buffer2"]:
                entries = block_manager.read_from_block(block_name)
                for entry in entries:
                    if entry.get("data_type", "").startswith("system_chain_"):
                        all_chain_entries.append(entry)
            
            # Lajittele aikajärjestykseen
            sorted_entries = sorted(all_chain_entries, 
                                  key=lambda x: x["timestamp"])
            
            # Luo uusi system_chain
            new_chain = self._create_new_chain()
            new_chain["metadata"]["recovered_from_blocks"] = True
            new_chain["metadata"]["recovery_timestamp"] = datetime.now(timezone.utc).isoformat()
            new_chain["metadata"]["source_election_id"] = election_id
            new_chain["metadata"]["source_node_id"] = node_id
            
            # Lisää lohkot uuteen ketjuun
            for i, entry in enumerate(sorted_entries):
                block_data = entry["data"]
                new_block = self._create_block(
                    action_type=block_data["action_type"],
                    description=block_data["description"],
                    question_ids=block_data["question_ids"],
                    user_id=block_data["user_id"],
                    metadata=block_data["metadata"]
                )
                new_block["block_id"] = i  # Uudet ID:t
                new_block["recovered"] = True
                new_block["original_entry_id"] = entry["entry_id"]
                
                new_chain["blocks"].append(new_block)
            
            # Päivitä hashat
            for i, block in enumerate(new_chain["blocks"]):
                if i > 0:
                    previous_block = new_chain["blocks"][i-1]
                    block["previous_hash"] = self._calculate_block_hash(previous_block)
                block["block_hash"] = self._calculate_block_hash(block)
            
            # Korvaa vanha ketju
            self._save_chain(new_chain)
            
            return {
                "success": True,
                "blocks_recovered": len(sorted_entries),
                "recovery_timestamp": datetime.now(timezone.utc).isoformat(),
                "election_id": election_id,
                "node_id": node_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Ketjun palautus epäonnistui: {e}"
            }
    
    def _load_chain(self) -> Dict[str, Any]:
        """Lataa system_chain tai luo uusi"""
        if self.chain_file.exists():
            with open(self.chain_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return self._create_new_chain()
    
    def _create_new_chain(self) -> Dict[str, Any]:
        """Luo uusi system_chain"""
        return {
            "chain_id": "enhanced_chain",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "description": "Laajennettu system chain IPFS-lohkoilla",
            "version": "2.0.0",
            "metadata": {
                "ipfs_integrated": True,
                "block_recovery_supported": True
            },
            "blocks": [],
            "current_state": {
                "last_updated": None,
                "total_blocks": 0,
                "ipfs_backed": False
            }
        }
    
    def _create_block(self, action_type: str, description: str, 
                     question_ids: List[str], user_id: Optional[str],
                     metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Luo uusi lohko"""
        return {
            "block_id": self._get_next_block_id(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action_type": action_type,
            "description": description,
            "user_id": user_id,
            "question_ids": question_ids,
            "metadata": metadata,
            "previous_hash": None,
            "block_hash": None
        }
    
    def _get_next_block_id(self) -> int:
        """Hae seuraava block_id"""
        try:
            chain_data = self._load_chain()
            return len(chain_data["blocks"])
        except:
            return 0
    
    def _calculate_block_hash(self, block: Dict[str, Any]) -> str:
        """Laske lohkon hash"""
        block_copy = block.copy()
        block_copy.pop("previous_hash", None)
        block_copy.pop("block_hash", None)
        
        block_string = json.dumps(block_copy, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(block_string.encode('utf-8')).hexdigest()
    
    def _save_chain(self, chain_data: Dict[str, Any]) -> bool:
        """Tallenna system_chain"""
        try:
            with open(self.chain_file, 'w', encoding='utf-8') as f:
                json.dump(chain_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Virhe tallennettaessa system_chainia: {e}")
            return False

# Yksinkertaistetut APIt
def log_action_with_blocks(action_type: str, description: str, 
                          question_ids: Optional[List[str]] = None,
                          user_id: Optional[str] = None,
                          metadata: Optional[Dict[str, Any]] = None,
                          ipfs_client=None,
                          election_id: str = None,
                          node_id: str = None,
                          priority: str = "normal") -> Dict:
    """
    Yksinkertainen API system_chainin ja IPFS-lohkojen kirjaamiseen
    """
    manager = EnhancedSystemChainManager(ipfs_client=ipfs_client)
    return manager.log_action_with_blocks(
        action_type, description, question_ids, user_id, metadata, 
        election_id, node_id, priority
    )

def recover_chain_from_blocks(ipfs_client, election_id: str, node_id: str) -> Dict:
    """Palauta system_chain IPFS-lohkoista"""
    manager = EnhancedSystemChainManager(ipfs_client=ipfs_client)
    return manager.recover_chain_from_blocks(election_id, node_id)

# Testaus
if __name__ == "__main__":
    print("🧪 ENHANCED SYSTEM CHAIN MANAGER TESTI")
    print("=" * 50)
    
    from mock_ipfs import MockIPFS
    
    ipfs = MockIPFS()
    manager = EnhancedSystemChainManager(ipfs_client=ipfs)
    
    # Testaa perinteinen kirjaus
    result1 = manager.log_action(
        "test_action", 
        "Testikirjaus ilman IPFS:ää",
        ["q1", "q2"], 
        "test_user"
    )
    print(f"✅ Perinteinen kirjaus: {result1['success']}")
    
    # Testaa laajennettu kirjaus
    result2 = manager.log_action_with_blocks(
        "test_action_with_blocks",
        "Testikirjaus IPFS-lohkoilla",
        ["q3", "q4"],
        "test_user_2",
        {"test": "metadata"},
        "test_election_2024",
        "test_node_1",
        "normal"
    )
    print(f"✅ Laajennettu kirjaus: {result2['system_chain']['success']}")
    if result2['ipfs_blocks']:
        print(f"   IPFS-lohko: {result2['ipfs_blocks']['block_written']}")
    
    print("🎯 KÄYTTÖESIMERKKEJÄ:")
    print("""
# 1. Normaali kirjaus IPFS-lohkoihin
result = log_action_with_blocks(
    action_type="comparison",
    description="A voittaa: Kysymys1 vs Kysymys2",
    question_ids=["q1", "q2"],
    user_id="user123",
    ipfs_client=ipfs_client,
    election_id="election_2024",
    node_id="node_1"
)

# 2. Kiireellinen kirjaus
result = log_action_with_blocks(
    action_type="emergency_backup",
    description="Hätävaraus järjestelmän kaaduttua",
    user_id="system",
    ipfs_client=ipfs_client, 
    election_id="election_2024",
    node_id="node_1",
    priority="emergency"
)

# 3. Ketjun palautus
recovery = recover_chain_from_blocks(
    ipfs_client=ipfs_client,
    election_id="election_2024", 
    node_id="node_1"
)
    """)
