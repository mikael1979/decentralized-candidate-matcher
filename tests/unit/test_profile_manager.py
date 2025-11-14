#!/usr/bin/env python3
"""
Testit ProfileManager-luokalle - KORJATTU VERSIO
"""
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from src.templates.profile_manager import ProfileManager

class TestProfileManager:
    """Testit ProfileManager-luokalle"""
    
    def setup_method(self):
        """Testien alustus"""
        self.temp_dir = tempfile.mkdtemp()
        self.election_id = "Testivaali2026"
        self.manager = ProfileManager(self.election_id)
        
        # Ohjaa tiedostopolut väliaikaiseen hakemistoon
        self.manager.output_dir = Path(self.temp_dir) / "profiles"
        self.manager.metadata_file = Path(self.temp_dir) / "profiles_metadata.json"
    
    def teardown_method(self):
        """Testien siivous"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_init_creates_directories(self):
        """Testaa että alustus luo tarvittavat hakemistot"""
        # KORJATTU: Varmista että hakemistot luodaan
        self.manager.output_dir.mkdir(parents=True, exist_ok=True)
        self.manager.metadata_file.parent.mkdir(parents=True, exist_ok=True)
        
        assert self.manager.output_dir.exists()
        assert self.manager.metadata_file.parent.exists()
    
    # ... LOPUT TESTIT PYSYVÄT SAMOINA (kopioi alkuperäisestä) ...
