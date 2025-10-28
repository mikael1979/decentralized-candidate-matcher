#!/usr/bin/env python3
"""
System Chain Manager - Modulaarinen system_chainin hallinta
Käyttö: 
  from system_chain_manager import log_action
  log_action("comparison", "A voittaa: Kysymys1 vs Kysymys2", ["q1", "q2"], "user123")
"""

import json
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import List, Optional, Dict, Any
import hashlib

class SystemChainManager:
    """Hallinnoi system_chain.json tiedostoa ja tarjoaa yksinkertaisen APIn"""
    
    def __init__(self, chain_file: str = "runtime/system_chain.json"):
        self.chain_file = Path(chain_file)
        self.chain_file.parent.mkdir(exist_ok=True)  # Varmista hakemisto
    
    def log_action(self, action_type: str, description: str, 
                  question_ids: Optional[List[str]] = None,
                  user_id: Optional[str] = None,
                  metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Kirjaa toiminnon system_chainiin
        
        Args:
            action_type: Toiminnon tyyppi (comparison, vote, question_add, sync, etc.)
            description: Kuvaus toiminnosta
            question_ids: Lista kysymys-ID:istä joihin toiminto liittyy
            user_id: Käyttäjän ID
            metadata: Lisämetadatat
            
        Returns:
            True jos onnistui, False jos epäonnistui
        """
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
            
            # Laska hash edellisestä lohkosta (jos on)
            if len(chain_data["blocks"]) > 1:
                previous_block = chain_data["blocks"][-2]
                new_block["previous_hash"] = self._calculate_block_hash(previous_block)
            
            # Laske uusi hash
            new_block["block_hash"] = self._calculate_block_hash(new_block)
            
            # Tallenna
            return self._save_chain(chain_data)
            
        except Exception as e:
            print(f"❌ Virhe kirjattaessa system_chainiin: {e}")
            return False
    
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
            "chain_id": "default_chain",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "description": "Automaattisesti luotu system chain",
            "version": "1.0.0",
            "blocks": [],
            "current_state": {
                "last_updated": None,
                "total_blocks": 0
            },
            "metadata": {
                "algorithm": "sha256",
                "created_by": "SystemChainManager"
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
        # Poista hash kentät laskennasta
        block_copy = block.copy()
        block_copy.pop("previous_hash", None)
        block_copy.pop("block_hash", None)
        
        # Muunna JSONiksi ja laske hash
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
                "created_at": chain_data.get("created_at")
            }
        except:
            return {}
    
    def print_chain_status(self):
        """Tulosta ketjun status"""
        info = self.get_chain_info()
        
        print("\n🔗 SYSTEM_CHAIN TILA:")
        print("=" * 50)
        print(f"Ketju ID: {info.get('chain_id', 'Ei määritelty')}")
        print(f"Lohkoja: {info.get('total_blocks', 0)}")
        print(f"Viimeisin päivitys: {info.get('last_updated', 'Ei tietoa')}")
        print(f"Luotu: {info.get('created_at', 'Ei tietoa')}")

# Singleton instance
_system_chain_manager = None

def get_system_chain_manager(chain_file: str = "runtime/system_chain.json") -> SystemChainManager:
    """Hae SystemChainManager-instanssi"""
    global _system_chain_manager
    if _system_chain_manager is None:
        _system_chain_manager = SystemChainManager(chain_file)
    return _system_chain_manager

def log_action(action_type: str, description: str, 
              question_ids: Optional[List[str]] = None,
              user_id: Optional[str] = None,
              metadata: Optional[Dict[str, Any]] = None) -> bool:
    """
    Yksinkertainen API system_chainin kirjaamiseen
    
    Args:
        action_type: Toiminnon tyyppi
        description: Kuvaus
        question_ids: Lista kysymys-ID:istä
        user_id: Käyttäjän ID
        metadata: Lisämetadatat
        
    Returns:
        True jos onnistui
    """
    manager = get_system_chain_manager()
    return manager.log_action(action_type, description, question_ids, user_id, metadata)

# Testaus jos suoritetaan suoraan
if __name__ == "__main__":
    manager = SystemChainManager()
    manager.print_chain_status()
