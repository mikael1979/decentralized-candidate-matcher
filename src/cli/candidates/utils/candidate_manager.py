"""
candidate_manager.py - Candidate data management core logic
"""
import json
import os
import uuid
from pathlib import Path
from datetime import datetime

from src.core.file_utils import read_json_file, write_json_file, ensure_directory

class CandidateManager:
    """Core candidate data management functionality"""
    
    def __init__(self, election_id=None):
        self.election_id = election_id
        self.data_path = self._get_data_path()
        
    def _get_data_path(self):
        """Get candidate data file path"""
        from src.core.config_manager import get_election_id, get_data_path
        
        election_id = self.election_id or get_election_id()
        data_path = get_data_path(election_id)
        return data_path / "candidates.json"
    
    def load_candidates(self):
        """Load candidates from file"""
        candidates_file = self.data_path
        
        if not candidates_file.exists():
            return {"candidates": [], "metadata": {"last_updated": datetime.now().isoformat()}}
        
        try:
            return read_json_file(candidates_file, {"candidates": [], "metadata": {}})
        except Exception as e:
            print(f"❌ Virhe ladattaessa ehdokkaita: {e}")
            return {"candidates": [], "metadata": {}}
    
    def save_candidates(self, data):
        """Save candidates to file"""
        candidates_file = self.data_path
        
        try:
            # Ensure directory exists
            candidates_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Update metadata
            data["metadata"] = {
                "last_updated": datetime.now().isoformat(),
                "total_candidates": len(data.get("candidates", []))
            }
            
            write_json_file(candidates_file, data)
            return True
        except Exception as e:
            print(f"❌ Virhe tallennettaessa ehdokkaita: {e}")
            return False
    
    def find_candidate(self, identifier):
        """Find candidate by ID or name"""
        data = self.load_candidates()
        candidates = data.get("candidates", [])
        
        for candidate in candidates:
            # Check by ID
            if candidate.get("id") == identifier:
                return candidate
            
            # Check by Finnish name
            name_fi = candidate.get("basic_info", {}).get("name", {}).get("fi", "")
            if name_fi.lower() == identifier.lower():
                return candidate
        
        return None
    
    def validate_candidate_name(self, name_fi):
        """Validate candidate name uniqueness"""
        data = self.load_candidates()
        candidates = data.get("candidates", [])
        
        existing_names = [
            c.get("basic_info", {}).get("name", {}).get("fi", "").lower().strip()
            for c in candidates
            if c.get("basic_info", {}).get("name", {}).get("fi")
        ]
        
        return name_fi.lower().strip() not in existing_names
    
    def generate_candidate_id(self):
        """Generate unique candidate ID"""
        return f"cand_{uuid.uuid4().hex[:8]}"
