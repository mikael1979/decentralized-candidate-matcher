[file name]: ipfs_sync_engine.py
[file content begin]
"""
IPFS synkronointimoottori mock-IPFS:n ja oikean IPFS:n välille
Mahdollistaa siirtymisen mock -> production
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import tempfile
import os

try:
    import ipfshttpclient
    REAL_IPFS_AVAILABLE = True
except ImportError:
    REAL_IPFS_AVAILABLE = False
    print("⚠️  ipfshttpclient ei saatavilla, oikea IPFS pois käytöstä")

class RealIPFS:
    """Oikea IPFS-asiakas py-ipfs-http-client:lla"""
    
    def __init__(self, host: str = '/ip4/127.0.0.1/tcp/5001'):
        if not REAL_IPFS_AVAILABLE:
            raise ImportError("ipfshttpclient ei asennettu")
        
        try:
            self.client = ipfshttpclient.connect(host)
            self.connected = True
            print(f"✅ Yhdistetty oikeaan IPFS:ään: {host}")
        except Exception as e:
            self.connected = False
            print(f"❌ IPFS-yhteysvirhe: {e}")
            raise
    
    def upload(self, data: Dict[str, Any]) -> str:
        """Lähetä data oikeaan IPFS:ään"""
        if not self.connected:
            raise ConnectionError("IPFS-yhteys katkaistu")
        
        # Kirjoita data väliaikaiseen tiedostoon
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            temp_path = f.name
        
        try:
            # Lähetä IPFS:ään
            result = self.client.add(temp_path)
            cid = result['Hash']
            
            # Pinnaa data pysyväksi
            self.client.pin.add(cid)
            
            print(f"✅ Lähetetty oikeaan IPFS:ään - CID: {cid}")
            return cid
        except Exception as e:
            print(f"❌ IPFS-upload virhe: {e}")
            raise
        finally:
            # Siivoa väliaikainen tiedosto
            os.unlink(temp_path)
    
    def download(self, cid: str) -> Optional[Dict[str, Any]]:
        """Lataa data oikeasta IPFS:stä"""
        if not self.connected:
            raise ConnectionError("IPFS-yhteys katkaistu")
        
        try:
            # Hae data IPFS:stä
            content = self.client.cat(cid)
            data = json.loads(content.decode('utf-8'))
            
            print(f"✅ Ladattu oikeasta IPFS:stä - CID: {cid}")
            return data
        except Exception as e:
            print(f"❌ IPFS-download virhe CID:llä {cid}: {e}")
            return None
    
    def pin(self, cid: str) -> bool:
        """Pinnaa data oikeassa IPFS:ässä"""
        if not self.connected:
            return False
        
        try:
            self.client.pin.add(cid)
            print(f"✅ Pinnattu oikeassa IPFS:ässä - CID: {cid}")
            return True
        except Exception as e:
            print(f"❌ Pin-virhe: {e}")
            return False
    
    def unpin(self, cid: str) -> bool:
        """Poista pinnaus oikeasta IPFS:stä"""
        if not self.connected:
            return False
        
        try:
            self.client.pin.rm(cid)
            print(f"✅ Poistettu pinnaus - CID: {cid}")
            return True
        except Exception as e:
            print(f"❌ Unpin-virhe: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Hae tilastot oikeasta IPFS:stä"""
        if not self.connected:
            return {"connected": False}
        
        try:
            # Yksinkertaiset tilastot
            id_info = self.client.id()
            return {
                "connected": True,
                "peer_id": id_info['ID'],
                "agent_version": id_info['AgentVersion'],
                "protocol_version": id_info['ProtocolVersion']
            }
        except Exception as e:
            return {"connected": False, "error": str(e)}

class IPFSSyncEngine:
    """
    Synkronointimoottori mock-IPFS:n ja oikean IPFS:n välille
    """
    
    def __init__(self, mock_ipfs, real_ipfs_host: str = '/ip4/127.0.0.1/tcp/5001'):
        self.mock_ipfs = mock_ipfs
        self.real_ipfs = None
        self.sync_status_file = Path("ipfs_sync_status.json")
        self.sync_status = self._load_sync_status()
        
        # Yritä yhdistää oikeaan IPFS:ään
        try:
            self.real_ipfs = RealIPFS(real_ipfs_host)
            self.sync_status["real_ipfs_available"] = True
        except Exception as e:
            self.real_ipfs = None
            self.sync_status["real_ipfs_available"] = False
            print(f"⚠️  Oikea IPFS ei saatavilla: {e}")
    
    def _load_sync_status(self) -> Dict[str, Any]:
        """Lataa synkronointitila"""
        try:
            with open(self.sync_status_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "sync_enabled": False,
                "last_sync": None,
                "synced_cids": [],
                "failed_syncs": [],
                "real_ipfs_available": False,
                "sync_mode": "mock_only"  # mock_only, hybrid, real_only
            }
    
    def _save_sync_status(self):
        """Tallenna synkronointitila"""
        with open(self.sync_status_file, 'w', encoding='utf-8') as f:
            json.dump(self.sync_status, f, indent=2, ensure_ascii=False)
    
    def enable_sync(self, mode: str = "hybrid"):
        """Ota synkronointi käyttöön"""
        valid_modes = ["mock_only", "hybrid", "real_only"]
        if mode not in valid_modes:
            raise ValueError(f"Virheellinen tila: {mode}. Sallitut: {valid_modes}")
        
        if mode != "mock_only" and not self.real_ipfs:
            raise ValueError("Oikea IPFS ei saatavilla hybrid/real_only -tilaan")
        
        self.sync_status["sync_enabled"] = True
        self.sync_status["sync_mode"] = mode
        self._save_sync_status()
        
        print(f"✅ IPFS-synkronointi käytössä tilassa: {mode}")
    
    def disable_sync(self):
        """Poista synkronointi käytöstö"""
        self.sync_status["sync_enabled"] = False
        self._save_sync_status()
        print("✅ IPFS-synkronointi pois käytöstä")
    
    def upload(self, data: Dict[str, Any]) -> str:
        """
        Lähetä data IPFS:ään nykyisen synkronointitilan mukaisesti
        """
        # 1. Aina mock-IPFS:ään
        mock_cid = self.mock_ipfs.upload(data)
        
        # 2. Synkronoi oikeaan IPFS:ään jos käytössä
        if (self.sync_status["sync_enabled"] and 
            self.sync_status["sync_mode"] in ["hybrid", "real_only"] and 
            self.real_ipfs):
            
            try:
                real_cid = self.real_ipfs.upload(data)
                
                # Tallenna synkronointitieto
                self.sync_status["synced_cids"].append({
                    "mock_cid": mock_cid,
                    "real_cid": real_cid,
                    "timestamp": datetime.now().isoformat(),
                    "data_type": type(data).__name__
                })
                self.sync_status["last_sync"] = datetime.now().isoformat()
                self._save_sync_status()
                
                print(f"✅ Synkronoitu mock -> real: {mock_cid} -> {real_cid}")
                
                # Real-only tilassa palautetaan oikea CID
                if self.sync_status["sync_mode"] == "real_only":
                    return real_cid
                
            except Exception as e:
                # Tallennetaan epäonnistunut synkronointi
                self.sync_status["failed_syncs"].append({
                    "mock_cid": mock_cid,
                    "timestamp": datetime.now().isoformat(),
                    "error": str(e)
                })
                self._save_sync_status()
                print(f"❌ Synkronointi epäonnistui: {e}")
        
        return mock_cid
    
    def download(self, cid: str) -> Optional[Dict[str, Any]]:
        """
        Lataa data IPFS:stä nykyisen synkronointitilan mukaisesti
        """
        # Yritä ensin mock-IPFS:ää
        data = self.mock_ipfs.download(cid)
        
        if data is not None:
            return data
        
        # Jos dataa ei löydy mockista ja real-IPFS on käytössä, yritä sieltä
        if (self.sync_status["sync_enabled"] and 
            self.sync_status["sync_mode"] in ["hybrid", "real_only"] and 
            self.real_ipfs):
            
            try:
                data = self.real_ipfs.download(cid)
                if data:
                    # Synkronoi takaisin mock-IPFS:ään
                    self.mock_ipfs.upload(data)
                    print(f"✅ Synkronoitu real -> mock: {cid}")
                    return data
            except Exception as e:
                print(f"❌ Lataus oikeasta IPFS:stä epäonnistui: {e}")
        
        return None
    
    def sync_all_mock_to_real(self) -> Dict[str, Any]:
        """
        Synkronoi kaikki mock-IPFS:n data oikeaan IPFS:ään
        """
        if not self.real_ipfs:
            return {"success": False, "error": "Oikea IPFS ei saatavilla"}
        
        print("🔄 SYNKRONOIDAAN KAIKKI MOCK -> REAL IPFS")
        print("=" * 50)
        
        results = {
            "total_synced": 0,
            "successful": [],
            "failed": [],
            "start_time": datetime.now().isoformat()
        }
        
        # Käy läpi kaikki mock-datat
        for cid, mock_data in self.mock_ipfs.content_store.items():
            try:
                data = mock_data["data"]
                real_cid = self.real_ipfs.upload(data)
                
                results["successful"].append({
                    "mock_cid": cid,
                    "real_cid": real_cid,
                    "data_type": type(data).__name__
                })
                results["total_synced"] += 1
                
                print(f"✅ {cid} -> {real_cid}")
                
            except Exception as e:
                results["failed"].append({
                    "mock_cid": cid,
                    "error": str(e)
                })
                print(f"❌ {cid}: {e}")
        
        results["end_time"] = datetime.now().isoformat()
        results["success"] = True
        
        # Päivitä synkronointitila
        self.sync_status["last_full_sync"] = datetime.now().isoformat()
        self.sync_status["total_synced_items"] = results["total_synced"]
        self._save_sync_status()
        
        print(f"🎉 SYNKRONOINTI VALMIS: {results['total_synced']} kohdetta")
        return results
    
    def sync_specific_from_real(self, real_cid: str) -> bool:
        """
        Synkronoi tietty CID oikeasta IPFS:stä mock-IPFS:ään
        """
        if not self.real_ipfs:
            return False
        
        try:
            data = self.real_ipfs.download(real_cid)
            if data:
                mock_cid = self.mock_ipfs.upload(data)
                print(f"✅ Synkronoitu real -> mock: {real_cid} -> {mock_cid}")
                return True
        except Exception as e:
            print(f"❌ Synkronointi epäonnistui: {e}")
        
        return False
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Hae nykyinen synkronointitila"""
        status = self.sync_status.copy()
        status["mock_stats"] = self.mock_ipfs.get_stats()
        
        if self.real_ipfs:
            status["real_stats"] = self.real_ipfs.get_stats()
        else:
            status["real_stats"] = {"connected": False}
        
        return status
    
    def migrate_to_real_only(self) -> bool:
        """
        Siirrä täysin oikeaan IPFS:ään
        """
        if not self.real_ipfs:
            return False
        
        print("🚀 SIIRRETÄÄN OIKEAAN IPFS:ÄÄN")
        
        # 1. Synkronoi kaikki data
        sync_results = self.sync_all_mock_to_real()
        
        if not sync_results["success"]:
            return False
        
        # 2. Vaihda real-only tilaan
        self.sync_status["sync_mode"] = "real_only"
        self.sync_status["migrated_at"] = datetime.now().isoformat()
        self._save_sync_status()
        
        print("✅ SIIRTO OIKEAAN IPFS:ÄÄN VALMIS")
        return True

# Singleton instance
_sync_engine = None

def get_ipfs_sync_engine(mock_ipfs, real_ipfs_host: str = '/ip4/127.0.0.1/tcp/5001'):
    """Palauttaa IPFSSyncEngine-instanssin"""
    global _sync_engine
    if _sync_engine is None:
        _sync_engine = IPFSSyncEngine(mock_ipfs, real_ipfs_host)
    return _sync_engine
[file content end]
