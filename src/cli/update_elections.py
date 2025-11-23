#!/usr/bin/env python3
"""
Päivitä vaalilista IPFS:ään uusilla vaaleilla
"""
import click
import json
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.ipfs.client import IPFSClient
from core.file_utils import ensure_directory, read_json_file, write_json_file

def load_current_elections_list():
    """
    Lataa nykyinen elections lista IPFS:stä
    
    Returns:
        tuple: (elections_data, elections_cid)
    """
    try:
        # Lataa first_install.json:sta elections CID
        install_info_path = Path("data/installation/first_install.json")
        if not install_info_path.exists():
            print("❌ First install infoa ei löydy")
            return None, None
            
        install_info = read_json_file(install_info_path)
        elections_cid = install_info.get("elections_list_cid")
        
        if not elections_cid:
            print("❌ Elections CID:ä ei löydy")
            return None, None
            
        ipfs_client = IPFSClient()
        elections_data = ipfs_client.get_json(elections_cid)
        
        if elections_data:
            print(f"✅ Elections lista ladattu: {elections_cid}")
            return elections_data, elections_cid
        else:
            print("❌ Elections listan lataus epäonnistui")
            return None, elections_cid
            
    except Exception as e:
        print(f"❌ Elections listan lataus epäonnistui: {e}")
        return None, None

def add_election_to_list(elections_data, election_id, name_fi, name_en, name_sv, 
                        election_type, status, level, description_fi="", description_en="", description_sv=""):
    """
    Lisää uusi vaali elections listaan
    
    Args:
        elections_data: Nykyinen elections data
        election_id: Vaalin uniikki ID
        name_*: Nimi eri kielillä
        election_type: Vaalin tyyppi
        status: Vaalin tila
        level: Vaalin taso
        description_*: Kuvaus eri kielillä
    """
    
    # Tarkista että vaalia ei ole jo olemassa
    if election_exists(elections_data, election_id):
        print(f"⚠️  Vaali '{election_id}' on jo olemassa")
        return False
    
    new_election = {
        "election_id": election_id,
        "name": {
            "fi": name_fi,
            "en": name_en,
            "sv": name_sv
        },
        "type": election_type,
        "status": status,
        "level": level,
        "description": {
            "fi": description_fi,
            "en": description_en,
            "sv": description_sv
        },
        "added_at": datetime.now().isoformat(),
        "added_by": "update_elections_cli"
    }
    
    # Lisää "other_elections" osioon
    if "other_elections" not in elections_data["hierarchy"]:
        elections_data["hierarchy"]["other_elections"] = {}
    
    # Käytä election_id:ta avaimena
    elections_data["hierarchy"]["other_elections"][election_id] = new_election
    
    # Päivitä metadata
    elections_data["metadata"]["last_updated"] = datetime.now().isoformat()
    elections_data["metadata"]["version"] = "2.1.0"  # Päivitä versio
    
    print(f"✅ Vaali '{election_id}' lisätty listaan")
    return True

def election_exists(elections_data, election_id):
    """
    Tarkista onko vaali jo olemassa
    """
    hierarchy = elections_data.get("hierarchy", {})
    
    # Tarkista mantereet
    for continent_data in hierarchy.get("continents", {}).values():
        for country_data in continent_data.get("countries", {}).values():
            for existing_election in country_data.get("elections", {}).values():
                if existing_election.get("election_id") == election_id:
                    return True
    
    # Tarkista muut vaalit
    for existing_election in hierarchy.get("other_elections", {}).values():
        if isinstance(existing_election, dict) and existing_election.get("election_id") == election_id:
            return True
    
    return False

def publish_updated_elections_list(elections_data):
    """
    Julkaise päivitetty elections lista IPFS:ään
    
    Returns:
        str: Uusi CID
    """
    try:
        ipfs_client = IPFSClient()
        new_cid = ipfs_client.add_json(elections_data)
        
        if new_cid:
            print(f"📋 Päivitetty elections lista julkaistu: {new_cid}")
            
            # Päivitä first_install.json uudella CID:llä
            update_first_install_info(new_cid)
            
            return new_cid
        else:
            print("❌ Elections listan julkaisu epäonnistui")
            return None
            
    except Exception as e:
        print(f"❌ Elections listan julkaisu epäonnistui: {e}")
        return None

def update_first_install_info(new_elections_cid):
    """
    Päivitä first_install.json uudella elections CID:llä
    """
    try:
        install_info_path = Path("data/installation/first_install.json")
        if install_info_path.exists():
            install_info = read_json_file(install_info_path)
            install_info["elections_list_cid"] = new_elections_cid
            install_info["last_updated"] = datetime.now().isoformat()
            
            write_json_file(install_info_path, install_info)
            print(f"✅ First install info päivitetty: {install_info_path}")
            
    except Exception as e:
        print(f"⚠️  First install info päivitys epäonnistui: {e}")

@click.command()
@click.option('--election-id', required=True, help='Vaalin tunniste')
@click.option('--name-fi', required=True, help='Vaalin nimi suomeksi')
@click.option('--name-en', required=True, help='Vaalin nimi englanniksi')
@click.option('--name-sv', required=True, help='Vaalin nimi ruotsiksi')
@click.option('--type', required=True, help='Vaalin tyyppi (national, international, fantasy, etc.)')
@click.option('--status', default='upcoming', help='Vaalin tila (upcoming, active, completed)')
@click.option('--level', required=True, help='Vaalin taso (national, international, local, fantasy)')
@click.option('--description-fi', default='', help='Kuvaus suomeksi')
@click.option('--description-en', default='', help='Kuvaus englanniksi')
@click.option('--description-sv', default='', help='Kuvaus ruotsiksi')
@click.option('--list-current', is_flag=True, help='Näytä nykyinen vaalilista')
def update_elections(election_id, name_fi, name_en, name_sv, type, status, level, 
                    description_fi, description_en, description_sv, list_current):
    """
    Lisää uusi vaali IPFS-vaalilistaan ja julkaise päivitetty lista
    
    Esimerkkejä:
        # Lisää uusi vaali:
        python update_elections.py --election-id "testivaali_2024" \
          --name-fi "Testivaali 2024" --name-en "Test Election 2024" --name-sv "Testval 2024" \
          --type national --status upcoming --level national
        
        # Näytä nykyinen lista:
        python update_elections.py --list-current
    """
    
    if list_current:
        # Näytä nykyinen lista
        elections_data, elections_cid = load_current_elections_list()
        if elections_data:
            show_elections_list(elections_data)
        return
    
    # Lataa nykyinen lista
    elections_data, elections_cid = load_current_elections_list()
    if not elections_data:
        print("❌ Nykyisen listan lataus epäonnistui")
        return
    
    # Lisää uusi vaali
    success = add_election_to_list(
        elections_data, election_id, name_fi, name_en, name_sv,
        type, status, level, description_fi, description_en, description_sv
    )
    
    if not success:
        return
    
    # Julkaise päivitetty lista
    new_cid = publish_updated_elections_list(elections_data)
    
    if new_cid:
        print(f"\n🎉 VAALI LISÄTTY ONNISTUNEESTI!")
        print(f"📋 Uusi elections lista: {new_cid}")
        print(f"🎯 Vaali: {election_id}")
        print(f"📊 Tila: {status}")
        print(f"💡 Muut nodet näkevät vaalin seuraavalla --list-elections komennolla")
    else:
        print("❌ Vaalin lisäys epäonnistui")

def show_elections_list(elections_data):
    """
    Näytä vaalilista
    """
    print("\n🌍 NYKYINEN VAALILISTA:")
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
                election_name = election_data["name"]["fi"]
                status = election_data["status"]
                status_icon = "🟢" if status == "active" else "🟡" if status == "upcoming" else "🔴"
                print(f"    {status_icon} {election_name} ({election_data['election_id']})")
    
    # Näytä muut vaalit
    other_elections = hierarchy.get("other_elections", {})
    if other_elections:
        print(f"\n🎭 MUUT VAALIT:")
        print("-" * 30)
        
        for election_id, election_data in other_elections.items():
            if isinstance(election_data, dict) and "election_id" in election_data:
                election_name = election_data["name"]["fi"]
                status = election_data["status"]
                status_icon = "🟢" if status == "active" else "🟡" if status == "upcoming" else "🔴"
                print(f"  {status_icon} {election_name} ({election_data['election_id']})")

if __name__ == "__main__":
    update_elections()
