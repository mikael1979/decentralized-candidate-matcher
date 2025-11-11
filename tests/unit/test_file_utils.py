import pytest
import tempfile
import os
from src.core.file_utils import read_json_file, write_json_file, calculate_fingerprint

def test_read_write_json_file():
    """Testaa JSON-tiedostojen lukemista ja kirjoittamista"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        test_data = {"test": "data", "number": 123}
        write_json_file(f.name, test_data)
        
        # Lue takaisin
        read_data = read_json_file(f.name)
        assert read_data == test_data
        
    # Siivoa
    os.unlink(f.name)

def test_calculate_fingerprint():
    """Testaa fingerprintin laskentaa"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("test content\n# comment\n\nanother line")
        f.flush()
        
        fingerprint = calculate_fingerprint(f.name)
        assert len(fingerprint) == 64  # SHA256 pituus
        
    os.unlink(f.name)
