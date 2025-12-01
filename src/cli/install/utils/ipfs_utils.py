"""
IPFS-toiminnot asennukselle.
"""
from pathlib import Path

# Import riippuvuudet samalla tavalla kuin alkuperäisessä
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from core.ipfs.client import IPFSClient
from core.file_utils import read_json_file


def get_static_marker_cid():
    """
    Hae staattisen merkin CID first_install.json tiedostosta
    
    Returns:
        str: Static marker CID tai fallback CID
    """
    try:
        install_info_path = Path("data/installation/first_install.json")
        if install_info_path.exists():
            install_info = read_json_file(install_info_path)
            return install_info.get("static_marker_cid")
    except Exception as e:
        print(f"⚠️  First install info load failed: {e}")
    
    # Fallback vanhaan CID:ään
    return "QmVaaliKoneStaticMarker123456789"


def check_system_installed():
    """
    Tarkista onko järjestelmä asennettu IPFS:ään
    
    Returns:
        tuple: (is_installed, elections_cid)
    """
    try:
        ipfs_client = IPFSClient()
        
        # Hae oikea CID first_install.json:sta
        static_marker_cid = get_static_marker_cid()
        print(f"🔍 Checking static marker: {static_marker_cid}")
        
        # Yritä ladata staattista merkkitiedostoa
        marker_data = ipfs_client.get_json(static_marker_cid)
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


def load_elections_list(elections_cid):
    """
    Lataa elections lista IPFS:stä
    
    Args:
        elections_cid: Elections listan CID
        
    Returns:
        dict: Elections listan data
    """
    try:
        ipfs_client = IPFSClient()
        elections_data = ipfs_client.get_json(elections_cid)
        
        if elections_data:
            print("✅ Vaalilista ladattu IPFS:stä")
            return elections_data
        else:
            print("❌ Vaalilistan lataus epäonnistui")
            return None
            
    except Exception as e:
        print(f"⚠️  Vaalilistan lataus epäonnistui: {e}")
        return None
