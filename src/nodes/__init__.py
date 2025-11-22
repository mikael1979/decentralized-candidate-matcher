# src/nodes/__init__.py
"""
Multi-node modules for decentralized candidate matcher
"""

__version__ = "2.0.0"
__author__ = "Hajautettu Vaalikone Team"

# Legacy imports (existing functionality)
from .node_manager import NodeManager, OLYMPIAN_NODES
from .network_sync import NetworkSyncManager
from .quorum_voting import QuorumVoting

# New multinode architecture imports
from .core.node_identity import NodeIdentity
from .core.network_manager import NetworkManager
from .protocols.consensus import ConsensusManager
from .discovery.peer_discovery import PeerDiscovery

__all__ = [
    # Legacy
    'NodeManager',
    'OLYMPIAN_NODES', 
    'NetworkSyncManager',
    'QuorumVoting',
    
    # New multinode architecture
    'NodeIdentity',
    'NetworkManager', 
    'ConsensusManager',
    'PeerDiscovery'
]
