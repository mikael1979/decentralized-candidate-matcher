#!/usr/bin/env python3
"""
Integraatiotestit HTML-generoinnille
"""
import pytest
import json
import tempfile
from pathlib import Path
from src.templates.html_generator import HTMLProfileGenerator

class TestHTMLGenerationIntegration:
    """Integraatiotestit HTML-generoinnille"""
    
    def setup_method(self):
        """Testien alustus"""
        self.temp_dir = tempfile.mkdtemp()
        self.election_id = "Testivaali2026"
        self.generator = HTMLProfileGenerator(self.election_id)
        
        # Ohjaa output väliaikaiseen hakemistoon
        self.generator.profile_manager.output_dir = Path(self.temp_dir) / "profiles"
        self.generator.profile_manager.metadata_file = Path(self.temp_dir) / "profiles_metadata.json"
    
    def teardown_method(self):
        """Testien siivous"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_full_party_profile_generation(self):
        """Testaa koko puolueprofiilin generointiprosessi"""
        party_data = {
            "party_id": "party_integration_test",
            "name": {"fi": "Integraatiotestipuolue", "en": "Integration Test Party", "sv": "Integrationstestparti"},
            "description": {"fi": "Testaa koko prosessia", "en": "Test the whole process", "sv": "Testa hela processen"},
            "registration": {
                "verification_status": "verified",
                "verified_by": ["node_1", "node_2", "node_3"],
                "verification_timestamp": "2024-01-01T12:00:00"
            },
            "candidates": ["cand_1", "cand_2"],
            "metadata": {
                "contact_email": "integration@example.com",
                "website": "https://integration.example.com",
                "founding_year": "2024"
            }
        }
        
        # Generoi profiili
        metadata = self.generator.generate_and_publish_party_profile(party_data)
        
        # Tarkista metadata
        assert metadata["entity_id"] == "party_integration_test"
        assert metadata["entity_type"] == "party"
        assert metadata["entity_name"] == "Integraatiotestipuolue"
        assert metadata["election_id"] == self.election_id
        
        # Tarkista että HTML-tiedosto luotiin
        html_file = Path(metadata["filepath"])
        assert html_file.exists()
        
        # Tarkista HTML-sisältö
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        assert "Integraatiotestipuolue" in html_content
        assert "integration@example.com" in html_content
        assert "https://integration.example.com" in html_content
        
        # Tarkista että metadata tallennettiin
        assert self.generator.profile_manager.metadata_file.exists()
        
        with open(self.generator.profile_manager.metadata_file, 'r', encoding='utf-8') as f:
            saved_metadata = json.load(f)
        
        assert "party_party_integration_test" in saved_metadata["profiles"]
    
    def test_base_json_generation(self):
        """Testaa base.json generointia"""
        # Generoi base.json
        base_file = self.generator.save_base_json()
        
        assert Path(base_file).exists()
        
        # Tarkista base.json sisältö
        with open(base_file, 'r', encoding='utf-8') as f:
            base_data = json.load(f)
        
        assert base_data["metadata"]["election_id"] == self.election_id
        assert "links" in base_data
        assert "ipfs_cids" in base_data
        assert "profiles" in base_data
        assert "statistics" in base_data
