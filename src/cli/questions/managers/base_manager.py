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


class BaseQuestionManager:
    """Perusmanageri kysymysten tiedostokäsittelylle."""
    
    def __init__(self, election_id: str = None):
        self.election_id = election_id or get_election_id()
        self.data_path = get_data_path(self.election_id)
        self.questions_file = Path(self.data_path) / "questions.json"
    
    def load_questions(self) -> Dict[str, Any]:
        """Lataa kysymykset JSON-tiedostosta."""
        if not self.questions_file.exists():
            return {"questions": []}
        return read_json_file(self.questions_file)
    
    def save_questions(self, questions_data: Dict[str, Any]) -> None:
        """Tallenna kysymykset JSON-tiedostoon."""
        ensure_directory(self.questions_file.parent)
        write_json_file(self.questions_file, questions_data)
