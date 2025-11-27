#!/usr/bin/env python3
"""
Ensimmäinen asennus - luo IPFS:ään perusrakenteet ja kiinteän merkin
"""
import click
import json
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import ConfigManager
from core.ipfs.client import IPFSClient
from core.file_utils import ensure_directory, read_json_file, write_json_file


# KIINTEÄ CID MERKKITIEDOSTOLLE - tämä on sama kaikissa asennuksissa
STATIC_MARKER_CID = "QmVaaliKoneStaticMarker123456789"  # Tämä on esimerkki, oikea tulee IPFS:stä

def create_static_marker():
    """
    Luo staattinen merkkitiedosto IPFS:ään joka osoittaa että vaalikone on asennettu
    
    Returns:
        str: Merkkitiedoston CID
    """
    try:
        ipfs_client = IPFSClient()
        
        marker_data = {
            "system": "decentralized-candidate-matcher",
            "version": "2.0.0",
            "deployed_at": datetime.now().isoformat(),
            "marker_type": "static_system_marker",
            "description": {
                "fi": "Hajautetun vaalikoneen staattinen merkkitiedosto",
                "en": "Static marker file for decentralized candidate matcher",
                "sv": "Statisk markörfil för decentraliserad kandidatmatchare"
            },
            "schema_version": "1.0.0",
            "content_hash": "8f7d88ebc19a5e7a5b2c8f4d7e6a1b9c3f8a2e4d5c6b9a8e7f6d5c4b3a2e1f0"
        }
        
        cid = ipfs_client.add_json(marker_data)
        print(f"📍 Staattinen merkkitiedosto luotu IPFS:ään: {cid}")
        return cid
        
    except Exception as e:
        print(f"⚠️  Merkkitiedoston luonti epäonnistui: {e}")
        return None

def load_elections_template():
    """
    Lataa elections hierarchy template tiedostosta
    
    Returns:
        dict: Template data
    """
    try:
        template_path = Path("base_templates/elections/elections_hierarchy.base.json")
        if not template_path.exists():
            print(f"❌ Template tiedostoa ei löydy: {template_path}")
            return None
            
        template_data = read_json_file(template_path)
        return template_data
        
    except Exception as e:
        print(f"❌ Template:n lataus epäonnistui: {e}")
        return None

def create_elections_list_from_template(static_marker_cid):
    """
    Luo elections listan templatesta
    
    Args:
        static_marker_cid: Staattisen merkin CID
        
    Returns:
        dict: Elections list data
    """
    template_data = load_elections_template()
    if not template_data:
        return None
    
    # Korvaa placeholderit
    timestamp = datetime.now().isoformat()
    
    # Yksinkertainen placeholder-korvaus
    import json
    elections_json = json.dumps(template_data)
    elections_json = elections_json.replace("{{TIMESTAMP}}", timestamp)
    elections_json = elections_json.replace("{{STATIC_MARKER_CID}}", static_marker_cid)
    
    elections_data = json.loads(elections_json)
    
    # Päivitä metadata
    elections_data["metadata"]["created"] = timestamp
    elections_data["metadata"]["last_updated"] = timestamp
    elections_data["metadata"]["static_marker_cid"] = static_marker_cid
    
    return elections_data

def publish_elections_list(static_marker_cid):
    """
    Julkaise elections lista IPFS:ään
    
    Args:
        static_marker_cid: Staattisen merkin CID
        
    Returns:
        str: Elections list CID
    """
    try:
        ipfs_client = IPFSClient()
        
        elections_data = create_elections_list_from_template(static_marker_cid)
        if not elections_data:
            print("❌ Elections listan luonti epäonnistui")
            return None
            
        cid = ipfs_client.add_json(elections_data)
        
        print(f"📋 Elections lista julkaistu IPFS:ään: {cid}")
        return cid
        
    except Exception as e:
        print(f"⚠️  Elections listan julkaisu epäonnistui: {e}")
        return None

def check_existing_installation():
    """
    Tarkista onko järjestelmä jo asennettu IPFS:ään
    
    Returns:
        bool: True jos asennus on olemassa
    """
    try:
        ipfs_client = IPFSClient()
        
        # Yritä ladata staattista merkkitiedostoa
        marker_data = ipfs_client.get_json(STATIC_MARKER_CID)
        if marker_data and marker_data.get("system") == "decentralized-candidate-matcher":
            print("✅ Hajautettu vaalikone on jo asennettu IPFS:ään")
            return True
            
    except Exception as e:
        # Jos merkkitiedostoa ei löydy, asennusta ei ole
        pass
        
    return False

@click.command()
@click.option('--force', is_flag=True, help='Pakota uudelleenasennus')
def first_install(force):
    """
    Suorita ensimmäinen asennus - luo IPFS-rakenteet
    
    Tämä suoritetaan vain kerran koko järjestelmän historiassa
    """
    
    print("🚀 HAJautetun Vaalikoneen Ensimmäinen Asennus")
    print("=" * 50)
    
    # Tarkista onko jo asennettu
    if not force and check_existing_installation():
        print("💡 Käytä --force pakottaaksesi uudelleenasennuksen")
        return
    
    try:
        # 1. Luo staattinen merkkitiedosto
        print("\n📍 Luodaan staattinen merkkitiedosto...")
        marker_cid = create_static_marker()
        if not marker_cid:
            print("❌ Merkkitiedoston luonti epäonnistui")
            return
        
        # 2. Luo elections lista templatesta
        print("\n📋 Luodaan vaalilista templatesta...")
        elections_cid = publish_elections_list(marker_cid)
        if not elections_cid:
            print("❌ Vaalilistan luonti epäonnistui")
            return
        
        # 3. Tallenna tiedot paikallisesti
        install_info = {
            "first_install_completed": True,
            "completed_at": datetime.now().isoformat(),
            "static_marker_cid": marker_cid,
            "elections_list_cid": elections_cid,
            "version": "2.0.0"
        }
        
        info_path = Path("data/installation/first_install.json")
        ensure_directory(info_path.parent)
        write_json_file(info_path, install_info)
        
        print(f"\n🎉 ENSIMMÄINEN ASENNUS VALMIS!")
        print(f"📍 Staattinen merkki: {marker_cid}")
        print(f"📋 Vaalilista: {elections_cid}")
        print(f"💾 Paikallinen info: {info_path}")
        print("\n💡 Nyt voit ajaa normaalin install.py muille koneille")
        
    except Exception as e:
        print(f"❌ Ensimmäinen asennus epäonnistui: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    first_install()
