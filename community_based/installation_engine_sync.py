[file name]: installation_engine_sync.py
[file content begin]
"""
Päivitetty asennusmoottori IPFS-synkronointia varten
"""

from installation_engine import InstallationEngine
from ipfs_sync_engine import get_ipfs_sync_engine
from mock_ipfs_sync_ready import MockIPFSSyncReady

class InstallationEngineWithSync(InstallationEngine):
    """Asennusmoottori IPFS-synkronointituelle"""
    
    def __init__(self, runtime_dir: str = "runtime", enable_sync: bool = False):
        super().__init__(runtime_dir)
        
        # Käytä synkronointivalmista mock-IPFS:ää
        self.mock_ipfs = MockIPFSSyncReady()
        
        # Alusta synkronointimoottori
        self.sync_engine = get_ipfs_sync_engine(self.mock_ipfs)
        
        # Ota synkronointi käyttöön jos haluttu
        if enable_sync:
            try:
                self.sync_engine.enable_sync("hybrid")
                print("✅ IPFS-synkronointi käytössä hybrid-tilassa")
            except Exception as e:
                print(f"⚠️  Synkronointi ei saatavilla: {e}")
        
        # Aseta synkronointimoottori IPFS-asiakkaaksi
        self.ipfs_client = self.sync_engine
    
    def set_sync_mode(self, mode: str):
        """Aseta synkronointitila"""
        valid_modes = ["mock_only", "hybrid", "real_only"]
        if mode not in valid_modes:
            raise ValueError(f"Virheellinen tila: {mode}")
        
        self.sync_engine.enable_sync(mode)
        print(f"✅ Synkronointitila asetettu: {mode}")
    
    def get_sync_status(self):
        """Hae synkronointitila"""
        return self.sync_engine.get_sync_status()
    
    def migrate_to_real_ipfs(self):
        """Siirrä oikeaan IPFS:ään"""
        return self.sync_engine.migrate_to_real_only()
    
    def sync_all_data(self):
        """Synkronoi kaikki data mock -> real"""
        return self.sync_engine.sync_all_mock_to_real()
