# tests/cli/install/utils/test_election_utils.py - korjattu
"""
Testit election_utils-moduulille
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from src.cli.install.utils.election_utils import (
    validate_election_id,
    get_election_info,
    format_election_display,
    show_elections_hierarchy
)


@pytest.fixture
def sample_elections_data():
    """Testidata vaaleille"""
    return {
        "hierarchy": {
            "continents": {
                "europe": {
                    "name": {"fi": "Eurooppa"},  # LISÄTTY
                    "countries": {
                        "finland": {
                            "name": {"fi": "Suomi"},  # LISÄTTY
                            "elections": {
                                "presidential": {
                                    "election_id": "finland_presidential_2024",
                                    "name": {"fi": "Presidentinvaalit 2024"},
                                    "status": "upcoming"
                                }
                            }
                        }
                    }
                }
            },
            "other_elections": {
                "olympian": {
                    "election_id": "olympian_gods_2024",
                    "name": {"fi": "Olimpian jumalten vaalit 2024"},
                    "status": "active"
                }
            }
        }
    }


def test_validate_election_id(sample_elections_data):
    """Testaa vaalin validointia"""
    # Testaa löytyvä vaali
    assert validate_election_id("finland_presidential_2024", sample_elections_data)
    assert validate_election_id("olympian_gods_2024", sample_elections_data)
    
    # Testaa ei-löytyvä vaali
    assert not validate_election_id("nonexistent_election", sample_elections_data)
    assert not validate_election_id("", sample_elections_data)
    assert not validate_election_id("test", None)
    assert not validate_election_id(None, sample_elections_data)  # Lisätty
    assert not validate_election_id("test", {})  # Lisätty


def test_get_election_info(sample_elections_data):
    """Testaa vaalin tietojen hakemista"""
    # Testaa löytyvä vaali
    info = get_election_info("finland_presidential_2024", sample_elections_data)
    assert info is not None
    assert info["election_id"] == "finland_presidential_2024"
    
    # Testaa toinen vaali
    info = get_election_info("olympian_gods_2024", sample_elections_data)
    assert info is not None
    assert info["election_id"] == "olympian_gods_2024"
    
    # Testaa ei-löytyvä
    assert get_election_info("nonexistent", sample_elections_data) is None
    assert get_election_info("", sample_elections_data) is None
    assert get_election_info(None, sample_elections_data) is None  # Lisätty


def test_format_election_display():
    """Testaa vaalin muotoilua"""
    election_data = {
        "election_id": "test_election",
        "name": {"fi": "Testivaali"},
        "status": "active"
    }
    
    result = format_election_display(election_data)
    assert "Testivaali" in result
    assert "test_election" in result
    assert "🟢" in result  # active status icon
    assert result.startswith("    ")  # 4 välilyöntiä
    
    # Testaa tuntematon status
    election_data["status"] = "unknown_status"
    result = format_election_display(election_data)
    assert "⚪" in result  # default icon
    
    # Testaa tyhjä data
    assert format_election_display(None) == "Unknown election"
    assert format_election_display({}) == "Unknown election"


def test_validate_empty_data():
    """Testaa tyhjällä datalla"""
    assert not validate_election_id("test", {})
    assert not validate_election_id("test", {"hierarchy": {}})
    assert not validate_election_id("", {"hierarchy": {"continents": {}}})


def test_show_elections_hierarchy(capsys, sample_elections_data):
    """Testaa vaalihierarkian näyttämistä"""
    show_elections_hierarchy(sample_elections_data)
    captured = capsys.readouterr()
    
    assert "KÄYTÖSSÄ OLEVAT VAALIT" in captured.out
    assert "EUROOPPA" in captured.out  # Nyt isolla!
    assert "Suomi" in captured.out
    assert "Presidentinvaalit 2024" in captured.out
    assert "Olimpian jumalten vaalit 2024" in captured.out
    assert "🟡" in captured.out  # upcoming
    assert "🟢" in captured.out  # active
