class PeerDiscovery:
    """Peer discovery (minimal implementation for testing)"""
    
    def __init__(self, election_id: str = "test"):
        self.election_id = election_id
    
    def __repr__(self):
        return f"PeerDiscovery({self.election_id})"