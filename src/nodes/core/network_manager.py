"""
Network management for multinode architecture
Extends existing NetworkSyncManager functionality
"""

import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path

class NetworkManager:
    """Complete network management implementation"""
    
    def __init__(self, identity):
        self.identity = identity
        self.peers = {}  # node_id -> peer_info
        self.message_handlers = {}
        self.message_queue = []
        self.connection_status = "disconnected"
        
        # Statistics
        self.messages_sent = 0
        self.messages_received = 0
        self.connection_attempts = 0
        
        # Setup default handlers
        self.setup_default_handlers()
    
    def setup_default_handlers(self):
        """Setup default message handlers"""
        self.message_handlers = {
            "ping": self._handle_ping,
            "pong": self._handle_pong,
            "node_announce": self._handle_node_announce,
            "peer_list": self._handle_peer_list,
            "vote_proposal": self._handle_vote_proposal,
            "data_sync": self._handle_data_sync
        }
    
    def connect_to_network(self, bootstrap_peers: List[Dict] = None) -> bool:
        """Connect to the network using bootstrap peers"""
        print(f"🌐 Connecting {self.identity.node_id} to network...")
        
        self.connection_attempts += 1
        
        # Mock connection process
        if bootstrap_peers:
            for peer in bootstrap_peers:
                self.add_peer(peer)
        
        # Simulate connection delay
        time.sleep(0.5)
        
        self.connection_status = "connected"
        print(f"✅ {self.identity.node_id} connected to network with {len(self.peers)} peers")
        return True
    
    def disconnect_from_network(self):
        """Disconnect from network"""
        print(f"🌐 Disconnecting {self.identity.node_id} from network...")
        self.connection_status = "disconnected"
        self.peers.clear()
        print("✅ Disconnected from network")
    
    def add_peer(self, peer_identity):
        """Add peer to network"""
        peer_info = {
            "identity": peer_identity,
            "last_seen": datetime.now().isoformat(),
            "connection_status": "connected",
            "message_count": 0
        }
        
        self.peers[peer_identity.node_id] = peer_info
        print(f"✅ Added peer: {peer_identity.node_id}")
    
    def remove_peer(self, node_id: str):
        """Remove peer from network"""
        if node_id in self.peers:
            del self.peers[node_id]
            print(f"✅ Removed peer: {node_id}")
            return True
        return False
    
    def get_peer_count(self) -> int:
        """Get number of connected peers - FIXED METHOD"""
        return len(self.peers)
    
    def broadcast_message(self, message_type: str, payload: Dict, exclude_nodes: List[str] = None):
        """Broadcast message to all peers"""
        if self.connection_status != "connected":
            print("❌ Cannot broadcast - not connected to network")
            return
        
        exclude_nodes = exclude_nodes or []
        
        message = {
            "type": message_type,
            "payload": payload,
            "sender": self.identity.node_id,
            "timestamp": datetime.now().isoformat(),
            "election_id": self.identity.election_id,
            "message_id": f"msg_{int(time.time())}_{hash(str(payload))[:8]}"
        }
        
        # Sign message if we have crypto capabilities
        if hasattr(self.identity, 'crypto_manager'):
            message["signature"] = self.identity.crypto_manager.sign_data(
                self.identity.keys["private_key"], payload
            )
        
        sent_count = 0
        for peer_id, peer_info in self.peers.items():
            if peer_id not in exclude_nodes:
                self._send_to_peer(peer_info, message)
                sent_count += 1
        
        self.messages_sent += sent_count
        print(f"📤 Broadcast '{message_type}' to {sent_count} peers")
    
    def send_message(self, target_node_id: str, message_type: str, payload: Dict) -> bool:
        """Send message to specific peer"""
        if target_node_id not in self.peers:
            print(f"❌ Target peer not found: {target_node_id}")
            return False
        
        message = {
            "type": message_type,
            "payload": payload,
            "sender": self.identity.node_id,
            "target": target_node_id,
            "timestamp": datetime.now().isoformat(),
            "election_id": self.identity.election_id
        }
        
        peer_info = self.peers[target_node_id]
        self._send_to_peer(peer_info, message)
        self.messages_sent += 1
        
        return True
    
    def _send_to_peer(self, peer_info: Dict, message: Dict):
        """Send message to specific peer (mock implementation)"""
        # Mock implementation - in real system this would use WebSocket/REST
        peer_identity = peer_info["identity"]
        peer_info["last_seen"] = datetime.now().isoformat()
        peer_info["message_count"] += 1
        
        print(f"📤 [{self.identity.node_id}] → [{peer_identity.node_id}]: {message['type']}")
        
        # Simulate network delay
        time.sleep(0.1)
        
        # In real system, this would actually send the message
        # For now, we'll just log it
    
    def process_incoming_message(self, message: Dict):
        """Process incoming message from network"""
        self.messages_received += 1
        
        message_type = message.get("type")
        handler = self.message_handlers.get(message_type)
        
        if handler:
            try:
                handler(message)
                print(f"📥 Processed {message_type} from {message.get('sender')}")
            except Exception as e:
                print(f"❌ Error processing {message_type}: {e}")
        else:
            print(f"⚠️  No handler for message type: {message_type}")
    
    # Message handlers
    def _handle_ping(self, message: Dict):
        """Handle ping message"""
        response_payload = {
            "original_ping": message.get("payload", {}),
            "response_time": datetime.now().isoformat()
        }
        
        # Send pong response
        sender = message.get("sender")
        if sender:
            self.send_message(sender, "pong", response_payload)
    
    def _handle_pong(self, message: Dict):
        """Handle pong message"""
        print(f"🏓 Pong received from {message.get('sender')}")
    
    def _handle_node_announce(self, message: Dict):
        """Handle node announcement"""
        node_data = message.get("payload", {})
        print(f"📢 Node announcement from {node_data.get('node_id')}")
    
    def _handle_peer_list(self, message: Dict):
        """Handle peer list update"""
        peers = message.get("payload", {}).get("peers", [])
        print(f"📋 Received peer list with {len(peers)} peers")
    
    def _handle_vote_proposal(self, message: Dict):
        """Handle vote proposal"""
        proposal_data = message.get("payload", {})
        print(f"🗳️ Vote proposal: {proposal_data.get('proposal_id', 'unknown')}")
    
    def _handle_data_sync(self, message: Dict):
        """Handle data synchronization"""
        sync_data = message.get("payload", {})
        print(f"🔄 Data sync: {sync_data.get('data_type', 'unknown')}")
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Get network statistics"""
        return {
            "node_id": self.identity.node_id,
            "connection_status": self.connection_status,
            "peer_count": self.get_peer_count(),  # Use the fixed method
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "connection_attempts": self.connection_attempts,
            "active_handlers": len(self.message_handlers)
        }
    
    def register_message_handler(self, message_type: str, handler: Callable):
        """Register custom message handler"""
        self.message_handlers[message_type] = handler
        print(f"✅ Registered handler for '{message_type}'")
    
    def __repr__(self):
        return f"NetworkManager({self.identity.node_id}, peers: {self.get_peer_count()}, status: {self.connection_status})"


# Simple test that works when running module directly
def test_network_manager_direct():
    """Simple test for NetworkManager when running module directly"""
    print("🧪 Testing NetworkManager (direct execution)...")
    
    # Create a simple mock identity for testing
    class MockIdentity:
        def __init__(self):
            self.node_id = "test_node_123"
            self.election_id = "TestElection"
            self.node_type = "coordinator"
    
    # Test basic functionality
    mock_identity = MockIdentity()
    network = NetworkManager(mock_identity)
    
    # Test basic methods
    assert network.get_peer_count() == 0
    assert network.connection_status == "disconnected"
    
    # Test connection
    result = network.connect_to_network()
    assert result == True
    assert network.connection_status == "connected"
    
    # Test network stats
    stats = network.get_network_stats()
    assert stats["peer_count"] == 0
    assert stats["connection_status"] == "connected"
    
    print("✅ NetworkManager basic functionality works!")
    print(f"   Peer count: {network.get_peer_count()}")
    print(f"   Status: {network.connection_status}")
    print(f"   Messages sent: {network.messages_sent}")
    
    return network


if __name__ == "__main__":
    test_network_manager_direct()
