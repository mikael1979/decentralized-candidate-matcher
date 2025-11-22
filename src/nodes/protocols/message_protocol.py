class MessageProtocol:
    """Message protocol (minimal implementation for testing)"""
    
    def __init__(self):
        self.version = "1.0"
    
    def __repr__(self):
        return f"MessageProtocol({self.version})"