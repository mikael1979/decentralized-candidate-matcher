#!/usr/bin/env python3
"""
Testit HTML-pohjille ja CSS-tyyleille
"""
import pytest
import json
from datetime import datetime
from src.templates.html_templates import HTMLTemplates, PARTY_COLOR_THEMES

class TestHTMLTemplates:
    """Testit HTMLTemplates-luokalle"""
    
    def test_get_base_css_returns_string(self):
        """Testaa että get_base_css palauttaa merkkijonon"""
        css = HTMLTemplates.get_base_css()
        assert isinstance(css, str)
        assert len(css) > 100  # Varmista että CSS on riittävän pitkä
        assert "body" in css  # Varmista että sisältää peruselementtejä
        assert "font-family" in css
    
    def test_party_color_themes_exist(self):
        """Testaa että väriteemat on määritelty"""
        assert "default" in PARTY_COLOR_THEMES
        assert "blue_theme" in PARTY_COLOR_THEMES
        assert "green_theme" in PARTY_COLOR_THEMES
        assert "red_theme" in PARTY_COLOR_THEMES
        assert "purple_theme" in PARTY_COLOR_THEMES
    
    def test_color_theme_structure(self):
        """Testaa että väriteemat sisältävät tarvittavat kentät"""
        for theme_name, theme in PARTY_COLOR_THEMES.items():
            assert "primary" in theme
            assert "secondary" in theme
            assert "accent" in theme
            assert "background" in theme
            # Varmista että värit ovat hex-muodossa
            assert theme["primary"].startswith("#")
            assert theme["secondary"].startswith("#")
    
    def test_generate_party_html_basic_structure(self):
        """Testaa puolueen HTML-generointia"""
        party_data = {
            "party_id": "party_test_001",
            "name": {"fi": "Testipuolue", "en": "Test Party", "sv": "Testparti"},
            "description": {"fi": "Testikuvaus", "en": "Test description", "sv": "Testbeskrivning"},
            "metadata": {
                "founding_year": "2024",
                "contact_email": "test@example.com",
                "website": "https://example.com"
            }
        }
        
        colors = PARTY_COLOR_THEMES["default"]
        page_id = "party_test_001_20240101_120000"
        candidate_cards = "<div>Testiehdokkaat</div>"
        ipfs_cids = {"parties": "QmTest123", "candidates": "QmTest456"}
        election_id = "Jumaltenvaalit2026"
        
        html = HTMLTemplates.generate_party_html(
            party_data, colors, page_id, candidate_cards, ipfs_cids, election_id
        )
        
        # Perustarkistukset
        assert isinstance(html, str)
        assert "<!DOCTYPE html>" in html
        assert "<html lang=\"fi\">" in html
        assert "Testipuolue" in html
        assert "Jumaltenvaalit 2026" in html
        assert party_data["party_id"] in html
        assert page_id in html
    
    def test_generate_candidate_html_basic_structure(self):
        """Testaa ehdokkaan HTML-generointia"""
        candidate_data = {
            "candidate_id": "cand_test_001",
            "basic_info": {
                "name": {"fi": "Testi Ehdokas", "en": "Test Candidate", "sv": "Testkandidat"},
                "party": "Testipuolue",
                "domain": "Testialue"
            },
            "answers": [
                {
                    "question_id": "q_1",
                    "answer_value": 3,
                    "confidence": 4,
                    "explanation": {"fi": "Testiperustelu"}
                }
            ]
        }
        
        party_data = {
            "party_id": "party_test_001",
            "name": {"fi": "Testipuolue"}
        }
        
        colors = PARTY_COLOR_THEMES["blue_theme"]
        page_id = "candidate_test_001_20240101_120000"
        answer_cards = "<div>Testivastaukset</div>"
        ipfs_cids = {"candidates": "QmTest789"}
        election_id = "Jumaltenvaalit2026"
        
        html = HTMLTemplates.generate_candidate_html(
            candidate_data, party_data, colors, page_id, answer_cards, ipfs_cids, election_id
        )
        
        # Perustarkistukset
        assert isinstance(html, str)
        assert "<!DOCTYPE html>" in html
        assert "Testi Ehdokas" in html
        assert "Testipuolue" in html
        assert candidate_data["candidate_id"] in html
        assert page_id in html
    
    def test_html_includes_metadata(self):
        """Testaa että HTML sisältää tarvittavat metadata-tagit"""
        party_data = {
            "party_id": "party_test_001",
            "name": {"fi": "Testipuolue"},
            "description": {"fi": "Testi"},
            "metadata": {}
        }
        
        html = HTMLTemplates.generate_party_html(
            party_data, 
            PARTY_COLOR_THEMES["default"],
            "test_page",
            "<div></div>",
            {},
            "Testivaali2026"
        )
        
        # Tarkista metadata-tagit
        assert "meta name=\"profile-id\"" in html
        assert "meta name=\"profile-type\"" in html
        assert "meta name=\"party-id\"" in html
        assert "meta name=\"election-id\"" in html
    
    def test_css_variables_included(self):
        """Testaa että CSS-muuttujat sisältyvät HTML:ään"""
        party_data = {
            "party_id": "party_test_001",
            "name": {"fi": "Testipuolue"},
            "description": {"fi": "Testi"},
            "metadata": {}
        }
        
        colors = PARTY_COLOR_THEMES["red_theme"]
        html = HTMLTemplates.generate_party_html(
            party_data, colors, "test", "<div></div>", {}, "test"
        )
        
        # Tarkista että CSS-muuttujat sisältyvät
        assert f"--primary-color: {colors['primary']}" in html
        assert f"--secondary-color: {colors['secondary']}" in html
        assert f"--accent-color: {colors['accent']}" in html
