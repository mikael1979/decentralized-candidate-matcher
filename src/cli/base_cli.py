"""Perusluokka kaikille CLI-komennoille"""
import click
from src.core.data_manager import DataManager
from src.core.election_validator import ElectionValidator
from src.core.error_handling import handle_file_errors, validate_election_exists

class BaseCLI:
    def __init__(self, election_id: str):
        self.election_id = election_id
        self.data_manager = DataManager(election_id)
        self.validator = ElectionValidator()
    
    def validate_election(self):
        """Varmista että vaali on olemassa"""
        validate_election_exists(self.election_id)
