class ConsensusManager:
    """Consensus management (minimal implementation for testing)"""
    
    def __init__(self, network_manager):
        self.network = network_manager
    
    def __repr__(self):
        return f"ConsensusManager({self.network.identity.node_id})"