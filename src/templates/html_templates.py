# src/templates/html_templates.py (REFAKTOROITU)
#!/usr/bin/env python3
"""
HTML-pohjat profiilisivuille - Päämoduuli joka delegoida alempiin moduuleihin
"""
import json
from datetime import datetime
from typing import Dict

# Tuo uudet moduulit
from .css_generator import CSSGenerator, PARTY_COLOR_THEMES
from .candidate_templates import CandidateTemplates
from .party_templates import PartyTemplates


class HTMLTemplates:
    """HTML-pohjat profiilisivuille - Päämoduuli joka delegoida alempiin moduuleihin"""
    
    @staticmethod
    def get_base_css() -> str:
        """Hae perus-CSS tyylit CSSGeneratorista"""
        return CSSGenerator.get_base_css()
    
    @staticmethod
    def generate_party_html(*args, **kwargs) -> str:
        """Generoi HTML-profiilisivun puolueelle - delegoida PartyTemplatesille"""
        return PartyTemplates.generate_party_html(*args, **kwargs)
    
    @staticmethod 
    def generate_candidate_html(*args, **kwargs) -> str:
        """Generoi HTML-profiilisivun ehdokkaalle - delegoida CandidateTemplatesille"""
        return CandidateTemplates.generate_candidate_html(*args, **kwargs)

    # Yhteiset apumetodit pysyvät tässä
    @staticmethod
    def _get_ipfs_cids() -> Dict:
        """Hae IPFS-CID:t datatiedostoille"""
        import json
        from pathlib import Path
        
        ipfs_sync_file = Path("data/runtime/ipfs_sync.json")
        if ipfs_sync_file.exists():
            with open(ipfs_sync_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("ipfs_cids", {})
        return {}

    @staticmethod
    def _load_questions() -> list:
        """Lataa kysymykset"""
        import json
        from pathlib import Path
        
        questions_file = Path("data/runtime/questions.json")
        if questions_file.exists():
            with open(questions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("questions", [])
        return []
