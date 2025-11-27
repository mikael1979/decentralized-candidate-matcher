#!/usr/bin/env python3
"""
Vaalikohtainen eristysmanageri - estää päällekkäisyydet
"""
import os
import hashlib
from pathlib import Path
from typing import Dict, Optional, Set
from datetime import datetime


class ElectionIsolationManager:
    """Hallitsee vaalikohtaista eristystä ja estää päällekkäisyydet"""
    
    def __init__(self):
        self.active_elections: Set[str] = set()
        self.election_locks: Dict[str, bool] = {}
        self.base_config_path = Path("config/elections")
        self.base_data_path = Path("data/elections")
    
    def validate_election_isolation(self, election_id: str, operation: str) -> Dict:
        """Validoi että operaatio ei aiheuta päällekkäisyyttä"""
        
        risks = []
        
        # 1. Tarkista että vaali on olemassa
        election_config_path = self.base_config_path / election_id / "election_config.json"
        if not election_config_path.exists():
            risks.append(f"Vaalia {election_id} ei löydy - uusi vaali?")
        
        # 2. Tarkista data-hakemiston eristys
        election_data_path = self.base_data_path / election_id
        if election_data_path.exists():
            # Tarkista että hakemisto sisältää oikean vaalin dataa
            expected_files = ['questions.json', 'candidates.json', 'answers.json']
            for file in expected_files:
                file_path = election_data_path / file
                if file_path.exists():
                    # Yksinkertainen sisällöntarkistus
                    if not self._validate_file_content(file_path, election_id):
                        risks.append(f"Tiedosto {file} ei kuulu vaaliin {election_id}")
        
        # 3. Tarkista aktiiviset vaalit
        if self.active_elections and election_id not in self.active_elections:
            risks.append(f"Vaali {election_id} ei ole aktiivinen - tarkista konteksti")
        
        return {
            "election_id": election_id,
            "operation": operation,
            "risks_found": len(risks),
            "risk_details": risks,
            "is_safe": len(risks) == 0
        }
    
    def _validate_file_content(self, file_path: Path, expected_election_id: str) -> bool:
        """Tarkista että tiedoston sisältö kuuluu oikeaan vaaliin"""
        try:
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Yksinkertainen sisällöntarkistus
            if expected_election_id in content:
                return True
                
            # Tarkista JSON-rakenne
            data = json.loads(content)
            if isinstance(data, dict):
                # Tarkista yleisimmät vaalikohtaiset kentät
                if data.get('election_id') == expected_election_id:
                    return True
                if data.get('election') == expected_election_id:
                    return True
                    
            return False
            
        except:
            return False
    
    def acquire_election_lock(self, election_id: str, operation: str) -> bool:
        """Hae lukko vaalin käsittelyyn"""
        if election_id in self.election_locks and self.election_locks[election_id]:
            return False  # Vaali on jo lukittu
            
        self.election_locks[election_id] = True
        self.active_elections.add(election_id)
        print(f"🔒 LUKITTU: {election_id} - {operation}")
        return True
    
    def release_election_lock(self, election_id: str):
        """Vapauta vaalin lukko"""
        if election_id in self.election_locks:
            self.election_locks[election_id] = False
            print(f"🔓 VAPAUTETTU: {election_id}")
    
    def detect_cross_election_contamination(self) -> Dict:
        """Tunnista mahdolliset päällekkäisyydet"""
        contamination_risks = []
        
        # Tarkista config-hakemisto
        if self.base_config_path.exists():
            for election_dir in self.base_config_path.iterdir():
                if election_dir.is_dir():
                    config_file = election_dir / "election_config.json"
                    if config_file.exists():
                        validation = self.validate_election_isolation(election_dir.name, "config_check")
                        if not validation["is_safe"]:
                            contamination_risks.append({
                                "election": election_dir.name,
                                "type": "config",
                                "risks": validation["risk_details"]
                            })
        
        # Tarkista data-hakemisto
        if self.base_data_path.exists():
            for election_dir in self.base_data_path.iterdir():
                if election_dir.is_dir():
                    validation = self.validate_election_isolation(election_dir.name, "data_check")
                    if not validation["is_safe"]:
                        contamination_risks.append({
                            "election": election_dir.name,
                            "type": "data", 
                            "risks": validation["risk_details"]
                        })
        
        return {
            "scan_timestamp": datetime.now().isoformat(),
            "contamination_risks_found": len(contamination_risks),
            "risks": contamination_risks
        }
    
    def get_election_health_report(self, election_id: str) -> Dict:
        """Hae vaalin terveysraportti"""
        config_validation = self.validate_election_isolation(election_id, "health_check")
        data_validation = self.validate_election_isolation(election_id, "data_health_check")
        
        return {
            "election_id": election_id,
            "timestamp": datetime.now().isoformat(),
            "config_health": config_validation,
            "data_health": data_validation,
            "overall_health": config_validation["is_safe"] and data_validation["is_safe"]
        }
