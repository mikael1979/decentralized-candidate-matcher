"""
Testit election_loader-moduulille
"""
import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import json

from src.cli.install.election_loader import ElectionLoader


@pytest.fixture
def mock_ipfs_client():
    """Mock IPFSClient"""
    mock = Mock()
    mock.get_json.return_value = {
        "system": "decentralized-candidate-matcher",
        "version": "2.0.0"
    }
    return mock


@pytest.fixture
def election_loader(mock_ipfs_client):
    """ElectionLoader-instanssi mockilla"""
    return ElectionLoader(ipfs_client=mock_ipfs_client)


def test_get_all_election_ids():
    """Testaa kaikkien vaalien ID:den hakemista"""
    loader = ElectionLoader()
    
    sample_data = {
        "hierarchy": {
            "continents": {
                "europe": {
                    "countries": {
                        "finland": {
                            "elections": {
                                "pres": {"election_id": "pres_2024"},
                                "parl": {"election_id": "parl_2023"}
                            }
                        }
                    }
                }
            },
            "other_elections": {
                "eu": {"election_id": "eu_2024"},
                "un": {"election_id": "un_2024"}
            }
        }
    }
    
    election_ids = loader.get_all_election_ids(sample_data)
    assert len(election_ids) == 4
    assert "pres_2024" in election_ids
    assert "eu_2024" in election_ids
    assert sorted(election_ids) == election_ids  # Pitäisi olla sortattu
    
    # Testaa tyhjällä datalla
    assert loader.get_all_election_ids(None) == []
    assert loader.get_all_election_ids({}) == []
    assert loader.get_all_election_ids({"hierarchy": {}}) == []


@patch('src.cli.install.election_loader.get_static_marker_cid')
@patch('src.cli.install.election_loader.read_json_file')
def test_check_system_installed(mock_read_json, mock_get_cid, election_loader, mock_ipfs_client):
    """Testaa järjestelmän asennuksen tarkistusta"""
    # Mockaa funktiot
    mock_get_cid.return_value = "test_cid_123"
    mock_read_json.return_value = {"elections_list_cid": "elections_cid_456"}
    
    # Testaa onnistunut tarkistus
    is_installed, elections_cid = election_loader.check_system_installed()
    
    assert is_installed is True
    assert elections_cid == "elections_cid_456"
    mock_ipfs_client.get_json.assert_called_with("test_cid_123")
    mock_read_json.assert_called()
    
    # Testaa epäonnistunut tarkistus (väärä systeemi)
    mock_ipfs_client.get_json.return_value = {"system": "wrong_system"}
    is_installed, elections_cid = election_loader.check_system_installed()
    assert is_installed is False
    assert elections_cid is None
    
    # Testaa epäonnistunut tarkistus (ei dataa)
    mock_ipfs_client.get_json.return_value = None
    is_installed, elections_cid = election_loader.check_system_installed()
    assert is_installed is False
    assert elections_cid is None


def test_show_elections_hierarchy(capsys):
    """Testaa vaalihierarkian näyttämistä"""
    loader = ElectionLoader()
    
    sample_data = {
        "hierarchy": {
            "continents": {
                "europe": {
                    "name": {"fi": "Eurooppa"},
                    "countries": {
                        "finland": {
                            "name": {"fi": "Suomi"},
                            "elections": {
                                "pres": {
                                    "election_id": "test_election",
                                    "name": {"fi": "Testivaali"},
                                    "status": "active"
                                }
                            }
                        }
                    }
                }
            },
            "other_elections": {
                "eu": {
                    "election_id": "eu_test",
                    "name": {"fi": "EU-testivaali"},
                    "status": "upcoming"
                }
            }
        }
    }
    
    loader.show_elections_hierarchy(sample_data)
    captured = capsys.readouterr()
    
    assert "KÄYTÖSSÄ OLEVAT VAALIT" in captured.out
    assert "EUROOPPA" in captured.out  # Muutettu: nyt isolla!
    assert "Suomi" in captured.out
    assert "Testivaali" in captured.out
    assert "EU-testivaali" in captured.out
    assert "🟢" in captured.out  # active
    assert "🟡" in captured.out  # upcoming


def test_cache_directory_creation():
    """Testaa että cache-hakemisto luodaan"""
    with patch('pathlib.Path.mkdir') as mock_mkdir:
        loader = ElectionLoader()
        mock_mkdir.assert_called_with(exist_ok=True, parents=True)
