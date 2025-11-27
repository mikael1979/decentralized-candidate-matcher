#!/usr/bin/env python3
"""
Config-tiedostojen lataus ja tallennus
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigLoader:
    """Konfiguraatio-tiedostojen lataaja"""
    
    def __init__(self, base_path: Path = Path("config/elections")):
        self.base_path = base_path
    
    def load_election_config(self, election_id: str) -> Optional[Dict]:
        """Lataa vaalikonfiguraatio tiedostosta"""
        config_file = self.base_path / election_id / "election_config.json"
        
        if not config_file.exists():
            return None
            
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Config-tiedoston lukuvirhe: {e}")
            return None
    
    def save_election_config(self, election_id: str, config: Dict) -> bool:
        """Tallenna vaalikonfiguraatio tiedostoon"""
        try:
            config_dir = self.base_path / election_id
            config_dir.mkdir(parents=True, exist_ok=True)
            
            config_file = config_dir / "election_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Config-tiedoston tallennusvirhe: {e}")
            return False
    
    def config_exists(self, election_id: str) -> bool:
        """Tarkista onko config-tiedosto olemassa"""
        config_file = self.base_path / election_id / "election_config.json"
        return config_file.exists()
