# tests/test_installer.py
import pytest
from src.cli.install.installer import SystemInstaller
from src.cli.install.election_loader import validate_election_id

def test_validate_election_id():
    """Testaa vaalin validointia"""
    sample_data = {
        "hierarchy": {
            "continents": {
                "europe": {
                    "countries": {
                        "finland": {
                            "elections": {
                                "test_election": {
                                    "election_id": "test_election"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    assert validate_election_id("test_election", sample_data)
    assert not validate_election_id("nonexistent", sample_data)
