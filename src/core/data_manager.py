"""Keskitetty data-hallinta kaikille moduuleille"""
import json
from pathlib import Path
from typing import Dict, Any
from .error_handling import safe_json_read, safe_json_write

class DataManager:
    def __init__(self, election_id: str):
        self.election_id = election_id
        self.data_dir = Path(f"data/runtime/{election_id}")
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def load_data(self, filename: str) -> Dict[str, Any]:
        """Lataa data-tiedosto"""
        file_path = self.data_dir / filename
        return safe_json_read(str(file_path))
    
    def save_data(self, filename: str, data: Dict[str, Any]):
        """Tallenna data-tiedosto"""
        file_path = self.data_dir / filename
        safe_json_write(str(file_path), data)
    
    def get_questions(self):
        return self.load_data("questions.json")
    
    def get_candidates(self):
        return self.load_data("candidates.json")
    
    def get_parties(self):
        return self.load_data("parties.json")
