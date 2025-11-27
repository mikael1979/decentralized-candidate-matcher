"""
session_manager.py - Voting session core management with multinode support
"""
import json
import uuid
from datetime import datetime
from pathlib import Path

# Importoi tarvittavat moduulit
try:
    from src.core import get_election_id, get_data_path
    from src.core.file_utils import read_json_file, write_json_file
except ImportError:
    # Fallback jos importit eivät toimi
    def get_election_id(election_param=None):
        return election_param or "test_election"
    
    def get_data_path(election_id):
        return Path(f"data/elections/{election_id}")
    
    def read_json_file(file_path, default=None):
        return default or {}
    
    def write_json_file(file_path, data):
        pass

# Multinode availability check
try:
    from nodes.core.node_identity import NodeIdentity
    from nodes.core.network_manager import NetworkManager
    from nodes.protocols.consensus import ConsensusManager
    MULTINODE_AVAILABLE = True
except ImportError:
    MULTINODE_AVAILABLE = False

class VotingSessionManager:
    """Voting session management with multinode support"""
    
    def __init__(self, election_id=None, enable_multinode=False):
        self.election_id = election_id or get_election_id()
        self.data_path = get_data_path(self.election_id)
        
        # MULTINODE: Alusta node-järjestelmä
        self.enable_multinode = enable_multinode
        self.node_identity = None
        self.network_manager = None
        self.consensus_manager = None
        
        # Perus session-hallinta
        self.sessions = {}
        self.current_session = None
        
        if self.enable_multinode and MULTINODE_AVAILABLE:
            self._initialize_multinode()
    
    def _initialize_multinode(self):
        """Alustaa multinode-järjestelmän voting-sessioihin"""
        try:
            print("🌐 Alustetaan multinode-voting...")
            
            # Lataa olemassa oleva node identity tai luo uusi
            self.node_identity = self._load_or_create_node_identity()
            
            # Luo verkkomanageri
            self.network_manager = NetworkManager(self.node_identity)
            
            # Luo konsensusmanageri
            self.consensus_manager = ConsensusManager(self.network_manager)
            
            # Yhdistä verkkoon (tyhjät bootstrap-peerit voting-sessioille)
            self.network_manager.connect_to_network([])
            
            print(f"✅ Multinode voting alustettu: {self.node_identity.node_id}")
            
        except Exception as e:
            print(f"⚠️  Multinode initialization failed: {e}")
            self.enable_multinode = False
    
    def _load_or_create_node_identity(self):
        """Lataa olemassa oleva node identity tai luo uusi"""
        try:
            # Yritä ladata olemassa oleva identity
            identity_files = list(Path(f"data/nodes/{self.election_id}").glob("*_identity.json"))
            if identity_files:
                latest_file = max(identity_files, key=lambda f: f.stat().st_mtime)
                identity = NodeIdentity(self.election_id, "voter")
                if identity.load_identity(latest_file.stem.replace("_identity", "")):
                    print(f"✅ Loaded existing node identity: {identity.node_id}")
                    return identity
            
            # Luo uusi identity
            identity = NodeIdentity(self.election_id, "voter")
            identity.generate_identity()
            identity.save_identity()
            print(f"✅ Created new node identity: {identity.node_id}")
            return identity
            
        except Exception as e:
            print(f"❌ Node identity creation failed: {e}")
            raise
    
    def create_session(self, session_data):
        """Create new voting session"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            'id': session_id,
            'created': datetime.now().isoformat(),
            'data': session_data,
            'results': None
        }
        self.current_session = session_id
        return session_id
    
    def get_session(self, session_id):
        """Get voting session by ID"""
        return self.sessions.get(session_id)
    
    def save_session(self, session_id, results):
        """Save session results"""
        if session_id in self.sessions:
            self.sessions[session_id]['results'] = results
            self.sessions[session_id]['completed'] = datetime.now().isoformat()
            return True
        return False
    
    def list_sessions(self):
        """List all voting sessions"""
        return list(self.sessions.keys())
