"""
CSS generator for party profiles using template files.
"""
from typing import Dict
from src.core.configuration_manager import ConfigurationManager
from .html_templates import HTMLTemplates

class CSSGenerator:
    """Generates CSS styles for party profiles using templates."""
    
    @staticmethod
    def get_color_themes(election_name: str = "Jumaltenvaalit2026") -> Dict[str, Dict[str, str]]:
        """Get available color themes."""
        config_manager = ConfigurationManager(election_name)
        return config_manager.get_color_themes()
    
    def generate_party_css(self, color_theme: Dict[str, str]) -> str:
        """Generate CSS for party profile using color theme and templates."""
        return HTMLTemplates.generate_css(color_theme)
