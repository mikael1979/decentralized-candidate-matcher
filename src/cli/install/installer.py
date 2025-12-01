"""
Pääasennuslogiikka - perustuu alkuperäiseen implementaatioon
"""
import sys
import json
from pathlib import Path
from datetime import datetime

# Lisää polku
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    # Yritä ensin suhteellisia importteja
    from core.config import ConfigManager
    from core.file_utils import ensure_directory
    from .utils import (
        check_system_installed,
        load_elections_list,
        show_elections_hierarchy,
        validate_election_id,
        initialize_node,
        initialize_basic_data_files
    )
    HAS_UTILS = True
except ImportError as e:
    print(f"⚠️  Relative import error: {e}")
    # Yritä absoluuttisia
    try:
        from core.config import ConfigManager
        from core.file_utils import ensure_directory
        from src.cli.install.utils import (
            check_system_installed,
            load_elections_list,
            show_elections_hierarchy,
            validate_election_id,
            initialize_node,
            initialize_basic_data_files
        )
        HAS_UTILS = True
    except ImportError as e2:
        print(f"❌ Utils import failed: {e2}")
        HAS_UTILS = False


class SystemInstaller:
    """Järjestelmän asennuslogiikka"""
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.elections_data = None
        self.node_identity = None
    
    def run(self, election_id=None, node_type='worker', 
           node_name=None, enable_multinode=False, list_elections=False):
        """Suorita asennus"""
        
        if not HAS_UTILS:
            return False, "❌ Utils-moduulit puuttuvat"
        
        # Tarkista onko järjestelmä asennettu
        is_installed, elections_cid = check_system_installed()
        if not is_installed:
            return False, "❌ Hajautettua vaalikonetta ei löydy IPFS:stä\n💡 Suorita ensin: python src/cli/first_install.py"
        
        if not elections_cid:
            return False, "❌ Vaalilistaa ei löydy"
        
        # Lataa elections lista
        self.elections_data = load_elections_list(elections_cid)
        if not self.elections_data:
            return False, "❌ Vaalilistan lataus epäonnistui"
        
        # Näytä vaalit jos pyydetty
        if list_elections:
            show_elections_hierarchy(self.elections_data)
            return True, "Vaalilista näytetty"
        
        # Jos vaalia ei ole annettu, näytä lista
        if not election_id:
            show_elections_hierarchy(self.elections_data)
            import click
            election_id = click.prompt('\n📝 Valitse vaali (election_id)', type=str)
        
        # Validoi election_id
        if not validate_election_id(election_id, self.elections_data):
            return False, f"❌ Vaalia '{election_id}' ei löydy"
        
        # Tarkista onko config jo olemassa
        current_config = None
        try:
            config_path = Path("config.json")
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    current_config = json.load(f)
        except Exception as e:
            print(f"⚠️  Config load warning: {e}")
            current_config = None
        
        if current_config and current_config.get("metadata", {}).get("election_id") != election_id:
            import click
            click.confirm(
                f"Haluatko vaihtaa vaalia '{current_config.get('metadata', {}).get('election_id')}' -> '{election_id}'?",
                abort=True
            )
        
        # Generoi config manuaalisesti
        print(f"📋 Alustetaan config vaalille: {election_id}")
        config = self._generate_config(election_id, node_type)
        
        # Tallenna config
        config_path = Path("config.json")
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Config save failed: {e}")
            config_path = "config.json"
        
        print(f"✅ Config tallennettu: {config_path}")
        
        # Alusta node jos multinode käytössä
        if enable_multinode:
            self.node_identity = initialize_node(election_id, node_type, node_name)
        
        # Luo data-hakemistot
        data_path = Path(f"data/runtime/{election_id}")
        ensure_directory(data_path)
        print(f"✅ Data-hakemistot luotu: {data_path}")
        
        # Alusta perus data-tiedostot
        initialize_basic_data_files(election_id)
        
        return True, {
            "election_id": election_id,
            "node_type": node_type,
            "node_identity": self.node_identity,
            "config_path": str(config_path),
            "data_path": str(data_path)
        }
    
    def _generate_config(self, election_id, node_type):
        """Generoi config manuaalisesti"""
        return {
            "metadata": {
                "election_id": election_id,
                "node_type": node_type,
                "version": "2.0.0",
                "created_at": datetime.now().isoformat()
            },
            "paths": {
                "data_root": f"data/runtime/{election_id}",
                "cache_dir": "data/cache",
                "logs_dir": "data/logs"
            },
            "ipfs": {
                "gateway": "http://localhost:8080",
                "api_port": 5001
            },
            "network": {
                "multinode_enabled": False,
                "node_discovery": True
            }
        }
