"""
Template manager for loading templates from files.
"""
from pathlib import Path
from typing import Dict, Optional
import string

class TemplateManager:
    """Manages HTML templates loaded from files."""
    
    def __init__(self, template_dir: str = "src/templates/template_files"):
        self.template_dir = Path(template_dir)
        self._templates: Dict[str, str] = {}
        self._load_templates()
    
    def _load_templates(self):
        """Load all templates from template directory."""
        template_files = [
            "party_profile.html",
            "candidate_card.html", 
            "platform_point.html",
            "base_css.css"
        ]
        
        for template_file in template_files:
            template_path = self.template_dir / template_file
            if template_path.exists():
                template_name = template_path.stem  # Remove .html/.css extension
                try:
                    content = template_path.read_text(encoding='utf-8')
                    # Siivoa template - poista mahdolliset ylimääräiset rivinvaihdot
                    content = content.strip()
                    self._templates[template_name] = content
                    print(f"✅ Loaded template: {template_name} ({len(content)} chars)")
                except Exception as e:
                    print(f"❌ Error loading template {template_name}: {e}")
            else:
                print(f"⚠️  Template file not found: {template_path}")
    
    def get_template(self, template_name: str) -> str:
        """Get template by name."""
        return self._templates.get(template_name, "")
    
    def render(self, template_name: str, **kwargs) -> str:
        """Render template with given variables using safe substitution."""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template not found: {template_name}")
        
        try:
            # Käytä turvallista template-substituutiota
            template_obj = string.Template(template)
            return template_obj.safe_substitute(**kwargs)
        except Exception as e:
            raise ValueError(f"Template rendering failed for {template_name}: {e}")
    
    def template_exists(self, template_name: str) -> bool:
        """Check if template exists."""
        return template_name in self._templates

# Global template manager instance
_template_manager = TemplateManager()

def get_template_manager() -> TemplateManager:
    """Get the global template manager instance."""
    return _template_manager
