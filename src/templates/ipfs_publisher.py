#!/usr/bin/env python3
"""
IPFS-julkaisu profiileille - KORJATTU VERSIO
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

class IPFSPublisher:
    """IPFS-julkaisuluokka profiileille"""
    
    def __init__(self, election_id: str = "Jumaltenvaalit2026"):
        self.election_id = election_id
        self.output_dir = Path("output/profiles")
        
        # IPFS-client - KORJATTU: Parempi virheenkäsittely
        try:
            # Yritä ensin absoluuttista importia
            from src.core.ipfs_client import IPFSClient
            self.ipfs_client = IPFSClient.get_client(election_id)
            self.ipfs_available = True
        except ImportError:
            try:
                # Sitten suoraa importia
                from core.ipfs_client import IPFSClient
                self.ipfs_client = IPFSClient.get_client(election_id)
                self.ipfs_available = True
            except Exception:
                self.ipfs_available = False
                self.ipfs_client = None
                print("🔶 IPFS ei saatavilla, käytetään paikallista tallennusta")
    
    def publish_html_to_ipfs(self, html_content: str, filename: str) -> Optional[str]:
        """Julkaise HTML-sisältö IPFS:ään"""
        if not self.ipfs_available:
            mock_cid = f"mock_{filename}_{int(datetime.now().timestamp())}"
            print(f"🔶 Mock IPFS: {mock_cid}")
            return mock_cid
        
        try:
            # Julkaise HTML-sivu suoraan IPFS:ään
            ipfs_cid = self.ipfs_client.publish_html_content(html_content, filename)
            print(f"🌐 Profiili julkaistu IPFS:ään: {ipfs_cid}")
            return ipfs_cid
        except Exception as e:
            print(f"❌ IPFS-julkaisu epäonnistui: {e}")
            return f"mock_fallback_{filename}_{int(datetime.now().timestamp())}"
    
    def save_local_file(self, html_content: str, filename: str) -> str:
        """Tallenna HTML-sisältö paikallisesti"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Profiili tallennettu: {filepath}")
        return str(filepath)
