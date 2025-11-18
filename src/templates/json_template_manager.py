"""
JSON-pohjainen template-järjestelmä.
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from string import Template

class JSONTemplateManager:
    """Hallitsee JSON-muotoisia templateja."""
    
    def __init__(self, template_dir: str = "src/templates/json_templates"):
        self.template_dir = Path(template_dir)
        self._templates: Dict[str, Dict] = {}
        self._load_templates()
    
    def _load_templates(self):
        """Lataa JSON-templatet hakemistosta."""
        if not self.template_dir.exists():
            print(f"⚠️  Template-hakemistoa ei löydy: {self.template_dir}")
            return
            
        for json_file in self.template_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                    template_name = template_data.get('template_name', json_file.stem)
                    self._templates[template_name] = template_data
                    print(f"✅ Ladattu JSON-template: {template_name}")
            except Exception as e:
                print(f"❌ Virhe ladattaessa templatea {json_file}: {e}")
    
    def get_template(self, template_name: str) -> Optional[Dict]:
        """Hae template nimen perusteella."""
        return self._templates.get(template_name)
    
    def render_html_template(self, template_name: str, data: Dict[str, Any]) -> str:
        """Renderöi HTML-templaten."""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Templatea ei löydy: {template_name}")
        
        # Yhdistä oletusarvot käyttäjän datan kanssa
        merged_data = template.get('default_values', {}).copy()
        merged_data.update(data)
        
        html_parts = []
        html_template = template.get('html_template', {})
        
        # Määritä osien renderöintijärjestys
        parts_order = self._get_template_parts_order(template_name)
        
        for part in parts_order:
            if part in html_template:
                rendered_part = self._render_template_part(html_template[part], merged_data)
                if rendered_part:
                    html_parts.append(rendered_part)
        
        result = '\n'.join(filter(None, html_parts))
        
        # Varmista että kaikki placeholderit on korvattu
        result = self._ensure_placeholders_replaced(result, merged_data)
        
        return result
    
    def _get_template_parts_order(self, template_name: str) -> List[str]:
        """Palauta template-osien renderöintijärjestys."""
        order_map = {
            'party_profile': [
                'doctype', 'html_open', 'head', 'body_open', 'container_open',
                'header', 'info_section', 'platform_section', 'candidates_section', 
                'footer', 'container_close', 'body_close', 'html_close'
            ],
            'candidate_card': [
                'card_open', 'header', 'details', 'platform_section', 'card_close'
            ],
            'platform_point': ['point']
        }
        return order_map.get(template_name, [])
    
    def _render_template_part(self, template_part, data: Dict[str, Any]) -> str:
        """Renderöi yksittäinen template-osa."""
        if isinstance(template_part, str):
            # Yksinkertainen merkkijono - renderöi suoraan
            try:
                return Template(template_part).safe_substitute(data)
            except Exception as e:
                print(f"⚠️  Virhe renderöitäessä template-osaa: {e}")
                return template_part
        elif isinstance(template_part, dict):
            # Monimutkainen osa - renderöi rekursiivisesti
            rendered_parts = []
            
            for key, value in template_part.items():
                # Ohita struktuuriavaimet ensimmäisellä tasolla
                if key not in ['section', 'section_close']:
                    rendered = self._render_template_part(value, data)
                    if rendered:
                        rendered_parts.append(rendered)
            
            # Käsittele section avaimet
            section_open = template_part.get('section', '')
            section_close = template_part.get('section_close', '')
            
            if section_open:
                rendered_open = Template(section_open).safe_substitute(data)
                rendered_parts.insert(0, rendered_open)
            if section_close:
                rendered_close = Template(section_close).safe_substitute(data)
                rendered_parts.append(rendered_close)
                
            return '\n'.join(filter(None, rendered_parts))
        else:
            return str(template_part)
    
    def render_css_template(self, template_name: str, color_theme: Dict[str, str]) -> str:
        """Renderöi CSS-templaten."""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"CSS-templatea ei löydy: {template_name}")
        
        # Yhdistä oletusarvot väriteeman kanssa
        merged_theme = template.get('default_values', {}).copy()
        merged_theme.update(color_theme)
        
        css_parts = []
        css_template = template.get('css_template', {})
        
        # Renderöi CSS-osat
        for part_name, part_template in css_template.items():
            if isinstance(part_template, str):
                rendered_css = Template(part_template).safe_substitute(merged_theme)
                css_parts.append(rendered_css)
            elif isinstance(part_template, dict):
                for sub_part_name, sub_part_template in part_template.items():
                    rendered_css = Template(sub_part_template).safe_substitute(merged_theme)
                    css_parts.append(rendered_css)
        
        result = '\n\n'.join(filter(None, css_parts))
        
        # Varmista että kaikki placeholderit on korvattu
        result = self._ensure_placeholders_replaced(result, merged_theme)
        
        return result
    
    def _ensure_placeholders_replaced(self, text: str, data: Dict[str, Any]) -> str:
        """Varmista että kaikki placeholderit on korvattu datalla."""
        # Käytä Template.safe_substitute uudelleen varmistaaksemme korvaukset
        try:
            template_obj = Template(text)
            result = template_obj.safe_substitute(data)
            
            # Tarkista onko placeholder-ongelmia
            import re
            remaining_placeholders = re.findall(r'\{(\w+)\}', result)
            if remaining_placeholders:
                print(f"⚠️  Huom: Seuraavia placeholdereita ei korvattu: {set(remaining_placeholders)}")
                
            return result
        except Exception as e:
            print(f"⚠️  Virhe varmistettaessa placeholder-korvauksia: {e}")
            return text
    
    def validate_data(self, template_name: str, data: Dict[str, Any]) -> bool:
        """Validoi että datassa on kaikki vaaditut kentät."""
        template = self.get_template(template_name)
        if not template:
            return False
            
        required_fields = template.get('required_fields', [])
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            print(f"⚠️  Puuttuvat kentät templatelle {template_name}: {missing_fields}")
            return False
            
        return True
    
    def list_templates(self) -> List[str]:
        """Listaa kaikki ladatut templatet."""
        return list(self._templates.keys())
    
    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """Hae templaten metadata."""
        template = self.get_template(template_name)
        if not template:
            return {}
        
        return {
            'name': template.get('template_name'),
            'version': template.get('version'),
            'description': template.get('description'),
            'structure': template.get('structure', {}),
            'required_fields': template.get('required_fields', [])
        }

# Globaali instanssi
_json_template_manager = JSONTemplateManager()

def get_json_template_manager() -> JSONTemplateManager:
    """Hae globaali JSON template manager."""
    return _json_template_manager
