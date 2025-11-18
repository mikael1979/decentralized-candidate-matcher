#!/usr/bin/env python3
import click
import json
from datetime import datetime
import os
import sys
from pathlib import Path

# LISÄTTY: Lisää src hakemisto Python-polkuun
sys.path.insert(0, str(Path(__file__).parent.parent))

"""Perusluokka kaikille CLI-komennoille"""
import click
from core.data_manager import DataManager
from core.election_validator import ElectionValidator
from core.error_handling import handle_file_errors, validate_election_exists

class BaseCLI:
    def __init__(self, election_id: str):
        self.election_id = election_id
        self.data_manager = DataManager(election_id)
        self.validator = ElectionValidator()
    
    def validate_election(self):
        """Varmista että vaali on olemassa"""
        validate_election_exists(self.election_id)
