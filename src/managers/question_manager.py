from pathlib import Path
from typing import Dict, List
from src.core.file_utils import read_json_file, write_json_file

class QuestionManager:
    def __init__(self, election_id: str, data_dir: str = "data/runtime"):
        self.election_id = election_id
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def submit_question(self, question_data: Dict) -> str:
        """Lähetä uusi kysymys järjestelmään"""
        tmp_file = self.data_dir / "tmp_new_questions.json"
        
        # Lue nykyinen data tai alusta uusi
        if tmp_file.exists():
            data = read_json_file(str(tmp_file))
        else:
            data = {"questions": [], "metadata": {"election_id": self.election_id}}
        
        # Lisää uusi kysymys
        question_id = f"q_{len(data['questions']) + 1}"
        question_data["local_id"] = question_id
        data["questions"].append(question_data)
        
        # Tallenna
        write_json_file(str(tmp_file), data)
        return question_id
    
    def sync_tmp_to_new(self) -> List[str]:
        """Synkronoi tmp kysymykset new_questions.json:ään"""
        tmp_file = self.data_dir / "tmp_new_questions.json"
        new_file = self.data_dir / "new_questions.json"
        
        if not tmp_file.exists():
            return []
        
        tmp_data = read_json_file(str(tmp_file))
        new_data = read_json_file(str(new_file)) if new_file.exists() else {"questions": []}
        
        # Siirrä kysymykset
        synced_questions = []
        for question in tmp_data["questions"]:
            new_data["questions"].append(question)
            synced_questions.append(question["local_id"])
        
        # Tallenna ja tyhjennä tmp
        write_json_file(str(new_file), new_data)
        write_json_file(str(tmp_file), {"questions": []})
        
        return synced_questions
