"""
Template-generointi analysoidusta HTML/CSS:stä.
"""
import json
from typing import Dict, Any
from .css_analyzer import CSSAnalyzer
from .html_analyzer import HTMLAnalyzer

class TemplateGenerator:
    """Generoi JSON-templateja analysoidusta HTML/CSS:stä."""
    
    def __init__(self):
        self.css_analyzer = CSSAnalyzer()
        self.html_analyzer = HTMLAnalyzer()
    
    def generate_from_files(self, html_file: str, css_file: str = None) -> Dict[str, Any]:
        """Generoi template HTML- ja CSS-tiedostoista."""
        result = {
            'party_profile': self._generate_party_template(html_file, css_file),
            'css_theme': self._generate_css_theme(css_file) if css_file else {}
        }
        
        return result
    
    def generate_from_content(self, html_content: str, css_content: str = None) -> Dict[str, Any]:
        """Generoi template HTML- ja CSS-sisällöstä."""
        result = {
            'party_profile': self._generate_party_template_from_content(html_content, css_content),
            'css_theme': self._generate_css_theme_from_content(css_content) if css_content else {}
        }
        
        return result
    
    def _generate_party_template(self, html_file: str, css_file: str = None) -> Dict[str, Any]:
        """Generoi puolueprofiilin templaten."""
        html_analysis = self.html_analyzer.analyze_html_file(html_file)
        
        template = {
            "template_name": "generated_party_profile",
            "version": "1.0",
            "description": "Automaattisesti generoitu puolueprofiili",
            "structure": {
                "type": "html",
                "sections": list(html_analysis.get('sections', {}).keys())
            },
            "html_template": self._build_html_template(html_analysis),
            "default_values": {
                "language": "fi",
                "charset": "UTF-8"
            },
            "required_fields": ["party_name", "slogan"]
        }
        
        return template
    
    def _generate_party_template_from_content(self, html_content: str, css_content: str = None) -> Dict[str, Any]:
        """Generoi puolueprofiilin templaten sisällöstä."""
        html_analysis = self.html_analyzer.analyze_html_content(html_content)
        
        template = {
            "template_name": "generated_party_profile",
            "version": "1.0",
            "description": "Automaattisesti generoitu puolueprofiili",
            "structure": {
                "type": "html",
                "sections": list(html_analysis.get('sections', {}).keys())
            },
            "html_template": self._build_html_template(html_analysis),
            "default_values": {
                "language": "fi",
                "charset": "UTF-8"
            },
            "required_fields": ["party_name", "slogan"]
        }
        
        return template
    
    def _build_html_template(self, html_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Rakenna HTML-template analyysin perusteella."""
        sections = html_analysis.get('sections', {})
        safe_html = html_analysis.get('safe_html', '')
        
        # Jos löytyy selkeät osat, käytä niitä
        if sections:
            template = {
                "doctype": "<!DOCTYPE html>",
                "html_open": "<html lang=\"{language}\">",
                "head": {
                    "meta_charset": "<meta charset=\"{charset}\">",
                    "meta_viewport": "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">",
                    "title": "<title>{party_name} - Vaaliprofiili</title>",
                    "styles": "<style>\n{css_content}\n</style>"
                },
                "body_open": "<body>"
            }
            
            # Lisää osat jos saatavilla
            if 'header' in sections:
                template["header"] = {
                    "section": "<header class=\"party-header\">",
                    "content": self._extract_header_content(sections['header']),
                    "section_close": "</header>"
                }
            
            if 'main' in sections:
                template["main_section"] = {
                    "section": "<main class=\"party-main\">",
                    "content": "{platform_content}\n{candidates_content}",
                    "section_close": "</main>"
                }
            
            if 'footer' in sections:
                template["footer"] = {
                    "section": "<footer class=\"party-footer\">",
                    "content": sections['footer'],
                    "section_close": "</footer>"
                }
            
            template.update({
                "body_close": "</body>",
                "html_close": "</html>"
            })
            
        else:
            # Käytä koko HTML:ää templatena
            template = {
                "full_template": safe_html
            }
        
        return template
    
    def _extract_header_content(self, header_html: str) -> str:
        """Poimi header-sisältö ja korvaa dynaamisilla osilla."""
        # Korvaa potentiaaliset staattiset osat placeholdereilla
        content = header_html
        
        # Korvaa otsikot
        content = re.sub(r'<h1[^>]*>.*?</h1>', '<h1>{party_name}</h1>', content, flags=re.DOTALL)
        content = re.sub(r'<p[^>]*class="[^"]*slogan[^"]*"[^>]*>.*?</p>', 
                        '<p class="party-slogan">{slogan}</p>', content, flags=re.DOTALL)
        
        return content
    
    def _generate_css_theme(self, css_file: str) -> Dict[str, Any]:
        """Generoi CSS-teeman CSS-tiedostosta."""
        css_analysis = self.css_analyzer.analyze_css_file(css_file)
        color_theme = self.css_analyzer.suggest_color_theme(
            open(css_file, 'r', encoding='utf-8').read()
        )
        
        template = {
            "template_name": "generated_css_theme",
            "version": "1.0",
            "description": "Automaattisesti generoitu CSS-teema",
            "structure": {
                "type": "css",
                "components": ["variables", "base_styles"]
            },
            "css_template": {
                "variables": ":root {{\n  --primary-color: {primary_color};\n  --secondary-color: {secondary_color};\n  --accent-color: {accent_color};\n  --background-color: {background_color};\n  --text-color: {text_color};\n}}",
                "base_styles": self._extract_base_styles(css_file)
            },
            "default_values": color_theme
        }
        
        return template
    
    def _generate_css_theme_from_content(self, css_content: str) -> Dict[str, Any]:
        """Generoi CSS-teeman CSS-sisällöstä."""
        css_analysis = self.css_analyzer.analyze_css_content(css_content)
        color_theme = self.css_analyzer.suggest_color_theme(css_content)
        
        template = {
            "template_name": "generated_css_theme",
            "version": "1.0",
            "description": "Automaattisesti generoitu CSS-teema",
            "structure": {
                "type": "css",
                "components": ["variables", "base_styles"]
            },
            "css_template": {
                "variables": ":root {{\n  --primary-color: {primary_color};\n  --secondary-color: {secondary_color};\n  --accent-color: {accent_color};\n  --background-color: {background_color};\n  --text-color: {text_color};\n}}",
                "base_styles": self._extract_base_styles_from_content(css_content)
            },
            "default_values": color_theme
        }
        
        return template
    
    def _extract_base_styles(self, css_file: str) -> Dict[str, str]:
        """Poimi perustyylit CSS-tiedostosta."""
        try:
            with open(css_file, 'r', encoding='utf-8') as f:
                css_content = f.read()
            return self._extract_base_styles_from_content(css_content)
        except:
            return {}
    
    def _extract_base_styles_from_content(self, css_content: str) -> Dict[str, str]:
        """Poimi perustyylit CSS-sisällöstä."""
        base_styles = {}
        
        # Etsi yleisiä tyylejä
        common_selectors = ['body', '.container', 'header', 'footer', 'main']
        
        for selector in common_selectors:
            pattern = rf'({selector}[^{{]+\{{[^}}]+\}})'
            matches = re.findall(pattern, css_content, re.DOTALL)
            if matches:
                base_styles[selector.replace('.', '').replace('#', '')] = matches[0]
        
        return base_styles
