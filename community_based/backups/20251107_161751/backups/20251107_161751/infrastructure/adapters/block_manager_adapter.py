#!/usr/bin/env python3
"""
Block Manager Adapter - Adapts the existing IPFSBlockManager to new interface
"""

from typing import List, Dict, Optional
from domain.value_objects import CID

class BlockManagerAdapter:
    """Adapter for IPFSBlockManager to work with new architecture"""
    
    def __init__(self, ipfs_block_manager):
        self.block_manager = ipfs_block_manager
    
    def write_to_block(self, block_name: str, data: Dict, data_type: str, priority: str = "normal") -> str:
        """Write data to IPFS block"""
        return self.block_manager.write_to_block(block_name, data, data_type, priority)
    
    def read_from_block(self, block_name: str, entry_id: Optional[str] = None) -> List[Dict]:
        """Read data from IPFS block"""
        return self.block_manager.read_from_block(block_name, entry_id)
    
    def get_block_status(self, block_name: Optional[str] = None) -> Dict:
        """Get block status"""
        return self.block_manager.get_block_status(block_name)
    
    def initialize_blocks(self) -> CID:
        """Initialize IPFS blocks"""
        metadata_cid = self.block_manager.initialize_blocks()
        return CID(metadata_cid)
    
    def get_namespace_info(self) -> Dict:
        """Get namespace information"""
        return self.block_manager.get_namespace_info()
    
    def verify_namespace_integrity(self) -> bool:
        """Verify namespace integrity"""
        return self.block_manager.verify_namespace_integrity()
