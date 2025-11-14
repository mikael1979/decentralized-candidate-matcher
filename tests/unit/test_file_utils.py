#!/usr/bin/env python3
"""
Testit file_utils-moduulille - KORJATTU VERSIO
"""
import pytest
import json
import tempfile
from pathlib import Path

# KORJATTU: Oikeat importit
try:
    from src.core.file_utils import read_json_file, write_json_file, calculate_file_hash
except ImportError:
    from core.file_utils import read_json_file, write_json_file, calculate_file_hash

class TestFileUtils:
    """Testit file_utils-funktioille"""

    def test_read_json_file_existing(self):
        """Testaa olemassa olevan JSON-tiedoston lukeminen"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump({"test": "data"}, f)
            temp_path = f.name

        try:
            data = read_json_file(temp_path)
            assert data == {"test": "data"}
        finally:
            Path(temp_path).unlink()

    def test_read_json_file_missing_with_default(self):
        """Testaa puuttuvan JSON-tiedoston lukeminen oletusarvolla"""
        data = read_json_file("non_existent.json", default={"default": "value"})
        assert data == {"default": "value"}

    def test_read_json_file_missing_without_default(self):
        """Testaa puuttuvan JSON-tiedoston lukeminen ilman oletusarvoa"""
        with pytest.raises(Exception):  # Pitäisi heittää poikkeus
            read_json_file("non_existent.json")

    def test_write_json_file(self):
        """Testaa JSON-tiedoston kirjoittaminen"""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.json"
            test_data = {"key": "value"}

            write_json_file(str(file_path), test_data)

            assert file_path.exists()
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            assert data == test_data

    def test_calculate_file_hash(self):
        """Testaa tiedoston tiivisteen laskeminen"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("test content")
            temp_path = f.name

        try:
            file_hash = calculate_file_hash(temp_path)
            # Tarkista että saadaan 64 merkin pituinen hex-tiiviste (SHA-256)
            assert len(file_hash) == 64
            assert all(c in '0123456789abcdef' for c in file_hash)
        finally:
            Path(temp_path).unlink()

    def test_ensure_directory(self):
        """Testaa hakemiston varmistamista"""
        from src.core.file_utils import ensure_directory
        
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir) / "test_subdir"
            ensure_directory(str(test_dir))
            
            assert test_dir.exists()
            assert test_dir.is_dir()

    def test_file_exists(self):
        """Testaa tiedoston olemassaolon tarkistus"""
        from src.core.file_utils import file_exists
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("test")
            temp_path = f.name

        try:
            assert file_exists(temp_path) == True
            assert file_exists("non_existent_file.txt") == False
        finally:
            Path(temp_path).unlink()
