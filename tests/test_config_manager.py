"""Testit config_manager:lle"""
import pytest
import json
import tempfile
from pathlib import Path
from src.core.config_manager import ConfigManager


def test_config_generation():
    """Testaa configin generointia templatesta"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Luo testitemplate
        template_path = Path(temp_dir) / "config.base.json"
        template_data = {
            "metadata": {
                "election_id": "{{ELECTION_ID}}",
                "network_id": "{{NETWORK_ID}}",
                "deployed_at": "{{TIMESTAMP}}",
                "version": "{{VERSION}}"
            },
            "network_config": {
                "node_type": "{{NODE_TYPE}}"
            },
            "test_value": "static"
        }
        
        with open(template_path, 'w') as f:
            json.dump(template_data, f)
        
        # Testaa config manager
        manager = ConfigManager(
            config_path=Path(temp_dir) / "config.json",
            template_path=template_path
        )
        
        config = manager.generate_config(
            election_id="TestVaalit2025",
            node_type="worker",
            version="1.0.0"
        )
        
        assert config["metadata"]["election_id"] == "TestVaalit2025"
        assert config["metadata"]["network_id"] == "TestVaalit2025_network"
        assert config["network_config"]["node_type"] == "worker"
        assert config["test_value"] == "static"
        assert "config_hash" in config["metadata"]


def test_config_save_load():
    """Testaa configin tallennus ja lataus"""
    with tempfile.TemporaryDirectory() as temp_dir:
        template_path = Path(temp_dir) / "config.base.json"
        config_path = Path(temp_dir) / "config.json"
        
        # Template TÄYTYY sisältää metadata-kentän
        template_data = {
            "metadata": {
                "election_id": "{{ELECTION_ID}}",
                "network_id": "{{NETWORK_ID}}",
                "deployed_at": "{{TIMESTAMP}}",
                "version": "{{VERSION}}"
            },
            "network_config": {
                "node_type": "{{NODE_TYPE}}"
            },
            "test_section": {
                "value": "test"
            }
        }
        
        with open(template_path, 'w') as f:
            json.dump(template_data, f)
        
        manager = ConfigManager(config_path=config_path, template_path=template_path)
        config = manager.generate_config("TestVaalit")
        
        # Tallentaa
        saved_path = manager.save_config(config)
        assert saved_path.exists()
        
        # Lataa
        loaded_config = manager.load_config()
        assert loaded_config["metadata"]["election_id"] == "TestVaalit"


def test_election_id_resolution():
    """Testaa vaali-ID:n hakua"""
    with tempfile.TemporaryDirectory() as temp_dir:
        template_path = Path(temp_dir) / "config.base.json"
        config_path = Path(temp_dir) / "config.json"
        
        template_data = {
            "metadata": {
                "election_id": "{{ELECTION_ID}}",
                "network_id": "{{NETWORK_ID}}",
                "deployed_at": "{{TIMESTAMP}}",
                "version": "{{VERSION}}"
            },
            "network_config": {
                "node_type": "{{NODE_TYPE}}"
            }
        }
        
        with open(template_path, 'w') as f:
            json.dump(template_data, f)
        
        manager = ConfigManager(config_path=config_path, template_path=template_path)
        
        # Generoi config
        config = manager.generate_config("ConfigVaalit")
        manager.save_config(config)
        
        # Testaa ID:n hakua
        assert manager.get_election_id() == "ConfigVaalit"
        assert manager.get_election_id("ParamVaalit") == "ParamVaalit"  # Parametri voittaa
        assert manager.get_election_id(None) == "ConfigVaalit"  # Configista


def test_config_integrity_validation():
    """Testaa configin eheyden validointia"""
    with tempfile.TemporaryDirectory() as temp_dir:
        template_path = Path(temp_dir) / "config.base.json"
        config_path = Path(temp_dir) / "config.json"
        
        template_data = {
            "metadata": {
                "election_id": "{{ELECTION_ID}}",
                "network_id": "{{NETWORK_ID}}",
                "deployed_at": "{{TIMESTAMP}}",
                "version": "{{VERSION}}"
            },
            "network_config": {
                "node_type": "{{NODE_TYPE}}"
            },
            "test_data": "original"
        }
        
        with open(template_path, 'w') as f:
            json.dump(template_data, f)
        
        manager = ConfigManager(config_path=config_path, template_path=template_path)
        config = manager.generate_config("IntegrityTest")
        
        # Testaa validi config suoraan (ei tallenneta tiedostoon)
        is_valid, message = manager.validate_config_integrity(config)
        assert is_valid == True, f"Validation failed: {message}"
        assert "valid" in message
        
        # Testaa muutettu config
        corrupted_config = config.copy()
        corrupted_config["test_data"] = "modified"
        
        is_valid, message = manager.validate_config_integrity(corrupted_config)
        assert is_valid == False
        assert "integrity check failed" in message
        
        # Testaa tallennetun configin validointi
        manager.save_config(config)
        is_valid, message = manager.validate_config_integrity()  # Lataa automaattisesti tallennetusta
        assert is_valid == True, f"Saved config validation failed: {message}"
        assert "valid" in message


def test_get_config_value():
    """Testaa config-arvon hakua key pathilla"""
    with tempfile.TemporaryDirectory() as temp_dir:
        template_path = Path(temp_dir) / "config.base.json"
        config_path = Path(temp_dir) / "config.json"
        
        template_data = {
            "metadata": {
                "election_id": "{{ELECTION_ID}}",
                "network_id": "{{NETWORK_ID}}", 
                "deployed_at": "{{TIMESTAMP}}",
                "version": "{{VERSION}}"
            },
            "network_config": {
                "node_type": "{{NODE_TYPE}}"
            },
            "election_config": {
                "answer_scale": {"min": -5, "max": 5},
                "nested": {"value": "test"}
            }
        }
        
        with open(template_path, 'w') as f:
            json.dump(template_data, f)
        
        manager = ConfigManager(config_path=config_path, template_path=template_path)
        config = manager.generate_config("ConfigValueTest")
        manager.save_config(config)
        
        # Testaa arvojen hakua
        assert manager.get_config_value("metadata.election_id") == "ConfigValueTest"
        assert manager.get_config_value("election_config.answer_scale.min") == -5
        assert manager.get_config_value("election_config.answer_scale.max") == 5
        assert manager.get_config_value("election_config.nested.value") == "test"
        assert manager.get_config_value("nonexistent.path", "default") == "default"
        assert manager.get_config_value("nonexistent.path") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
