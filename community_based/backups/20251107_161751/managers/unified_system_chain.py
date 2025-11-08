#!/usr/bin/env python3
"""
Unified System Chain - Yhdistetty system chain ja IPFS-lohkot
Korvaa: system_chain_manager.py + enhanced_system_chain_manager.py
"""

import json
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import List, Optional, Dict, Any
import hashlib

class UnifiedSystemChain:
    """Yhdistetty System Chain - hallitsee perus- ja IPFS-lohkot"""
    
    def __init__(self, runtime_dir: str = "runtime", ipfs_client=None):
        self.runtime_dir = Path(runtime_dir)
        self.ipfs_client = ipfs_client
        self.chain_file = self.runtime_dir / "system_chain.json"
        self.chain_file.parent.mkdir(exist_ok=True)
        
        print("✅ Unified System Chain alustettu")
    
    def log_action(self, action_type: str, description: str, 
                  question_ids: Optional[List[str]] = None,
                  user_id: Optional[str] = None,
                  metadata: Optional[Dict[str, Any]] = None,
                  use_ipfs_blocks: bool = False,
                  election_id: str = None,
                  node_id: str = None,
                  priority: str = "normal") -> Dict[str, Any]:
        """
        Yhdenmukainen API kaikille lokituksille
        
        Returns:
            Dict with success status and entry IDs from both systems
        """
        result = {
            "success": False,
            "basic_chain_entry": None,
            "ipfs_block_entry": None,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            # 1. Perus system_chain kirjaus (aina)
            basic_result = self._log_to_basic_chain(
                action_type, description, question_ids, user_id, metadata
            )
            
            if basic_result["success"]:
                result["success"] = True
                result["basic_chain_entry"] = basic_result["block_id"]
            
            # 2. IPFS-lohkojen kirjaus (jos saatavilla ja käytössä)
            if use_ipfs_blocks and self.ipfs_client and election_id:
                ipfs_result = self._log_to_ipfs_blocks(
                    action_type, description, question_ids, user_id, metadata,
                    election_id, node_id, priority
                )
                
                if ipfs_result["success"]:
                    result["ipfs_block_entry"] = ipfs_result["entry_id"]
                    # Jos IPFS-kirjaus onnistuu, merkitään kokonaistonniksi onnistuneeksi
                    result["success"] = True
        
        except Exception as e:
            print(f"❌ Virhe system chain kirjauksessa: {e}")
            result["error"] = str(e)
        
        return result
    
    def _log_to_basic_chain(self, action_type: str, description: str, 
                           question_ids: Optional[List[str]] = None,
                           user_id: Optional[str] = None,
                           metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Yksinkertainen system_chain kirjaus"""
        try:
            # Lataa nykyinen ketju tai luo uusi
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
            
            # Laske hash edellisestä lohkosta (jos on)
            if len(chain_data["blocks"]) > 1:
                previous_block = chain_data["blocks"][-2]
                new_block["previous_hash"] = self._calculate_block_hash(previous_block)
            
            # Laske uusi hash
            new_block["block_hash"] = self._calculate_block_hash(new_block)
            
            # Tallenna
            if self._save_chain(chain_data):
                print(f"📝 System chain: {action_type} - {description[:50]}...")
                return {
                    "success": True,
                    "block_id": new_block["block_id"],
                    "timestamp": new_block["timestamp"]
                }
            else:
                return {"success": False, "error": "Tallennus epäonnistui"}
                
        except Exception as e:
            print(f"❌ Virhe perus system chain kirjauksessa: {e}")
            return {"success": False, "error": str(e)}
    
    def _log_to_ipfs_blocks(self, action_type: str, description: str,
                           question_ids: Optional[List[str]] = None,
                           user_id: Optional[str] = None,
                           metadata: Optional[Dict[str, Any]] = None,
                           election_id: str = None,
                           node_id: str = None,
                           priority: str = "normal") -> Dict[str, Any]:
        """IPFS-lohkojen kirjaus"""
        try:
            # Yritä käyttää enhanced_system_chain_manageria
            from enhanced_system_chain_manager import log_action_with_blocks
            
            result = log_action_with_blocks(
                action_type=action_type,
                description=description,
                question_ids=question_ids,
                user_id=user_id,
                metadata=metadata,
                ipfs_client=self.ipfs_client,
                election_id=election_id,
                node_id=node_id,
                priority=priority
            )
            
            if result["system_chain"]["success"]:
                print(f"🌐 IPFS-lohko: {action_type} - {description[:50]}...")
                return {
                    "success": True,
                    "entry_id": result["ipfs_blocks"]["entry_id"] if result["ipfs_blocks"] else None
                }
            else:
                return {"success": False, "error": "IPFS-kirjaus epäonnistui"}
                
        except ImportError:
            print("⚠️  Enhanced system chain ei saatavilla - skipataan IPFS-lohkot")
            return {"success": False, "error": "Enhanced system chain ei saatavilla"}
        except Exception as e:
            print(f"❌ Virhe IPFS-lohkojen kirjauksessa: {e}")
            return {"success": False, "error": str(e)}
    
    def _load_chain(self) -> Dict[str, Any]:
        """Lataa system_chain tai luo uusi"""
        if self.chain_file.exists():
            try:
                with open(self.chain_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Virhe ladattaessa system_chainia, luodaan uusi: {e}")
                return self._create_new_chain()
        else:
            return self._create_new_chain()
    
    def _create_new_chain(self) -> Dict[str, Any]:
        """Luo uusi system_chain"""
        # Hae vaalin tiedot metadatasta
        election_id = "unknown_election"
        election_name = "Tuntematon vaali"
        
        try:
            meta_file = Path("runtime/meta.json")
            if meta_file.exists():
                with open(meta_file, 'r', encoding='utf-8') as f:
                    meta_data = json.load(f)
                election_id = meta_data.get('election', {}).get('id', 'unknown_election')
                election_name = meta_data.get('election', {}).get('name', {}).get('fi', 'Tuntematon vaali')
        except:
            pass
        
        return {
            "chain_id": election_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "description": f"System chain vaalille: {election_name}",
            "version": "2.0.0",
            "blocks": [],
            "current_state": {
                "last_updated": None,
                "total_blocks": 0,
                "election_id": election_id,
                "election_name": election_name
            },
            "metadata": {
                "unified_system": True,
                "ipfs_integrated": self.ipfs_client is not None
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
    
    def get_chain_info(self) -> Dict[str, Any]:
        """Hae ketjun tiedot"""
        try:
            chain_data = self._load_chain()
            return {
                "chain_id": chain_data.get("chain_id"),
                "total_blocks": len(chain_data.get("blocks", [])),
                "last_updated": chain_data.get("current_state", {}).get("last_updated"),
                "created_at": chain_data.get("created_at"),
                "election_id": chain_data.get("current_state", {}).get("election_id"),
                "election_name": chain_data.get("current_state", {}).get("election_name"),
                "ipfs_integrated": chain_data.get("metadata", {}).get("ipfs_integrated", False)
            }
        except:
            return {}
    
    def print_status(self):
        """Tulosta ketjun status"""
        info = self.get_chain_info()
        
        print("\n🔗 UNIFIED SYSTEM CHAIN TILA:")
        print("=" * 50)
        print(f"Ketju ID: {info.get('chain_id', 'Ei määritelty')}")
        print(f"Lohkoja: {info.get('total_blocks', 0)}")
        print(f"Viimeisin päivitys: {info.get('last_updated', 'Ei tietoa')}")
        print(f"IPFS-integroitu: {'✅' if info.get('ipfs_integrated') else '❌'}")
        print(f"Vaali: {info.get('election_name', 'Tuntematon')}")

# Singleton instance
_system_chain = None

def get_system_chain(runtime_dir: str = "runtime", ipfs_client=None) -> UnifiedSystemChain:
    """Hae UnifiedSystemChain-instanssi"""
    global _system_chain
    if _system_chain is None:
        _system_chain = UnifiedSystemChain(runtime_dir, ipfs_client)
    return _system_chain

def log_action(action_type: str, description: str, **kwargs):
    """Yksinkertainen API kaikille ohjelmille"""
    chain = get_system_chain()
    return chain.log_action(action_type, description, **kwargs)

# Testaus
if __name__ == "__main__":
    print("🧪 UNIFIED SYSTEM CHAIN TESTI")
    print("=" * 50)
    
    # Testaa ilman IPFS:ää
    chain = UnifiedSystemChain()
    chain.print_status()
    
    # Testaa kirjaus
    result = log_action(
        action_type="test_action",
        description="Testikirjaus unified system chainiin",
        question_ids=["test_q1", "test_q2"],
        user_id="test_user"
    )
    
    print(f"📝 Testikirjaus: {'✅ ONNISTUI' if result['success'] else '❌ EPÄONNISTUI'}")
    if result['success']:
        print(f"   Basic chain entry: {result['basic_chain_entry']}")
        print(f"   IPFS block entry: {result.get('ipfs_block_entry', 'Ei käytössä')}")
    
    chain.print_status()
