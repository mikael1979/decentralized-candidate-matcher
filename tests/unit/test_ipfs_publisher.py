#!/usr/bin/env python3
"""
Testit IPFSPublisher-luokalle - KORJATTU VERSIO
"""
import pytest
import tempfile
from unittest.mock import Mock, patch
from pathlib import Path
from src.templates.ipfs_publisher import IPFSPublisher

class TestIPFSPublisher:
    """Testit IPFSPublisher-luokalle"""
    
    def setup_method(self):
        """Testien alustus"""
        self.election_id = "Testivaali2026"
    
    def test_publish_html_to_ipfs_mock_mode(self):
        """Testaa HTML-julkaisu mock-tilassa"""
        publisher = IPFSPublisher(self.election_id)
        publisher.ipfs_available = False
        
        html_content = "<html><body>Testi</body></html>"
        filename = "test_party.html"
        
        cid = publisher.publish_html_to_ipfs(html_content, filename)
        
        assert cid.startswith("mock_test_party.html_")
    
    def test_save_local_file(self):
        """Testaa paikallinen tiedostontalennus"""
        with tempfile.TemporaryDirectory() as temp_dir:
            publisher = IPFSPublisher(self.election_id)
            publisher.output_dir = Path(temp_dir) / "profiles"
            
            html_content = "<html><body>Testisisältö</body></html>"
            filename = "test_save.html"
            
            filepath = publisher.save_local_file(html_content, filename)
            
            expected_path = str(Path(temp_dir) / "profiles" / filename)
            assert filepath == expected_path
            
            with open(filepath, 'r', encoding='utf-8') as f:
                saved_content = f.read()
            
            assert saved_content == html_content
