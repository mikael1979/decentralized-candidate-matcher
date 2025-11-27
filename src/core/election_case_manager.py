#!/usr/bin/env python3
"""
Case sensitivity manager vaalien nimille - estää sekoittumiset
"""
from pathlib import Path
from typing import Dict, List, Optional


class ElectionCaseManager:
    """Hallitsee vaalien nimien case sensitivity ongelmia"""
    
    def __init__(self):
        self.base_config_path = Path("config/elections")
        self.base_data_path = Path("data/elections")
    
    def detect_case_conflicts(self) -> Dict:
        """Tunnista case sensitivity konfliktit"""
        conflicts = []
        
        if self.base_config_path.exists():
            elections = [d.name for d in self.base_config_path.iterdir() if d.is_dir()]
            
            # Etsi duplikaatit case insensitive vertailulla
            lower_map = {}
            for election in elections:
                lower_name = election.lower()
                if lower_name in lower_map:
                    lower_map[lower_name].append(election)
                else:
                    lower_map[lower_name] = [election]
            
            # Tunnista konfliktit
            for lower_name, variants in lower_map.items():
                if len(variants) > 1:
                    conflicts.append({
                        "case_insensitive_name": lower_name,
                        "conflicting_names": variants,
                        "type": "config_directory"
                    })
        
        return {
            "case_conflicts_found": len(conflicts),
            "conflicts": conflicts
        }
    
    def normalize_election_name(self, election_name: str) -> str:
        """Normalisoi vaalin nimi vakio muotoon"""
        # Käytä lowercasea vakiona, mutta säilytä alkuperäinen formaatti
        return election_name.lower()
    
    def get_canonical_election_name(self, election_name: str) -> Optional[str]:
        """Hae kanoninen nimi vaalille (jos se on olemassa)"""
        normalized = self.normalize_election_name(election_name)
        
        if self.base_config_path.exists():
            elections = [d.name for d in self.base_config_path.iterdir() if d.is_dir()]
            for existing_election in elections:
                if self.normalize_election_name(existing_election) == normalized:
                    return existing_election
        
        return None
    
    def validate_election_name_consistency(self, election_name: str) -> Dict:
        """Validoi vaalin nimen johdonmukaisuus"""
        normalized = self.normalize_election_name(election_name)
        canonical = self.get_canonical_election_name(election_name)
        
        issues = []
        
        if canonical and canonical != election_name:
            issues.append(f"Case inconsistency: '{election_name}' vs canonical '{canonical}'")
        
        # Tarkista data-hakemiston johdonmukaisuus
        config_exists = (self.base_config_path / election_name).exists()
        data_exists = (self.base_data_path / election_name).exists()
        
        canonical_config_exists = canonical and (self.base_config_path / canonical).exists()
        canonical_data_exists = canonical and (self.base_data_path / canonical).exists()
        
        if config_exists and not data_exists and canonical_data_exists:
            issues.append(f"Data exists for canonical name '{canonical}' but not for '{election_name}'")
        
        return {
            "election_name": election_name,
            "normalized_name": normalized,
            "canonical_name": canonical,
            "issues_found": len(issues),
            "issues": issues,
            "is_consistent": len(issues) == 0
        }
    
    def get_election_name_recommendations(self) -> Dict:
        """Hae suosituksia vaalien nimien korjauksiin"""
        conflicts_report = self.detect_case_conflicts()
        recommendations = []
        
        for conflict in conflicts_report["conflicts"]:
            conflicting_names = conflict["conflicting_names"]
            # Suosittele ensimmäistä nimeä kanoniseksi
            recommended_canonical = conflicting_names[0]
            
            for name in conflicting_names[1:]:
                recommendations.append({
                    "from": name,
                    "to": recommended_canonical,
                    "reason": f"Case conflict with {recommended_canonical}",
                    "type": "rename_recommendation"
                })
        
        return {
            "recommendations": recommendations,
            "total_recommendations": len(recommendations)
        }
