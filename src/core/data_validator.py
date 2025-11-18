#!/usr/bin/env python3
"""
Data-eheyden valvonta ja validointi
"""
import os
from .file_utils import read_json_file

def validate_candidate_uniqueness(candidates_file, new_candidate_name):
    """Tarkista että ehdokasnimi on uniikki"""
    if not os.path.exists(candidates_file):
        return True
    
    try:
        data = read_json_file(candidates_file, {"candidates": []})
        existing_names = [
            c["basic_info"]["name"]["fi"].lower().strip() 
            for c in data.get("candidates", [])
        ]
        return new_candidate_name.lower().strip() not in existing_names
    except Exception:
        return True

def get_candidate_by_id_or_name(candidates_file, identifier):
    """Etsi ehdokas ID:n tai nimen perusteella"""
    if not os.path.exists(candidates_file):
        return None
    
    try:
        data = read_json_file(candidates_file, {"candidates": []})
        for candidate in data.get("candidates", []):
            if (candidate["candidate_id"] == identifier or 
                candidate["basic_info"]["name"]["fi"] == identifier):
                return candidate
    except Exception:
        pass
    
    return None
