# src/templates/template_utils.py
#!/usr/bin/env python3
"""
Template-aputyökalut
"""

class TemplateUtils:
    """Aputyökaluja template-generointiin"""
    
    @staticmethod
    def sanitize_html(text: str) -> str:
        """Siivoa HTML-turvalliseksi"""
        if not text:
            return ""
        # Yksinkertainen sanitointi - tuotannossa käytä properia kirjastoa
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#x27;'))
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100) -> str:
        """Rajaa tekstin pituus"""
        if not text or len(text) <= max_length:
            return text
        return text[:max_length].rsplit(' ', 1)[0] + '...'
    
    @staticmethod
    def format_datetime(dt_string: str) -> str:
        """Muotoile datetime merkkijono"""
        from datetime import datetime
        try:
            dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
            return dt.strftime('%d.%m.%Y %H:%M')
        except (ValueError, AttributeError):
            return dt_string
