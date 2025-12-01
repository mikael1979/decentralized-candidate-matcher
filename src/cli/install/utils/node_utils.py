"""
Node-initialization toiminnot.
"""
from pathlib import Path
from datetime import datetime

# Import riippuvuudet
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from nodes.core.node_identity import NodeIdentity
    MULTINODE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Multinode modules not available: {e}")
    MULTINODE_AVAILABLE = False


def initialize_node(election_id, node_type, node_name=None):
    """
    Alusta node
    
    Args:
        election_id: Vaalin tunniste
        node_type: Solmun tyyppi
        node_name: Solmun nimi (valinnainen)
        
    Returns:
        NodeIdentity tai None
    """
    if not MULTINODE_AVAILABLE:
        print("⚠️  Multinode not available, skipping node initialization")
        return None
    
    try:
        print("🌐 Alustetaan node...")
        
        # Tarkista onko node jo olemassa
        nodes_dir = Path(f"data/nodes/{election_id}")
        if nodes_dir.exists():
            identity_files = list(nodes_dir.glob("*_identity.json"))
            if identity_files:
                print("ℹ️  Node identity already exists, using existing")
                latest_file = max(identity_files, key=lambda f: f.stat().st_mtime)
                existing_identity = NodeIdentity(election_id, node_type)
                if existing_identity.load_identity(latest_file.stem.replace("_identity", "")):
                    print(f"✅ Loaded existing node: {existing_identity.node_id}")
                    return existing_identity
        
        # Luo uusi node-identiteetti
        if not node_name:
            node_name = f"{node_type}_{election_id}_{datetime.now().strftime('%H%M%S')}"
            
        identity = NodeIdentity(
            election_id=election_id,
            node_type=node_type,
            node_name=node_name,
            domain="election_network"
        )
        
        identity.save_identity()
        print(f"✅ Node identity created: {identity.node_id}")
        return identity
        
    except Exception as e:
        print(f"❌ Node initialization failed: {e}")
        return None
