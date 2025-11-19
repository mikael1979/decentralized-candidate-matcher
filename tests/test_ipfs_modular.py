# tests/test_ipfs_modular.py
"""
Testaa uusia IPFS moduuleja
"""
import json
import sys
import os

# Lisää projekti Python-polkuun
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.ipfs.client import IPFSClient
from src.core.ipfs.sync_orchestrator import SyncOrchestrator

def test_modular_sync():
    """Testaa koko modulaarista synkronointiprosessia"""
    
    # Alusta client ja orchestrator
    client = IPFSClient()
    orchestrator = SyncOrchestrator("test_election", client)
    
    # Testidata
    initial_data = {
        "questions.json": {"q1": "Mitä mieltä olet?", "q2": "Mikä on lempivärisi?"},
        "candidates.json": {"c1": "Matti", "c2": "Liisa"}
    }
    
    print("🧪 TEST 1: First sync (full archive)")
    cid1 = orchestrator.sync_data(initial_data)
    print(f"   CID: {cid1}")
    
    print("🧪 TEST 2: Small change (delta sync)")
    updated_data = initial_data.copy()
    updated_data["questions.json"]["q2"] = "Mikä on lempieläimesi?"  # Pieni muutos
    
    cid2 = orchestrator.sync_data(updated_data)
    print(f"   CID: {cid2}")
    
    print("🧪 TEST 3: Load data back")
    loaded_data = orchestrator.load_data(cid2)
    print(f"   Loaded files: {list(loaded_data.keys())}")
    
    print("🧪 TEST 4: Statistics")
    stats = orchestrator.get_sync_statistics()
    print(f"   Full syncs: {stats.get('sync_count')}")
    print(f"   Delta syncs: {stats.get('delta_count')}")
    print(f"   Total savings: {stats.get('total_savings_bytes')} bytes")
    
    print("✅ All tests completed!")

if __name__ == "__main__":
    test_modular_sync()
