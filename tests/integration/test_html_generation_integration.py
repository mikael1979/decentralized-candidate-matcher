"""
Integration tests for HTML generation.
"""
import tempfile
import unittest
from pathlib import Path
from src.templates.html_generator import HTMLProfileGenerator

class TestHTMLGenerationIntegration(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.generator = HTMLProfileGenerator()
        # Aseta output directory
        if hasattr(self.generator, 'profile_manager'):
            self.generator.profile_manager.output_dir = Path(self.temp_dir) / "profiles"

    def test_full_party_profile_generation(self):
        """Test generating a complete party profile."""
        party_data = {
            'name': 'Testipuolue',
            'slogan': 'Testi on paras',
            'founded_year': '2020',
            'chairperson': 'Testi Testinen',
            'website': 'https://example.com',
            'platform': ['Testi idea 1', 'Testi idea 2'],
            'candidates': [
                {
                    'name': 'Esko Ehdokas',
                    'age': 35,
                    'profession': 'Testaaja',
                    'campaign_theme': 'Laadukas testaus',
                    'platform_points': ['Testaus on tärkeää', 'Laatua kaikille']
                }
            ],
            'election_date': '2023-03-01'
        }
        
        # Test generating HTML
        result = self.generator.generate_and_publish_party_profile(party_data)
        
        # Check that result contains expected keys
        self.assertIn('html_content', result)
        self.assertIn('css_content', result)
        self.assertIn('ipfs_hash', result)
        
        # Check that HTML contains party name
        self.assertIn('Testipuolue', result['html_content'])
