#!/usr/bin/env python3
"""
Elections List Manager - Hallinnoi keskitettyä vaalilistaa
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class ElectionsListManager:
    """Hallinnoi elections_list.json tiedostoa"""
    
    def __init__(self, elections_file: str = "elections_list.json"):
        self.elections_file = Path(elections_file)
        self._ensure_elections_file()
    
    def _ensure_elections_file(self):
        """Varmista että elections_list.json on olemassa"""
        if not self.elections_file.exists():
            self._create_default_elections_list()
    
    def _create_default_elections_list(self):
        """Luo oletus elections_list.json"""
        default_data = {
            "metadata": {
                "version": "1.0.0",
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "ipfs_cid": "QmDefaultElectionsList",
                "description": {
                    "fi": "Käsin ylläpidetty vaalilista",
                    "en": "Manually maintained elections list",
                    "sv": "Manuellt underhållen vallista"
                }
            },
            "elections": [],
            "election_types": {
                "presidential": {
                    "description": {
                        "fi": "Presidentinvaalit",
                        "en": "Presidential elections", 
                        "sv": "Presidentval"
                    },
                    "term_years": 6,
                    "max_terms": 2
                },
                "municipal": {
                    "description": {
                        "fi": "Kunnallisvaalit",
                        "en": "Municipal elections",
                        "sv": "Kommunalval"
                    },
                    "term_years": 4,
                    "max_terms": None
                },
                "test": {
                    "description": {
                        "fi": "Testivaalit",
                        "en": "Test elections",
                        "sv": "Testval"
                    },
                    "term_years": 1,
                    "max_terms": None
                }
            },
            "system_config": {
                "default_timelock_enabled": True,
                "default_grace_period_hours": 48,
                "default_community_managed": True,
                "supported_languages": ["fi", "en", "sv"],
                "version_control": True,
                "ipfs_backed": True
            }
        }
        
        with open(self.elections_file, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Luotu: {self.elections_file}")
    
    def add_election(self, election_data: Dict) -> bool:
        """Lisää uusi vaali elections_list.json:iin"""
        try:
            with open(self.elections_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Tarkista että vaali-ID on uniikki
            existing_ids = [e['election_id'] for e in data['elections']]
            if election_data['election_id'] in existing_ids:
                print(f"⚠️  Vaali-ID '{election_data['election_id']}' on jo olemassa")
                return False
            
            # Lisää vaali
            data['elections'].append(election_data)
            
            # Päivitä metadata
            data['metadata']['last_updated'] = datetime.now().isoformat()
            data['metadata']['total_elections'] = len(data['elections'])
            
            # Tallenna
            with open(self.elections_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Vaali '{election_data['election_id']}' lisätty elections_list.json:iin")
            return True
            
        except Exception as e:
            print(f"❌ Virhe vaalin lisäämisessä: {e}")
            return False
    
    def remove_election(self, election_id: str) -> bool:
        """Poista vaali elections_list.json:ista"""
        try:
            with open(self.elections_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Etsi ja poista vaali
            original_count = len(data['elections'])
            data['elections'] = [e for e in data['elections'] if e['election_id'] != election_id]
            
            if len(data['elections']) == original_count:
                print(f"❌ Vaalia '{election_id}' ei löydy")
                return False
            
            # Päivitä metadata
            data['metadata']['last_updated'] = datetime.now().isoformat()
            data['metadata']['total_elections'] = len(data['elections'])
            
            # Tallenna
            with open(self.elections_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Vaali '{election_id}' poistettu elections_list.json:ista")
            return True
            
        except Exception as e:
            print(f"❌ Virhe vaalin poistamisessa: {e}")
            return False
    
    def update_election_status(self, election_id: str, new_status: str) -> bool:
        """Päivitä vaalin tila"""
        try:
            with open(self.elections_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Etsi vaali
            for election in data['elections']:
                if election['election_id'] == election_id:
                    old_status = election.get('status', 'unknown')
                    election['status'] = new_status
                    
                    # Päivitä metadata
                    data['metadata']['last_updated'] = datetime.now().isoformat()
                    
                    # Tallenna
                    with open(self.elections_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    
                    print(f"✅ Vaali '{election_id}' tilaksi päivitetty: {old_status} → {new_status}")
                    return True
            
            print(f"❌ Vaalia '{election_id}' ei löydy")
            return False
            
        except Exception as e:
            print(f"❌ Virhe vaalin päivityksessä: {e}")
            return False
    
    def list_elections(self):
        """Listaa kaikki vaalit"""
        try:
            with open(self.elections_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print("\n📋 KAIKKI VAAILIT:")
            print("=" * 60)
            
            for election in data['elections']:
                status = election.get('status', 'unknown')
                dates = ", ".join([phase['date'] for phase in election['dates']])
                
                print(f"🏛️  {election['name']['fi']}")
                print(f"   🆔 ID: {election['election_id']}")
                print(f"   📅 Päivät: {dates}")
                print(f"   🏷️  Tyyppi: {election['type']}")
                print(f"   📊 Tila: {status}")
                print()
                
        except Exception as e:
            print(f"❌ Virhe vaalien listauksessa: {e}")
    
    def get_election_info(self, election_id: str) -> Optional[Dict]:
        """Hae tietyn vaalin tiedot"""
        try:
            with open(self.elections_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for election in data['elections']:
                if election['election_id'] == election_id:
                    return election
            
            return None
            
        except Exception as e:
            print(f"❌ Virhe vaalin haussa: {e}")
            return None

def main():
    """Pääohjelma"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Elections List Manager")
    parser.add_argument('action', choices=['list', 'add', 'remove', 'status', 'init'],
                       help='Toiminto')
    parser.add_argument('--election-id', help='Vaalin ID')
    parser.add_argument('--status', choices=['upcoming', 'active', 'completed', 'cancelled'],
                       help='Uusi tila')
    
    args = parser.parse_args()
    
    manager = ElectionsListManager()
    
    if args.action == 'init':
        print("✅ Elections list varmistettu")
        
    elif args.action == 'list':
        manager.list_elections()
        
    elif args.action == 'add':
        if not args.election_id:
            print("❌ --election-id vaaditaan")
            return
        
        # Tämä pitäisi integroida create_install_config.py:hyn
        print("⚠️  Toteuta add-toiminto create_install_config.py:ssä")
        
    elif args.action == 'remove':
        if not args.election_id:
            print("❌ --election-id vaaditaan")
            return
        
        manager.remove_election(args.election_id)
        
    elif args.action == 'status':
        if not args.election_id or not args.status:
            print("❌ --election-id ja --status vaaditaan")
            return
        
        manager.update_election_status(args.election_id, args.status)

if __name__ == "__main__":
    main()
