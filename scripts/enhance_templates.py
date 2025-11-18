# scripts/enhance_templates.py
#!/usr/bin/env python3
"""
Template-parannus työkalu - parantaa kaikki base templatet
"""
import json
from pathlib import Path
from typing import Dict, List

class TemplateEnhancer:
    def __init__(self, base_dir: Path = Path("base_templates")):
        self.base_dir = base_dir
        self.enhancement_plan = self._create_enhancement_plan()
    
    def _create_enhancement_plan(self) -> Dict:
        """Luo parannussuunnitelma template-tiedostoille"""
        return {
            "questions/questions.base.json": {
                "add_metadata": True,
                "ensure_placeholders": True,
                "add_examples": True,
                "validate_structure": True
            },
            "elections/install_config.base.json": {
                "add_metadata": True,
                "ensure_placeholders": True,
                "add_election_specific_guidance": True
            },
            # ... kaikille templateille omat säännöt
        }
    
    def enhance_all_templates(self):
        """Paranna kaikki template-tiedostot"""
        template_files = list(self.base_dir.rglob("*.base.json"))
        
        print(f"🔍 Löydetty {len(template_files)} template-tiedostoa")
        
        for template_file in template_files:
            relative_path = template_file.relative_to(self.base_dir)
            enhancement_rules = self.enhancement_plan.get(str(relative_path), {})
            
            if enhancement_rules:
                self.enhance_single_template(template_file, enhancement_rules)
    
    def enhance_single_template(self, template_path: Path, rules: Dict):
        """Paranna yksittäinen template"""
        print(f"🔄 Parannetaan: {template_path}")
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            # Sovella parannuksia
            if rules.get("add_metadata"):
                template_data = self._add_template_metadata(template_data, template_path)
            
            if rules.get("ensure_placeholders"):
                template_data = self._ensure_placeholders(template_data)
            
            if rules.get("add_examples"):
                template_data = self._add_minimal_examples(template_data, template_path)
            
            # Tallenna parannettu template
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Parannettu: {template_path}")
            
        except Exception as e:
            print(f"❌ Virhe tiedostossa {template_path}: {e}")
    
    def _add_template_metadata(self, template_data: Dict, template_path: Path) -> Dict:
        """Lisää template-metadata"""
        if "metadata" not in template_data:
            template_data["metadata"] = {}
        
        metadata = template_data["metadata"]
        metadata.update({
            "template_version": "2.0.0",
            "description": {
                "fi": f"Perusrakenne tiedostolle {template_path.name}",
                "en": f"Basic structure for {template_path.name}",
                "sv": f"Grundläggande struktur för {template_path.name}"
            },
            "generated_from": str(template_path),
            "placeholder_guidance": {
                "fi": "Korvaa {{...}} arvot todellisilla tiedoilla",
                "en": "Replace {{...}} with actual values", 
                "sv": "Ersätt {{...}} med faktiska värden"
            }
        })
        
        return template_data

if __name__ == "__main__":
    enhancer = TemplateEnhancer()
    enhancer.enhance_all_templates()
