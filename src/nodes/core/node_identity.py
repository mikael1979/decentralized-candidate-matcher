class NodeIdentity:
    """Node identity management (minimal implementation for testing)"""
    
    def __init__(self, election_id: str = "test", node_type: str = "worker"):
        self.election_id = election_id
        self.node_type = node_type
        self.node_id = f"test_node_{election_id}"
    
    def __repr__(self):
        return f"NodeIdentity({self.node_id}, {self.node_type})"