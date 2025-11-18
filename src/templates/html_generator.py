from typing import Dict, Optional
from src.templates.html_templates import HTMLTemplates
from src.templates.css_generator import CSSGenerator

class HTMLProfileGenerator:
    """Generates and publishes HTML profiles for parties and candidates."""
    
    def __init__(self, election_name="Jumaltenvaalit2026"):
        self.election_name = election_name
        self.css_generator = CSSGenerator()  # Ei parametreja
    
    def generate_and_publish_party_profile(self, party_data: Dict, custom_colors: Dict = None) -> Dict:
        """Generate HTML profile for a party and publish to IPFS."""
        
        # Get CSS content
        css_content = self.css_generator.generate_party_css(
            custom_colors or CSSGenerator.get_color_themes(self.election_name).get('default', {})
        )
        
        # Generate HTML content
        html_content = HTMLTemplates.generate_party_html(party_data, css_content)
        
        # For now, return mock IPFS hash
        # In real implementation, this would publish to IPFS
        return {
            'html_content': html_content,
            'css_content': css_content,
            'ipfs_hash': f"mock_ipfs_hash_{party_data.get('name', 'unknown').lower()}"
        }
    
    def generate_candidate_profile(self, candidate_data: Dict, party_theme: str = 'default') -> Dict:
        """Generate HTML profile for a candidate."""
        themes = CSSGenerator.get_color_themes(self.election_name)
        css_content = self.css_generator.generate_party_css(themes.get(party_theme, themes['default']))
        
        html_content = HTMLTemplates.generate_candidate_html(candidate_data)
        
        # Wrap candidate HTML in full document
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>{css_content}</style>
        </head>
        <body>
            <div class="container">
                {html_content}
            </div>
        </body>
        </html>
        """
        
        return {
            'html_content': full_html,
            'css_content': css_content,
            'ipfs_hash': f"mock_candidate_hash_{candidate_data.get('name', 'unknown').lower()}"
        }
