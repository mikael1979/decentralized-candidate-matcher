#!/usr/bin/env python3
"""
Worker node election installer - lataa ja asentaa vaalit IPFS:stä
"""
import json
import os
import requests
from pathlib import Path
from typing import Dict, List, Optional
import sys

# Lisää projektin juuri Python-polkuun
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.core.ipfs_client import IPFSClient
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Varmista että olet projektin juurihakemistossa")
    sys.exit(1)

class ElectionInstaller:
    """Lataa ja asentaa vaalit IPFS:stä"""
    
    def __init__(self, worker_config_path: str = "config/worker_config.json"):
        self.worker_config_path = Path(worker_config_path)
        self.config = self._load_config()
        self.ipfs_client = IPFSClient.get_client("worker_node")
        
    def _load_config(self) -> Dict:
        """Lataa workerin konfiguraatio"""
        if self.worker_config_path.exists():
            with open(self.worker_config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def download_election_registry(self, registry_cid: str) -> Dict:
        """Lataa vaalilista IPFS:stä"""
        try:
            print(f"📋 Ladataan vaalilistaa: {registry_cid}")
            registry_data = self.ipfs_client.retrieve_election_data(registry_cid)
            return registry_data.get('data', {})
        except Exception as e:
            print(f"❌ Vaalilistan lataus epäonnistui: {e}")
            return {}
    
    def download_election_config(self, election_id: str, config_cid: str) -> Dict:
        """Lataa vaalin asennustiedosto IPFS:stä"""
        try:
            print(f"📥 Ladataan vaalin {election_id} asetuksia: {config_cid}")
            config_data = self.ipfs_client.retrieve_election_data(config_cid)
            return config_data.get('data', {})
        except Exception as e:
            print(f"❌ Vaalin {election_id} asetusten lataus epäonnistui: {e}")
            return {}
    
    def download_election_data(self, data_source: Dict, target_path: Path) -> bool:
        """Lataa vaalidata IPFS:stä"""
        try:
            cid = data_source.get('cid')
            filename = data_source.get('filename')
            
            if not cid or not filename:
                print(f"❌ Virheellinen data-lähde: {data_source}")
                return False
            
            print(f"📄 Ladataan {filename}: {cid}")
            
            # Hae data IPFS:stä
            data = self.ipfs_client.retrieve_election_data(cid)
            
            if 'data' in data:
                # Tallenna tiedostoon
                full_path = target_path / filename
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(full_path, 'w', encoding='utf-8') as f:
                    json.dump(data['data'], f, indent=2, ensure_ascii=False)
                
                print(f"✅ {filename} tallennettu: {full_path}")
                return True
            else:
                print(f"❌ Dataa ei löytynyt CID:llä {cid}")
                return False
                
        except Exception as e:
            print(f"❌ Datan lataus epäonnistui: {e}")
            return False
    
    def install_election(self, election_id: str, config_cid: str) -> bool:
        """Asenna vaali paikallisesti"""
        try:
            print(f"🚀 Asennetaan vaalia: {election_id}")
            
            # 1. Lataa vaalin asetukset
            election_config = self.download_election_config(election_id, config_cid)
            if not election_config:
                return False
            
            # 2. Luo vaalin hakemistorakenne
            election_path = Path(f"data/elections/{election_id}")
            election_path.mkdir(parents=True, exist_ok=True)
            
            # 3. Tallenna vaalin asetukset
            config_file = election_path / "election_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(election_config, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Vaalin asetukset tallennettu: {config_file}")
            
            # 4. Lataa kaikki vaalidata
            data_sources = election_config.get('data_sources', {})
            success_count = 0
            total_sources = len(data_sources)
            
            for data_type, data_source in data_sources.items():
                if self.download_election_data(data_source, election_path):
                    success_count += 1
            
            # 5. Tarkista onnistuminen
            if success_count == total_sources:
                print(f"🎉 Vaali {election_id} asennettu onnistuneesti!")
                
                # Luo meta.json
                from datetime import datetime
                meta_data = {
                    "election_id": election_id,
                    "name": election_config['election_info']['name'],
                    "description": election_config['election_info']['description'],
                    "installed_at": datetime.now().isoformat(),
                    "data_sources": list(data_sources.keys()),
                    "status": "installed"
                }
                
                meta_file = election_path / "meta.json"
                with open(meta_file, 'w', encoding='utf-8') as f:
                    json.dump(meta_data, f, indent=2, ensure_ascii=False)
                
                return True
            else:
                print(f"⚠️ Vaali {election_id} asennettu osittain ({success_count}/{total_sources} dataa)")
                return False
                
        except Exception as e:
            print(f"❌ Vaalin {election_id} asennus epäonnistui: {e}")
            return False
    
    def list_available_elections(self, registry_cid: str) -> List[Dict]:
        """Listaa saatavilla olevat vaalit"""
        registry = self.download_election_registry(registry_cid)
        elections = registry.get('elections', {})
        
        available_elections = []
        for election_id, election_info in elections.items():
            available_elections.append({
                'election_id': election_id,
                'name': election_info['name'],
                'description': election_info['description'],
                'status': election_info.get('status', 'unknown'),
                'config_cid': election_info['config_cid']
            })
        
        return available_elections

# CLI-komento worker node:ille
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Worker Node - Vaalien asennus IPFS:stä")
    parser.add_argument("--list", help="Listaa saatavilla olevat vaalit", action="store_true")
    parser.add_argument("--install", help="Asenna tietty vaali", type=str)
    parser.add_argument("--registry", help="Vaalilistan CID", default="QmTestRegistryCID123456789")
    
    args = parser.parse_args()
    
    installer = ElectionInstaller()
    
    if args.list:
        print("📋 saatavilla olevat vaalit:")
        elections = installer.list_available_elections(args.registry)
        for election in elections:
            print(f"  🗳️  {election['election_id']}: {election['name']['fi']}")
            print(f"     📝 {election['description']['fi']}")
            print(f"     🔧 Asenna: python src/nodes/worker/election_installer.py --install {election['election_id']}")
            print()
    
    elif args.install:
        # Käytä testi CID:itä demoamiseen
        test_configs = {
            "jumaltenvaalit2026": "QmTestElectionConfig123456789",
            "testivaali2024": "QmTestConfig789012345"
        }
        
        config_cid = test_configs.get(args.install)
        if config_cid:
            installer.install_election(args.install, config_cid)
        else:
            print(f"❌ Tuntematon vaali: {args.install}")
            print("💡 Käytettävissä olevat vaalit:")
            for election_id in test_configs.keys():
                print(f"  - {election_id}")
