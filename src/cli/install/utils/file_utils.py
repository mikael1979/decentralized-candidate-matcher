"""
Tiedostojen käsittely asennukselle.
"""
import json
from datetime import datetime
from pathlib import Path

# Import riippuvuudet
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from core.file_utils import ensure_directory


def initialize_basic_data_files(election_id):
    """
    Alustaa perus data-tiedostot vaalille
    
    Args:
        election_id: Vaalin tunniste
    """
    data_path = Path(f"data/runtime/{election_id}")
    ensure_directory(data_path)
    
    basic_files = {
        "meta.json": {
            "election_id": election_id,
            "created_at": datetime.now().isoformat(),
            "version": "2.0.0"
        },
        "questions.json": {"questions": []},
        "candidates.json": {"candidates": []},
        "parties.json": {"parties": []},
        "candidate_answers.json": {"answers": []}
    }
    
    for filename, content in basic_files.items():
        file_path = data_path / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        print(f"  ✅ {filename} alustettu")
