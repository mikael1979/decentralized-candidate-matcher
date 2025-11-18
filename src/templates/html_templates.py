"""
HTML template system using JSON template files.
"""
from .json_template_manager import get_json_template_manager

class HTMLTemplates:
    """HTML template system using JSON template files."""
    
    _template_manager = get_json_template_manager()
    
    @classmethod
    def get_base_css(cls):
        """Return base CSS styles from JSON template."""
        return cls._template_manager.get_template("css_theme").get('css_template', {}).get('variables', '')
    
    @classmethod
    def generate_party_html(cls, party_data, css_content=""):
        """Generate party HTML from JSON templates."""
        # Format platform content
        platform_content = "<ul>"
        for point in party_data.get('platform', []):
            platform_content += cls.generate_platform_point({'point': point})
        platform_content += "</ul>"
        
        # Format candidates content
        candidates_content = ""
        for candidate in party_data.get('candidates', []):
            candidates_content += cls.generate_candidate_html(candidate)
        
        # Prepare data for party template
        template_data = {
            'party_name': party_data.get('name', ''),
            'css_content': css_content,
            'slogan': party_data.get('slogan', ''),
            'founded_year': party_data.get('founded_year', ''),
            'chairperson': party_data.get('chairperson', ''),
            'website': party_data.get('website', ''),
            'platform_content': platform_content,
            'candidates_content': candidates_content,
            'election_date': party_data.get('election_date', ''),
            'language': 'fi',
            'charset': 'UTF-8'
        }
        
        # Validate and render
        if not cls._template_manager.validate_data('party_profile', template_data):
            raise ValueError("Party data is missing required fields")
        
        return cls._template_manager.render_html_template('party_profile', template_data)
    
    @classmethod
    def generate_candidate_html(cls, candidate_data):
        """Generate candidate HTML from JSON templates."""
        # Format platform points
        platform_points = ""
        for point in candidate_data.get('platform_points', []):
            platform_points += cls.generate_platform_point({'point': point})
        
        template_data = {
            'name': candidate_data.get('name', ''),
            'age': candidate_data.get('age', ''),
            'profession': candidate_data.get('profession', ''),
            'campaign_theme': candidate_data.get('campaign_theme', 'Ei määritelty'),
            'platform_points': platform_points
        }
        
        if not cls._template_manager.validate_data('candidate_card', template_data):
            raise ValueError("Candidate data is missing required fields")
        
        return cls._template_manager.render_html_template('candidate_card', template_data)
    
    @classmethod
    def generate_platform_point(cls, point_data):
        """Generate platform point HTML from JSON templates."""
        if not cls._template_manager.validate_data('platform_point', point_data):
            return ""
        
        return cls._template_manager.render_html_template('platform_point', point_data)
    
    @classmethod
    def generate_css(cls, color_theme: dict) -> str:
        """Generate CSS with color theme variables from JSON template."""
        return cls._template_manager.render_css_template('css_theme', color_theme)
    
    @classmethod
    def get_available_templates(cls):
        """Get list of available templates."""
        return cls._template_manager.list_templates()
    
    @classmethod
    def get_template_info(cls, template_name: str):
        """Get information about a specific template."""
        return cls._template_manager.get_template_info(template_name)
