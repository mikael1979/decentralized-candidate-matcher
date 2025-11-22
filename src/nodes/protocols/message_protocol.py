# src/nodes/protocols/message_protocol.py
"""
Message protocols for multinode architecture
Standardized message formats and validation
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional

class MessageProtocol:
    """Standardized message protocol implementation"""
    
    def __init__(self, version: str = "1.0"):
        self.version = version
        self.supported_types = [
            "ping", "pong", "node_announce", "peer_list", 
            "consensus_proposal", "consensus_vote", "consensus_result",
            "data_sync", "error"
        ]
    
    def create_message(self, message_type: str, payload: Dict, 
                      sender_id: str, election_id: str) -> Dict[str, Any]:
        """Create standardized message"""
        if message_type not in self.supported_types:
            raise ValueError(f"Unsupported message type: {message_type}")
        
        message = {
            "protocol_version": self.version,
            "type": message_type,
            "payload": payload,
            "sender": sender_id,
            "election_id": election_id,
            "timestamp": datetime.now().isoformat(),
            "message_id": self._generate_message_id(payload)
        }
        
        return message
    
    def validate_message(self, message: Dict) -> tuple[bool, Optional[str]]:
        """Validate message structure"""
        required_fields = ["protocol_version", "type", "payload", "sender", "timestamp"]
        
        for field in required_fields:
            if field not in message:
                return False, f"Missing required field: {field}"
        
        if message["type"] not in self.supported_types:
            return False, f"Unsupported message type: {message['type']}"
        
        return True, None
    
    def _generate_message_id(self, payload: Dict) -> str:
        """Generate unique message ID"""
        content = json.dumps(payload, sort_keys=True) + str(datetime.now().timestamp())
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def __repr__(self):
        return f"MessageProtocol(v{self.version}, types: {len(self.supported_types)})"

# Simple test
def test_message_protocol():
    """Test MessageProtocol functionality"""
    print("🧪 Testing MessageProtocol...")
    
    protocol = MessageProtocol()
    
    # Test message creation
    message = protocol.create_message(
        "ping", 
        {"data": "test"}, 
        "test_node", 
        "TestElection"
    )
    
    assert message["type"] == "ping"
    assert message["sender"] == "test_node"
    assert "message_id" in message
    
    # Test validation
    valid, error = protocol.validate_message(message)
    assert valid == True
    assert error is None
    
    print("✅ MessageProtocol tests passed!")
    return protocol

if __name__ == "__main__":
    test_message_protocol()
