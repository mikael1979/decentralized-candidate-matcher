# src/core/configuration_manager.py - PARANNETTU VERSIO
#!/usr/bin/env python3
"""
Configuration Manager - Korvaa kovakoodatun datan dynaamisilla konfiguraatioilla
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigurationManager:
    def __init__(self, election_id: Optional[str] = None):
        self.election_id = election_id
        self.config_base = Path("config")
        self._ensure_config_structure()
    
    def _ensure_config_structure(self):
        """Varmista että konfiguraatiohakemistorakenne on olemassa"""
        directories = [
            self.config_base / "elections" / "_template",
            self.config_base / "system",
            self.config_base / "templates"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Luo oletusväritiedosto jos se puuttuu
        default_colors_path = self.config_base / "system" / "default_colors.json"
        if not default_colors_path.exists():
            self._create_default_colors()
    
    def _create_default_colors(self):
        """Luo oletusväriteemat"""
        default_colors = {
            "metadata": {
                "version": "1.0.0",
                "description": "Oletusväriteemat vaalijärjestelmälle"
            },
            "themes": {
                "default": {
                    "primary": "#2c3e50",
                    "secondary": "#3498db",
                    "accent": "#e74c3c",
                    "background": "#ecf0f1",
                    "text": "#2c3e50"
                }
            }
        }
        
        with open(self.config_base / "system" / "default_colors.json", 'w', encoding='utf-8') as f:
            json.dump(default_colors, f, indent=2, ensure_ascii=False)
    
    def get_color_themes(self) -> Dict[str, Any]:
        """Hae väriteemat - ensin vaalikohtaiset, sitten oletukset"""
        # Lataa oletusvärit
        default_themes = self._load_config("system/default_colors.json")
        
        # Lataa vaalikohtaiset värit jos saatavilla
        election_themes = {}
        if self.election_id:
            election_path = f"elections/{self.election_id}/color_themes.json"
            election_themes = self._load_config(election_path)
        
        # Merge: election-specific overrides defaults
        return {**default_themes.get("themes", {}), **election_themes.get("themes", {})}
    
    def get_election_config(self) -> Dict[str, Any]:
        """Hae vaalikonfiguraatio"""
        if not self.election_id:
            raise ValueError("Election ID required")
        
        # Lataa peruskonfiguraatio
        base_config = self._load_config("elections/_template/election_config.json")
        
        # Lataa vaalikohtaiset ylikirjoitukset
        election_config = self._load_config(f"elections/{self.election_id}/election_config.json")
        
        # Merge konfiguraatiot
        return self._deep_merge(base_config, election_config)
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Lataa konfiguraatiotiedosto - TURVALLINEN VERSIO"""
        full_path = self.config_base / config_path
        
        # Jos tiedostoa ei ole, palauta tyhjä sanakirja
        if not full_path.exists():
            return {}
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
                # Tarkista että tiedosto ei ole tyhjä
                if not content:
                    return {}
                    
                return json.loads(content)
                
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"⚠️  Varoitus: Konfiguraatiotiedosto {full_path} on virheellinen: {e}")
            return {}  # Palauta tyhjä sanakirja virheen sijaan
    
    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Syvämerge kahden sanakirjan välillä"""
        result = base.copy()
        
        for key, value in override.items():
            if (key in result and isinstance(result[key], dict) 
                and isinstance(value, dict)):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result

class ConfigurationError(Exception):
    """Konfiguraatiojärjestelmän virheet"""
    pass
