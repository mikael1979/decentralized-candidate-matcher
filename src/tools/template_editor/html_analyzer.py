"""
HTML-analyysi ja turvallisuussuodatus.
"""
import re
from typing import Dict, List, Tuple, Any
from html.parser import HTMLParser

class HTMLSanitizer(HTMLParser):
    """Suodattaa turvallisen HTML:n ja poistaa vaarallisen koodin."""
    
    def __init__(self):
        super().__init__()
        self.safe_tags = {
            'div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'ul', 'ol', 'li', 'a', 'strong', 'em', 'b', 'i', 'u',
            'br', 'hr', 'img', 'table', 'tr', 'td', 'th', 'thead', 'tbody',
            'header', 'footer', 'section', 'article', 'aside', 'nav',
            'main', 'figure', 'figcaption', 'blockquote', 'cite'
        }
        self.safe_attributes = {
            'class', 'id', 'style', 'href', 'src', 'alt', 'title',
            'width', 'height', 'colspan', 'rowspan', 'target'
        }
        self.allowed_protocols = {'http', 'https', 'mailto'}
        self.output = []
        self.current_tag = None
        
    def handle_starttag(self, tag, attrs):
        """Käsittele aloitustagit."""
        if tag.lower() in self.safe_tags:
            self.current_tag = tag.lower()
            attr_string = self._safe_attributes(attrs)
            self.output.append(f'<{tag}{attr_string}>')
        elif tag.lower() in ['script', 'style', 'iframe', 'object', 'embed']:
            # Ohita vaaralliset tagit
            pass
        else:
            # Muut tagit sallitaan mutta ilman attribuutteja
            self.output.append(f'<{tag}>')
    
    def handle_endtag(self, tag):
        """Käsittele lopetustagit."""
        if tag.lower() in self.safe_tags:
            self.output.append(f'</{tag}>')
            self.current_tag = None
        elif tag.lower() not in ['script', 'style', 'iframe', 'object', 'embed']:
            self.output.append(f'</{tag}>')
    
    def handle_data(self, data):
        """Käsittele data."""
        if self.current_tag not in ['script', 'style']:
            # Siivoa potentiaaliset XSS-yritykset
            cleaned_data = self._clean_text(data)
            self.output.append(cleaned_data)
    
    def handle_comment(self, data):
        """Ohita kommentit."""
        pass
    
    def _safe_attributes(self, attrs: List[Tuple[str, str]]) -> str:
        """Suodata turvalliset attribuutit."""
        safe_attrs = []
        for attr, value in attrs:
            if attr.lower() in self.safe_attributes:
                if attr.lower() in ['href', 'src']:
                    value = self._safe_url(value)
                elif attr.lower() == 'style':
                    value = self._safe_css(value)
                safe_attrs.append(f' {attr}="{value}"')
        return ''.join(safe_attrs)
    
    def _safe_url(self, url: str) -> str:
        """Varmista että URL on turvallinen."""
        if ':' in url:
            protocol = url.split(':', 1)[0].lower()
            if protocol not in self.allowed_protocols:
                return '#'
        return url
    
    def _safe_css(self, css: str) -> str:
        """Suodata turvallinen CSS."""
        # Poista vaaralliset CSS-ominaisuudet
        dangerous_properties = [
            'expression', 'javascript', 'vbscript', 'behavior',
            r'url\s*\(\s*javascript:', r'url\s*\(\s*vbscript:'
        ]
        
        for prop in dangerous_properties:
            css = re.sub(prop, '', css, flags=re.IGNORECASE)
        
        return css
    
    def _clean_text(self, text: str) -> str:
        """Siivoa teksti XSS-uhkia vastaan."""
        # Korvaa potentiaaliset script-yritykset
        replacements = {
            '<script': '&lt;script',
            '</script': '&lt;/script',
            'javascript:': 'javascript-blocked:',
            'onclick': 'data-onclick',
            'onload': 'data-onload',
            'onerror': 'data-onerror',
        }
        
        cleaned = text
        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)
        
        return cleaned
    
    def get_safe_html(self) -> str:
        """Palauta suodatettu HTML."""
        return ''.join(self.output)

class HTMLAnalyzer:
    """Analysoi HTML-sisältöä template-editoriin."""
    
    def __init__(self):
        self.sanitizer = HTMLSanitizer()
    
    def analyze_html_file(self, html_file_path: str) -> Dict[str, Any]:
        """Analysoi HTML-tiedoston rakenne."""
        try:
            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            return self.analyze_html_content(html_content)
        except Exception as e:
            print(f"❌ Virhe ladattaessa HTML-tiedostoa: {e}")
            return {}
    
    def analyze_html_content(self, html_content: str) -> Dict[str, Any]:
        """Analysoi HTML-sisällön rakenne."""
        # Suodata HTML ensin
        safe_html = self.sanitize_html(html_content)
        
        result = {
            'structure': self._analyze_structure(safe_html),
            'sections': self._extract_sections(safe_html),
            'safe_html': safe_html,
            'metadata': self._extract_metadata(html_content)
        }
        
        return result
    
    def sanitize_html(self, html_content: str) -> str:
        """Suodata HTML turvalliseksi."""
        self.sanitizer.output = []
        self.sanitizer.feed(html_content)
        return self.sanitizer.get_safe_html()
    
    def _analyze_structure(self, html_content: str) -> Dict[str, List[str]]:
        """Analysoi HTML-rakenteen."""
        structure = {
            'headings': [],
            'containers': [],
            'links': [],
            'images': []
        }
        
        # Otsikot
        headings = re.findall(r'<h([1-6])[^>]*>(.*?)</h\1>', html_content, re.DOTALL)
        structure['headings'] = [f'h{level}: {self._clean_text(content)}' 
                               for level, content in headings]
        
        # Kontit (div, section, article)
        containers = re.findall(r'<(div|section|article|main|header|footer)[^>]*>', html_content)
        structure['containers'] = list(set(containers))
        
        # Linkit
        links = re.findall(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', html_content, re.DOTALL)
        structure['links'] = [f'{self._clean_text(text)} -> {href}' 
                            for href, text in links if href]
        
        # Kuvat
        images = re.findall(r'<img[^>]*src="([^"]*)"[^>]*>', html_content)
        structure['images'] = images
        
        return structure
    
    def _extract_sections(self, html_content: str) -> Dict[str, str]:
        """Erota HTML osiin."""
        sections = {}
        
        # Header
        header_match = re.search(r'<header[^>]*>(.*?)</header>', html_content, re.DOTALL)
        if header_match:
            sections['header'] = header_match.group(1)
        
        # Main content
        main_match = re.search(r'<main[^>]*>(.*?)</main>', html_content, re.DOTALL)
        if main_match:
            sections['main'] = main_match.group(1)
        else:
            # Yritä löytää content div
            content_match = re.search(r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>', html_content, re.DOTALL)
            if content_match:
                sections['main'] = content_match.group(1)
        
        # Footer
        footer_match = re.search(r'<footer[^>]*>(.*?)</footer>', html_content, re.DOTALL)
        if footer_match:
            sections['footer'] = footer_match.group(1)
        
        return sections
    
    def _extract_metadata(self, html_content: str) -> Dict[str, str]:
        """Poimi metatiedot HTML:stä."""
        metadata = {}
        
        # Title
        title_match = re.search(r'<title>(.*?)</title>', html_content, re.DOTALL)
        if title_match:
            metadata['title'] = self._clean_text(title_match.group(1))
        
        # Meta description
        desc_match = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]*)"', html_content)
        if desc_match:
            metadata['description'] = desc_match.group(1)
        
        return metadata
    
    def _clean_text(self, text: str) -> str:
        """Siivoa teksti HTML-tageista."""
        return re.sub(r'<[^>]+>', '', text).strip()
