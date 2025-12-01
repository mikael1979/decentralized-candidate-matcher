"""
Perusmanageri tiedostokäsittelylle.
"""
import sys
from pathlib import Path
from typing import Dict, Any

# Lisää src hakemisto Python-polkuun
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from core import get_election_id, get_data_path
from core.file_utils import read_json_file, write_json_file, ensure_directory


class BaseAnswerManager:
    """Perusmanageri vastausten tiedostokäsittelylle."""
    
    def __init__(self, election_id: str = None):
        self.election_id = election_id or get_election_id()
        self.data_path = get_data_path(self.election_id)
        self.answers_file = Path(self.data_path) / "candidate_answers.json"
    
    def load_answers(self) -> Dict[str, Any]:
        """Lataa vastaukset JSON-tiedostosta."""
        if not self.answers_file.exists():
            return {"answers": []}
        return read_json_file(self.answers_file)
    
    def save_answers(self, answers_data: Dict[str, Any]) -> None:
        """Tallenna vastaukset JSON-tiedostoon."""
        ensure_directory(self.answers_file.parent)
        write_json_file(self.answers_file, answers_data)
