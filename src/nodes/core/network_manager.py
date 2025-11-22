class NetworkManager:
    """Network management (minimal implementation for testing)"""
    
    def __init__(self, identity):
        self.identity = identity
    
    def __repr__(self):
        return f"NetworkManager({self.identity.node_id})"