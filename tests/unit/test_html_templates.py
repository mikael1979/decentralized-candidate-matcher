"""
Unit tests for HTML templates using JSON templates.
"""
import unittest
from src.templates.html_templates import HTMLTemplates
from src.templates.css_generator import CSSGenerator

class TestHTMLTemplates(unittest.TestCase):

    def test_get_base_css_returns_string(self):
        """Test that get_base_css returns a non-empty string."""
        css = HTMLTemplates.get_base_css()
        self.assertIsInstance(css, str)
        self.assertGreater(len(css), 0)
        self.assertIn('--primary-color', css)

    def test_party_color_themes_exist(self):
        """Test that color themes exist and have expected structure."""
        themes = CSSGenerator.get_color_themes()
        self.assertIn('default', themes)
        self.assertIn('blue_theme', themes)
        self.assertIn('green_theme', themes)
        
        # Check theme structure with new key names
        default_theme = themes['default']
        self.assertIn('primary', default_theme)
        self.assertIn('secondary', default_theme)

    def test_color_theme_structure(self):
        """Test that color themes have required keys."""
        themes = CSSGenerator.get_color_themes()
        
        for theme_name, theme in themes.items():
            with self.subTest(theme=theme_name):
                self.assertIn('primary', theme)
                self.assertIn('secondary', theme)
                self.assertIn('accent', theme)
                self.assertIn('background', theme)
                self.assertIn('text', theme)

    def test_generate_party_html_basic_structure(self):
        """Test basic party HTML generation."""
        party_data = {
            "name": "Testipuolue",
            "slogan": "Testi on paras",
            "founded_year": "2024", 
            "chairperson": "Testi Testinen",
            "website": "https://example.com",
            "platform": ["Testi idea 1", "Testi idea 2"],
            "candidates": [
                {
                    "name": "Esko Ehdokas",
                    "age": 35,
                    "profession": "Testaaja", 
                    "campaign_theme": "Laadukas testaus",
                    "platform_points": ["Testaus on tärkeää", "Laatua kaikille"]
                }
            ],
            "election_date": "2024-03-01"
        }
        
        html = HTMLTemplates.generate_party_html(party_data)
        
        # Check basic structure
        self.assertIn("Testipuolue", html)
        self.assertIn("Testi on paras", html)
        self.assertIn("Testi idea 1", html)
        self.assertIn("Esko Ehdokas", html)
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("<html", html)

    def test_generate_candidate_html_basic_structure(self):
        """Test basic candidate HTML generation."""
        candidate_data = {
            "name": "Testi Ehdokas",
            "age": 35,
            "profession": "Testaaja",
            "campaign_theme": "Laadukas testaus", 
            "platform_points": ["Testaus on tärkeää", "Laatua kaikille"]
        }
        
        html = HTMLTemplates.generate_candidate_html(candidate_data)
        
        # Check basic structure
        self.assertIn("Testi Ehdokas", html)
        self.assertIn("35", html)
        self.assertIn("Testaaja", html)
        self.assertIn("Laadukas testaus", html)
        self.assertIn("Testaus on tärkeää", html)

    def test_html_includes_metadata(self):
        """Test that HTML includes necessary metadata."""
        party_data = {
            "name": "Testipuolue",
            "slogan": "Testi",
            "founded_year": "2024",
            "chairperson": "Testi",
            "website": "https://example.com",
            "platform": ["Testi"],
            "candidates": [],
            "election_date": "2024-01-01"
        }
        
        html = HTMLTemplates.generate_party_html(party_data)
        
        # Check for metadata
        self.assertIn('<meta charset="UTF-8">', html)
        self.assertIn('<meta name="viewport"', html)
        self.assertIn('<title>', html)

    def test_css_variables_included(self):
        """Test that CSS variables are included when provided."""
        party_data = {
            "name": "Testipuolue",
            "slogan": "Testi",
            "platform": ["Testi"],
            "candidates": []
        }
        
        # Test with CSS
        test_css = "body { color: red; }"
        html = HTMLTemplates.generate_party_html(party_data, test_css)
        
        self.assertIn("body { color: red; }", html)

    def test_available_templates(self):
        """Test that templates are available."""
        templates = HTMLTemplates.get_available_templates()
        self.assertIn('party_profile', templates)
        self.assertIn('candidate_card', templates)
        self.assertIn('css_theme', templates)

if __name__ == '__main__':
    unittest.main()
