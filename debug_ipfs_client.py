#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from core.ipfs_client import IPFSClient
    print("✅ IPFSClient löytyi!")
    
    ipfs = IPFSClient()
    print("✅ IPFSClient instanssi luotu!")
    
    # Listaa kaikki saatavilla olevat metodit
    methods = [method for method in dir(ipfs) if not method.startswith('_')]
    print(f"📋 IPFSClient metodit: {methods}")
    
    # Tarkista tila
    if hasattr(ipfs, 'check_ipfs_connection'):
        status = ipfs.check_ipfs_connection()
        print(f"🌐 IPFS yhteys: {status}")
    else:
        print("❌ check_ipfs_connection ei saatavilla")
        
except Exception as e:
    print(f"❌ Virhe: {e}")
    import traceback
    traceback.print_exc()
