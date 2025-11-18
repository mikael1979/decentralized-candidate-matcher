"""
Päätemplate-editori.
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
from .css_analyzer import CSSAnalyzer
from .html_analyzer import HTMLAnalyzer
from .template_generator import TemplateGenerator

class TemplateEditor:
    """Visuaalinen template-editori."""
    
    def __init__(self):
        self.css_analyzer = CSSAnalyzer()
        self.html_analyzer = HTMLAnalyzer()
        self.template_generator = TemplateGenerator()
    
    def create_template_from_website(self, html_file: str, css_file: str = None, 
                                   output_dir: str = "generated_templates") -> Dict[str, Any]:
        """
        Luo JSON-template olemassa olevasta verkkosivusta.
        
        Args:
            html_file: HTML-tiedoston polku
            css_file: CSS-tiedoston polku (valinnainen)
            output_dir: Output-hakemisto
            
        Returns:
            Generoitujen templatejen tiedot
        """
        print("🎨 LUODAAN TEMPLATE VERKKOSIVUSTA...")
        print(f"📄 HTML: {html_file}")
        if css_file:
            print(f"🎨 CSS: {css_file}")
        
        # Analysoi tiedostot
        html_analysis = self.html_analyzer.analyze_html_file(html_file)
        css_analysis = self.css_analyzer.analyze_css_file(css_file) if css_file else {}
        
        print("✅ Analyysi valmis")
        
        # Generoi templatet
        templates = self.template_generator.generate_from_files(html_file, css_file)
        
        # Tallenna templatet
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        saved_files = []
        for template_name, template_data in templates.items():
            if template_data:  # Tallennetaan vain ei-tyhjät templatet
                filename = output_path / f"{template_name}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(template_data, f, indent=2, ensure_ascii=False)
                saved_files.append(str(filename))
                print(f"💾 Tallennettu: {filename}")
        
        # Näytä yhteenveto
        self._show_summary(html_analysis, css_analysis, templates)
        
        return {
            'templates': templates,
            'saved_files': saved_files,
            'analysis': {
                'html': html_analysis,
                'css': css_analysis
            }
        }
    
    def create_template_from_content(self, html_content: str, css_content: str = None,
                                   output_dir: str = "generated_templates") -> Dict[str, Any]:
        """
        Luo JSON-template HTML/CSS-sisällöstä.
        
        Args:
            html_content: HTML-sisältö
            css_content: CSS-sisältö (valinnainen)
            output_dir: Output-hakemisto
            
        Returns:
            Generoitujen templatejen tiedot
        """
        print("🎨 LUODAAN TEMPLATE SISÄLLÖSTÄ...")
        
        # Analysoi sisällöt
        html_analysis = self.html_analyzer.analyze_html_content(html_content)
        css_analysis = self.css_analyzer.analyze_css_content(css_content) if css_content else {}
        
        print("✅ Analyysi valmis")
        
        # Generoi templatet
        templates = self.template_generator.generate_from_content(html_content, css_content)
        
        # Tallenna templatet
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        saved_files = []
        for template_name, template_data in templates.items():
            if template_data:  # Tallennetaan vain ei-tyhjät templatet
                filename = output_path / f"{template_name}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(template_data, f, indent=2, ensure_ascii=False)
                saved_files.append(str(filename))
                print(f"💾 Tallennettu: {filename}")
        
        # Näytä yhteenveto
        self._show_summary(html_analysis, css_analysis, templates)
        
        return {
            'templates': templates,
            'saved_files': saved_files,
            'analysis': {
                'html': html_analysis,
                'css': css_analysis
            }
        }
    
    def _show_summary(self, html_analysis: Dict, css_analysis: Dict, templates: Dict):
        """Näytä generoinnin yhteenveto."""
        print("\n📊 GENEROINNIN YHTEENVETO:")
        print("=" * 50)
        
        # HTML-analyysi
        html_struct = html_analysis.get('structure', {})
        print("📄 HTML-ANALYYSI:")
        print(f"  - Otsikoita: {len(html_struct.get('headings', []))}")
        print(f"  - Kontteja: {len(html_struct.get('containers', []))}")
        print(f"  - Linkkejä: {len(html_struct.get('links', []))}")
        print(f"  - Osia: {len(html_analysis.get('sections', {}))}")
        
        # CSS-analyysi
        if css_analysis:
            colors = css_analysis.get('colors', {})
            print("🎨 CSS-ANALYYSI:")
            print(f"  - Värejä: {sum(len(v) for v in colors.values())}")
            print(f"  - Fontteja: {len(css_analysis.get('fonts', {}).get('families', []))}")
            print(f"  - Selektoriluokkia: {len(css_analysis.get('selectors', {}).get('classes', []))}")
        
        # Template-generointi
        print("📝 GENEROIDUT TEMPLATET:")
        for template_name, template_data in templates.items():
            if template_data:
                structure = template_data.get('structure', {})
                print(f"  - {template_name}: {structure.get('type', 'unknown')}")
                if 'html_template' in template_data:
                    sections = list(template_data['html_template'].keys())
                    print(f"    Osat: {', '.join(sections[:3])}{'...' if len(sections) > 3 else ''}")
    
    def preview_template(self, template_data: Dict[str, Any], preview_data: Dict[str, Any] = None) -> str:
        """Esikatsele generoitua templatea."""
        from src.templates.json_template_manager import JSONTemplateManager
        
        tm = JSONTemplateManager()
        
        # Oletusesittelydata
        default_preview_data = {
            'party_name': 'Esimerkki Puolue',
            'slogan': 'Esimerkki iskulause',
            'platform_content': '<ul><li>Esimerkki kannatuskohta 1</li><li>Esimerkki kannatuskohta 2</li></ul>',
            'candidates_content': '<div>Esimerkki ehdokkaat</div>',
            'css_content': '/* CSS sisältö tulee tähän */',
            'language': 'fi',
            'charset': 'UTF-8'
        }
        
        if preview_data:
            default_preview_data.update(preview_data)
        
        try:
            if 'html_template' in template_data:
                return tm.render_html_template('generated_party_profile', default_preview_data)
            else:
                return "Templatea ei voi esikatsella"
        except Exception as e:
            return f"Esikatseluvirhe: {e}"

# Luodaan komentorivityökalu
def main():
    """Pääfunktio komentorivityökalulle."""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description='Template Editor - Luo JSON-templateja verkkosivuista')
    parser.add_argument('--html', required=True, help='HTML-tiedoston polku')
    parser.add_argument('--css', help='CSS-tiedoston polku (valinnainen)')
    parser.add_argument('--output', default='generated_templates', help='Output-hakemisto')
    parser.add_argument('--preview', action='store_true', help='Näytä esikatselu')
    
    args = parser.parse_args()
    
    editor = TemplateEditor()
    
    try:
        # Tarkista että HTML-tiedosto on olemassa
        if not Path(args.html).exists():
            print(f"❌ HTML-tiedostoa ei löydy: {args.html}")
            sys.exit(1)
        
        if args.css and not Path(args.css).exists():
            print(f"❌ CSS-tiedostoa ei löydy: {args.css}")
            sys.exit(1)
        
        # Luo template
        result = editor.create_template_from_website(
            html_file=args.html,
            css_file=args.css,
            output_dir=args.output
        )
        
        # Esikatselu jos pyydetty
        if args.preview and 'party_profile' in result['templates']:
            print("\n👁️  ESIKATSELU:")
            print("=" * 50)
            preview = editor.preview_template(result['templates']['party_profile'])
            print(preview[:500] + "..." if len(preview) > 500 else preview)
        
        print(f"\n🎉 Template-generointi valmis! Templatet tallennettu hakemistoon: {args.output}")
        
    except Exception as e:
        print(f"❌ Virhe: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
