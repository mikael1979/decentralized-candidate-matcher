#!/usr/bin/env python3
"""
Testit PartyCommands-luokalle - KORJATTU VERSIO
"""
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from src.cli.party_commands import PartyCommands

class TestPartyCommands:
    """Testit PartyCommands-luokalle"""
    
    def setup_method(self):
        """Testien alustus"""
        self.temp_dir = tempfile.mkdtemp()
        self.election_id = "Testivaali2026"
        self.commands = PartyCommands(self.election_id)
        self.commands.parties_file = str(Path(self.temp_dir) / "parties.json")
    
    def teardown_method(self):
        """Testien siivous"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_propose_party_creates_new_file(self):
        """Testaa että uuden puolueen ehdotus luo tiedoston"""
        result = self.commands.propose_party(
            name_fi="Testipuolue",
            description_fi="Testikuvaus",
            email="test@example.com",
            website="https://example.com",
            founding_year="2024"
        )
        
        assert result == True
        assert Path(self.commands.parties_file).exists()
        
        # Tarkista sisältö
        with open(self.commands.parties_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert "parties" in data
        assert len(data["parties"]) == 1
        assert data["parties"][0]["name"]["fi"] == "Testipuolue"
        assert data["parties"][0]["metadata"]["contact_email"] == "test@example.com"
    
    def test_propose_party_duplicate_prevention(self):
        """Testaa että samannimistä puoluetta ei voi ehdottaa kahteen kertaan"""
        # Ensimmäinen ehdotus
        self.commands.propose_party(name_fi="Testipuolue")
        
        # Toinen ehdotus samalla nimellä
        result = self.commands.propose_party(name_fi="Testipuolue")
        
        assert result == False
    
    def test_propose_party_validation(self):
        """Testaa syötteiden validointia"""
        # Testaa ilman nimeä
        result = self.commands.propose_party(name_fi="")
        assert result == False
        
        # Testaa virheellistä sähköpostia
        result = self.commands.propose_party(name_fi="Testi", email="invalid-email")
        assert result == False
        
        # Testaa virheellistä URL:ia
        result = self.commands.propose_party(name_fi="Testi", website="not-a-url")
        assert result == False
    
    @patch('click.echo')
    def test_list_parties_empty(self, mock_echo):
        """Testaa puoluelistaus tyhjällä rekisterillä"""
        result = self.commands.list_parties()
        
        assert result == False
        mock_echo.assert_called_with("💡 Käytä: python src/cli/manage_parties.py propose --election Jumaltenvaalit2026 --name-fi 'Nimi'")
    
    @patch('click.echo')
    def test_list_parties_with_data(self, mock_echo):
        """Testaa puoluelistaus datalla"""
        test_data = {
            "metadata": {
                "version": "1.0.0",
                "created": "2024-01-01T12:00:00",
                "last_updated": "2024-01-01T12:00:00",
                "election_id": self.election_id
            },
            "quorum_config": {
                "min_nodes_for_verification": 3,
                "approval_threshold_percent": 60
            },
            "parties": [
                {
                    "party_id": "party_001",
                    "name": {"fi": "Vahvistettu Puolue", "en": "Verified Party", "sv": "Verifierat Parti"},
                    "description": {"fi": "Kuvaus", "en": "Description", "sv": "Beskrivning"},
                    "registration": {
                        "verification_status": "verified",
                        "verified_by": ["node_1", "node_2", "node_3"],
                        "verification_timestamp": "2024-01-01T12:00:00"
                    },
                    "candidates": ["cand_1", "cand_2"],
                    "metadata": {
                        "contact_email": "verified@example.com",
                        "website": "https://verified.example.com"
                    }
                }
            ],
            "verification_history": []
        }
        
        with open(self.commands.parties_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        result = self.commands.list_parties()
        
        assert result == True
        calls_text = " ".join(str(call) for call in mock_echo.call_args_list)
        assert "Vahvistettu Puolue" in calls_text
    
    @patch('click.echo')
    def test_get_party_info_found(self, mock_echo):
        """Testaa yksittäisen puolueen tiedot löytyessä"""
        test_data = {
            "metadata": {"election_id": self.election_id},
            "parties": [
                {
                    "party_id": "party_test_001",
                    "name": {"fi": "Testipuolue", "en": "Test Party", "sv": "Testparti"},
                    "description": {"fi": "Testikuvaus", "en": "Test description", "sv": "Testbeskrivning"},
                    "registration": {
                        "verification_status": "verified",
                        "verified_by": ["node_1", "node_2", "node_3"],
                        "verification_timestamp": "2024-01-01T12:00:00",
                        "proposed_at": "2024-01-01T10:00:00",
                        "proposed_by": "system"
                    },
                    "candidates": ["cand_1", "cand_2"],
                    "metadata": {
                        "contact_email": "test@example.com",
                        "website": "https://example.com",
                        "founding_year": "2024"
                    }
                }
            ],
            "verification_history": []
        }
        
        with open(self.commands.parties_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        result = self.commands.get_party_info("party_test_001")
        
        assert result == True
        assert any("Testipuolue" in str(call) for call in mock_echo.call_args_list)
    
    @patch('click.echo')
    def test_get_party_info_not_found(self, mock_echo):
        """Testaa yksittäisen puolueen tiedot ei löydy"""
        test_data = {
            "metadata": {"election_id": self.election_id},
            "parties": [],
            "verification_history": []
        }
        
        with open(self.commands.parties_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        result = self.commands.get_party_info("party_nonexistent")
        
        assert result == False
        mock_echo.assert_called_with("❌ Puoluetta 'party_nonexistent' ei löydy")
