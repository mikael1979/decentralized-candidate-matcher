# src/nodes/core/__init__.py
"""
Core node functionality and identity management
"""

from .node_identity import NodeIdentity
from .network_manager import NetworkManager

__all__ = ['NodeIdentity', 'NetworkManager']
