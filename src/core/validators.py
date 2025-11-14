#!/usr/bin/env python3
"""
Data-validointifunktiot - UUSI TIEDOSTO
"""
import re
from typing import Dict, Any, Optional

class DataValidator:
    """Data-validointiluokka kaikille tietotyypeille"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validoi sähköpostiosoite"""
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validoi URL-osoite"""
        if not url:
            return False
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, url))
    
    @staticmethod
    def validate_answer_value(value: int) -> bool:
        """Validoi vastausarvo (-5 - +5)"""
        return -5 <= value <= 5
    
    @staticmethod
    def validate_confidence_level(confidence: int) -> bool:
        """Validoi luottamustaso (1-5)"""
        return 1 <= confidence <= 5
    
    @staticmethod
    def validate_party_data(party_data: Dict) -> bool:
        """Validoi puoluedata"""
        required_fields = ["name", "description"]
        for field in required_fields:
            if field not in party_data:
                return False
            if "fi" not in party_data[field]:
                return False
        return True
    
    @staticmethod
    def validate_candidate_data(candidate_data: Dict) -> bool:
        """Validoi ehdokasdata"""
        if "basic_info" not in candidate_data:
            return False
        if "name" not in candidate_data["basic_info"]:
            return False
        if "fi" not in candidate_data["basic_info"]["name"]:
            return False
        return True
    
    @staticmethod
    def validate_question_data(question_data: Dict) -> bool:
        """Validoi kysymysdata"""
        if "content" not in question_data:
            return False
        if "question" not in question_data["content"]:
            return False
        if "fi" not in question_data["content"]["question"]:
            return False
        return True

def validate_election_id(election_id: str) -> bool:
    """Validoi vaalin tunnisteen"""
    if not election_id:
        return False
    # Sallii aakkosnumeeriset ja alaviiva-merkit
    pattern = r'^[a-zA-Z0-9_]+$'
    return bool(re.match(pattern, election_id))

def validate_candidate_id(candidate_id: str) -> bool:
    """Validoi ehdokkaan tunnisteen"""
    if not candidate_id:
        return False
    pattern = r'^cand_[a-zA-Z0-9_]+$'
    return bool(re.match(pattern, candidate_id))

def validate_party_id(party_id: str) -> bool:
    """Validoi puolueen tunnisteen"""
    if not party_id:
        return False
    pattern = r'^party_[a-zA-Z0-9_]+$'
    return bool(re.match(pattern, party_id))

def validate_question_id(question_id: str) -> bool:
    """Validoi kysymyksen tunnisteen"""
    if not question_id:
        return False
    pattern = r'^q_[a-zA-Z0-9_]+$'
    return bool(re.match(pattern, question_id))
