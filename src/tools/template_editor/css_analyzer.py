"""
CSS-analyysi työkalu template-editoriin.
"""
import re
from typing import Dict, List, Any
from pathlib import Path

class CSSAnalyzer:
    """Analysoi CSS-tiedostoja ja poimii väriteemat."""
    
    def __init__(self):
        self.color_patterns = [
            r'#([0-9a-fA-F]{3,6})',  # Hex värit
            r'rgb\((\d+),\s*(\d+),\s*(\d+)\)',  # RGB
            r'rgba\((\d+),\s*(\d+),\s*(\d+),\s*[\d.]+\)',  # RGBA
            r'hsl\((\d+),\s*(\d+)%,\s*(\d+)%\)',  # HSL
        ]
    
    def analyze_css_file(self, css_file_path: str) -> Dict[str, Any]:
        """Analysoi CSS-tiedoston ja poimi väriteemat."""
        try:
            with open(css_file_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
            return self.analyze_css_content(css_content)
        except Exception as e:
            print(f"❌ Virhe ladattaessa CSS-tiedostoa: {e}")
            return {}
    
    def analyze_css_content(self, css_content: str) -> Dict[str, Any]:
        """Analysoi CSS-sisällön ja poimi väriteemat."""
        result = {
            'colors': self._extract_colors(css_content),
            'fonts': self._extract_fonts(css_content),
            'layout': self._analyze_layout(css_content),
            'selectors': self._analyze_selectors(css_content)
        }
        return result
    
    def _extract_colors(self, css_content: str) -> Dict[str, List[str]]:
        """Poimi kaikki värit CSS-sisällöstä."""
        colors = {
            'hex': [],
            'rgb': [],
            'rgba': [],
            'hsl': [],
            'named': []
        }
        
        # Hex värit
        hex_colors = re.findall(r'#([0-9a-fA-F]{3,6})', css_content)
        colors['hex'] = list(set(['#' + color for color in hex_colors]))
        
        # RGB värit
        rgb_colors = re.findall(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', css_content)
        colors['rgb'] = list(set([f'rgb({r},{g},{b})' for r, g, b in rgb_colors]))
        
        # RGBA värit
        rgba_colors = re.findall(r'rgba\((\d+),\s*(\d+),\s*(\d+),\s*[\d.]+\)', css_content)
        colors['rgba'] = list(set([match[0] for match in rgba_colors]))
        
        # HSL värit
        hsl_colors = re.findall(r'hsl\((\d+),\s*(\d+)%,\s*(\d+)%\)', css_content)
        colors['hsl'] = list(set([f'hsl({h},{s}%,{l}%)' for h, s, l in hsl_colors]))
        
        # Nimettyjä värejä
        named_colors = re.findall(r'\b(red|green|blue|black|white|gray|yellow|purple|orange|pink|brown)\b', css_content, re.IGNORECASE)
        colors['named'] = list(set([color.lower() for color in named_colors]))
        
        return colors
    
    def _extract_fonts(self, css_content: str) -> Dict[str, List[str]]:
        """Poimi fontit CSS-sisällöstä."""
        fonts = {
            'families': [],
            'sizes': [],
            'weights': []
        }
        
        # Font families
        font_families = re.findall(r'font-family:\s*([^;]+)', css_content)
        for family_list in font_families:
            families = [f.strip().strip('"\'').strip('"\'').strip('"\'').strip('"\'').strip('"\'').strip('"\'') 
                       for f in family_list.split(',')]
            fonts['families'].extend(families)
        
        fonts['families'] = list(set(fonts['families']))
        
        # Font sizes
        font_sizes = re.findall(r'font-size:\s*([^;]+)', css_content)
        fonts['sizes'] = list(set([size.strip() for size in font_sizes]))
        
        # Font weights
        font_weights = re.findall(r'font-weight:\s*([^;]+)', css_content)
        fonts['weights'] = list(set([weight.strip() for weight in font_weights]))
        
        return fonts
    
    def _analyze_layout(self, css_content: str) -> Dict[str, Any]:
        """Analysoi layout-ominaisuudet."""
        layout = {
            'grid_used': 'grid' in css_content or r'display:\s*grid' in css_content,
            'flexbox_used': 'flex' in css_content or r'display:\s*flex' in css_content,
            'media_queries': self._extract_media_queries(css_content)
        }
        return layout
    
    def _extract_media_queries(self, css_content: str) -> List[str]:
        """Poimi media queryt CSS-sisällöstä."""
        media_queries = re.findall(r'@media[^{]+\{', css_content)
        return list(set(media_queries))
    
    def _analyze_selectors(self, css_content: str) -> Dict[str, List[str]]:
        """Analysoi CSS-selektorit."""
        selectors = {
            'classes': [],
            'ids': [],
            'elements': []
        }
        
        # Poista kommentit ensin
        css_clean = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
        
        # Etsi selektorit
        rules = re.findall(r'([^{]+)\{', css_clean)
        
        for rule in rules:
            # Luokat
            classes = re.findall(r'\.([a-zA-Z][\w-]*)', rule)
            selectors['classes'].extend(classes)
            
            # ID:t
            ids = re.findall(r'#([a-zA-Z][\w-]*)', rule)
            selectors['ids'].extend(ids)
            
            # HTML-elementit
            elements = re.findall(r'^\s*([a-zA-Z][a-zA-Z0-9]*)(?![\.#\[])', rule)
            selectors['elements'].extend(elements)
        
        # Poista duplikaatit
        selectors['classes'] = list(set(selectors['classes']))
        selectors['ids'] = list(set(selectors['ids']))
        selectors['elements'] = list(set(selectors['elements']))
        
        return selectors
    
    def suggest_color_theme(self, css_content: str) -> Dict[str, str]:
        """Ehdota väriteemaa analysoidun CSS:n perusteella."""
        colors = self._extract_colors(css_content)
        
        theme = {
            'primary_color': self._suggest_primary_color(colors),
            'secondary_color': self._suggest_secondary_color(colors),
            'accent_color': self._suggest_accent_color(colors),
            'background_color': self._suggest_background_color(colors),
            'text_color': self._suggest_text_color(colors)
        }
        
        return theme
    
    def _suggest_primary_color(self, colors: Dict) -> str:
        """Ehdota pääväriä."""
        if colors['hex']:
            return colors['hex'][0]  # Ota ensimmäinen hex-väri
        elif colors['rgb']:
            return colors['rgb'][0]
        return '#2c3e50'  # Oletus
    
    def _suggest_secondary_color(self, colors: Dict) -> str:
        """Ehdota toissijaista väriä."""
        if len(colors['hex']) > 1:
            return colors['hex'][1]
        elif len(colors['rgb']) > 1:
            return colors['rgb'][1]
        return '#3498db'  # Oletus
    
    def _suggest_accent_color(self, colors: Dict) -> str:
        """Ehdota korostusväriä."""
        # Etsi kirkas väri
        for color in colors['hex']:
            if any(bright in color.lower() for bright in ['ff', 'e74', 'f39', 'e67']):
                return color
        return '#e74c3c'  # Oletus
    
    def _suggest_background_color(self, colors: Dict) -> str:
        """Ehdota taustaväriä."""
        # Etsi vaalea väri
        for color in colors['hex']:
            if any(light in color.lower() for light in ['fff', 'f8f', 'f5f', 'ecf', 'faf']):
                return color
        return '#ecf0f1'  # Oletus
    
    def _suggest_text_color(self, colors: Dict) -> str:
        """Ehdota tekstin väriä."""
        # Etsi tumma väri
        for color in colors['hex']:
            if any(dark in color.lower() for dark in ['000', '333', '222', '2c3', '344']):
                return color
        return '#2c3e50'  # Oletus
