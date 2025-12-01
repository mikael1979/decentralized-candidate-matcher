# src/cli/install/election_loader.py
"""
Vaalien lataus ja hallinta
"""
import json
from pathlib import Path
from datetime import datetime, timedelta

from core.ipfs.client import IPFSClient
from core.file_utils import read_json_file, write_json_file, ensure_directory
from .utils import get_static_marker_cid


class ElectionLoader:
    """Lataa ja hallinnoi vaalitietoja"""
    
    def __init__(self, ipfs_client=None):
        self.ipfs_client = ipfs_client or IPFSClient()
        self.cache_dir = Path("data/cache")
        ensure_directory(self.cache_dir)
    
    def check_system_installed(self):
        """
        Tarkista onko järjestelmä asennettu IPFS:ään
        
        Returns:
            tuple: (is_installed, elections_cid)
        """
        try:
            # Hae oikea CID first_install.json:sta
            static_marker_cid = get_static_marker_cid()
            print(f"🔍 Tarkistetaan staattista merkkiä: {static_marker_cid}")
            
            # Yritä ladata staattista merkkitiedostoa
            marker_data = self.ipfs_client.get_json(static_marker_cid)
            if marker_data and marker_data.get("system") == "decentralized-candidate-matcher":
                print("✅ Hajautettu vaalikone löytyi IPFS:stä")
                
                # Hae elections lista first_install.json:sta
                try:
                    install_info_path = Path("data/installation/first_install.json")
                    if install_info_path.exists():
                        install_info = read_json_file(install_info_path)
                        elections_cid = install_info.get("elections_list_cid")
                        if elections_cid:
                            return True, elections_cid
                except Exception as e:
                    print(f"⚠️  Elections CID load failed: {e}")
                        
        except Exception as e:
            print(f"⚠️  IPFS-tarkistus epäonnistui: {e}")
        
        return False, None
    
    def load_elections_list(self, elections_cid, use_cache=True, max_cache_age_hours=24):
        """
        Lataa elections lista IPFS:stä välimuistilla
        
        Args:
            elections_cid: Elections listan CID
            use_cache: Käytä välimuistia (default True)
            max_cache_age_hours: Kuinka vanha välimuisti sallitaan
            
        Returns:
            dict: Elections listan data tai None
        """
        cache_path = self.cache_dir / f"elections_{elections_cid}.json"
        
        # Tarkista välimuisti
        if use_cache and cache_path.exists():
            try:
                cache_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
                max_age = timedelta(hours=max_cache_age_hours)
                
                if cache_age < max_age:
                    cached_data = read_json_file(cache_path)
                    if cached_data:
                        print("✅ Vaalilista ladattu välimuistista")
                        return cached_data
                    else:
                        print("⚠️  Välimuistissa ei ole kelvollista dataa")
                else:
                    print(f"⚠️  Välimuisti on liian vanha ({cache_age})")
                    
            except Exception as e:
                print(f"⚠️  Välimuistin lataus epäonnistui: {e}")
        
        # Lataa IPFS:stä
        try:
            print("🌐 Ladataan vaalilistaa IPFS:stä...")
            elections_data = self.ipfs_client.get_json(elections_cid)
            
            if elections_data:
                print("✅ Vaalilista ladattu IPFS:stä")
                # Tallenna välimuistiin
                write_json_file(cache_path, elections_data)
                return elections_data
            else:
                print("❌ Vaalilistan lataus IPFS:stä epäonnistui")
                # Yritä vielä vanhasta välimuistista
                if cache_path.exists():
                    print("⚠️  Yritetään ladata vanhasta välimuistista...")
                    try:
                        return read_json_file(cache_path)
                    except Exception as e:
                        print(f"❌ Vanhasta välimuististakin lataus epäonnistui: {e}")
                        
        except Exception as e:
            print(f"❌ Vaalilistan lataus epäonnistui: {e}")
            # Yritä välimuistia viimeisenä keinona
            if cache_path.exists():
                print("⚠️  Yritetään ladata välimuistista (viimeinen yritys)...")
                try:
                    return read_json_file(cache_path)
                except:
                    pass
        
        return None
    
    def show_elections_hierarchy(self, elections_data):
        """
        Näytä vaalihierarkia käyttäjälle
        
        Args:
            elections_data: Elections listan data
        """
        print("\n🌍 KÄYTÖSSÄ OLEVAT VAALIT:")
        print("=" * 50)
        
        hierarchy = elections_data.get("hierarchy", {})
        
        # Näytä mantereet
        for continent_id, continent_data in hierarchy.get("continents", {}).items():
            continent_name = continent_data["name"]["fi"]
            print(f"\n🏔️  {continent_name.upper()}")
            print("-" * 30)
            
            for country_id, country_data in continent_data.get("countries", {}).items():
                country_name = country_data["name"]["fi"]
                print(f"  🇺🇳 {country_name}")
                
                for election_id, election_data in country_data.get("elections", {}).items():
                    from .utils import format_election_display
                    print(f"    {format_election_display(election_data)}")
        
        # Näytä muut vaalit
        other_elections = hierarchy.get("other_elections", {})
        if other_elections:
            print(f"\n🎭 MUUT VAALIT:")
            print("-" * 30)
            
            for category, election_data in other_elections.items():
                if isinstance(election_data, dict) and "election_id" in election_data:
                    from .utils import format_election_display
                    print(f"  {format_election_display(election_data)}")
    
    def get_all_election_ids(self, elections_data):
        """
        Hae kaikki vaalien ID:t
        
        Args:
            elections_data: Elections listan data
            
        Returns:
            list: Kaikki election_id:t
        """
        if not elections_data:
            return []
            
        election_ids = []
        hierarchy = elections_data.get("hierarchy", {})
        
        # Mantereiden vaalit
        for continent_data in hierarchy.get("continents", {}).values():
            for country_data in continent_data.get("countries", {}).values():
                for election_data in country_data.get("elections", {}).values():
                    if isinstance(election_data, dict) and "election_id" in election_data:
                        election_ids.append(election_data["election_id"])
        
        # Muut vaalit
        other_elections = hierarchy.get("other_elections", {})
        if isinstance(other_elections, dict):
            for category, election_data in other_elections.items():
                if isinstance(election_data, dict) and "election_id" in election_data:
                    election_ids.append(election_data["election_id"])
        
        return sorted(election_ids)
