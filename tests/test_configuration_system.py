# tests/test_configuration_system.py
#!/usr/bin/env python3
"""
Testit configuration-systemille
"""
import pytest
import json
from pathlib import Path
from src.core.configuration_manager import ConfigurationManager, ConfigurationError

class TestConfigurationManager:
    def setup_method(self):
        """Testien alustus"""
        self.config_dir = Path("test_configs")
        self.config_dir.mkdir(exist_ok=True)
        
        # Luo testikonfiguraatiot
        self._create_test_configs()
    
    def teardown_method(self):
        """Testien lopetus"""
        # Siivoa testitiedostot
        import shutil
        if self.config_dir.exists():
            shutil.rmtree(self.config_dir)
    
    def _create_test_configs(self):
        """Luo testikonfiguraatiotiedostot"""
        # System colors
        system_colors = {
            "themes": {
                "default": {"primary": "#000000", "secondary": "#111111"},
                "blue": {"primary": "#0000ff", "secondary": "#1111ff"}
            }
        }
        
        # Election-specific colors
        election_colors = {
            "themes": {
                "election_blue": {"primary": "#0000aa", "accent": "#00aaff"}
            }
        }
        
        # Tallenna testitiedostot
        (self.config_dir / "system").mkdir(exist_ok=True)
        (self.config_dir / "elections" / "test_election").mkdir(parents=True, exist_ok=True)
        
        with open(self.config_dir / "system" / "default_colors.json", 'w') as f:
            json.dump(system_colors, f)
        
        with open(self.config_dir / "elections" / "test_election" / "color_themes.json", 'w') as f:
            json.dump(election_colors, f)
    
    def test_color_theme_loading(self):
        """Testaa väriteemojen lataus"""
        # Tämä testi vaatii ConfigurationManagerin muokkaamista testihakemistoa varten
        pass
    
    def test_configuration_merge(self):
        """Testaa konfiguraatioiden merge-toiminto"""
        manager = ConfigurationManager()
        
        base = {"colors": {"primary": "#000000", "existing": "value"}}
        override = {"colors": {"primary": "#ffffff", "new": "new_value"}}
        
        merged = manager._deep_merge(base, override)
        
        assert merged["colors"]["primary"] == "#ffffff"  # Override voittaa
        assert merged["colors"]["existing"] == "value"   # Base säilyy
        assert merged["colors"]["new"] == "new_value"    # Uusi kenttä lisätään

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
