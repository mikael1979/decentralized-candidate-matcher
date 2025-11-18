# Uusi: src/core/dynamic_config.py
class DynamicConfig:
    def __init__(self, election_id: str):
        self.election_id = election_id
        self.base_dir = Path("config")
    
    def get_template(self, template_type: str) -> Dict:
        """Hae template konfiguraatiosta"""
        template_path = self.base_dir / "templates" / f"{template_type}.base.json"
        return self._load_validated_template(template_path)
    
    def get_election_config(self) -> Dict:
        """Hae vaalikohtainen konfiguraatio"""
        election_path = self.base_dir / "elections" / self.election_id
        config = {}
        
        # Merge peräkkäin: base → election → overrides
        config.update(self._load_if_exists(election_path / "base_config.json"))
        config.update(self._load_if_exists(election_path / "election_config.json")) 
        config.update(self._load_if_exists(election_path / "overrides.json"))
        
        return config
