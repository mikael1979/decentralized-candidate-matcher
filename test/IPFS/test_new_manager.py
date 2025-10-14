from mock_ipfs import MockIPFS
from election_data_manager import ElectionDataManager
from datetime import datetime, timedelta
import requests

def get_next_election_date():
    """
    Hakee seuraavan vaalipäivän Suomen vaalikalenterista tai 
    laskee oletusarvon nykyisestä päivästä
    """
    try:
        # Yritä hakea virallisesta lähteestä (esim. Vaalit.fi API)
        # Tässä esimerkki, voit korvata oikealla API:lla
        response = requests.get("https://api.vaalit.fi/next-election", timeout=5)
        if response.status_code == 200:
            election_data = response.json()
            return election_data["date"]
    except:
        # Fallback: Laske 3 kuukautta tulevaisuuteen
        future_date = datetime.now() + timedelta(days=90)
        return future_date.strftime("%Y-%m-%d")

def create_test_election_meta():
    """Luo testivaalin metadata dynaamisilla arvoilla"""
    
    election_date = get_next_election_date()
    current_year = datetime.now().year
    
    return {
        "system": "Decentralized Candidate Matcher",
        "version": "2.0.0",
        "election": {
            "id": "test_election",
            "country": "FI",
            "type": "municipal",
            "name": {
                "fi": f"Testivaali {current_year}",
                "en": f"Test Election {current_year}"
            },
            "date": election_date,
            "language": "fi"
        },
        "community_moderation": {
            "enabled": True,
            "thresholds": {
                "auto_block_inappropriate": 0.7,
                "auto_block_min_votes": 10,
                "community_approval": 0.8
            }
        },
        "created": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat()
    }

def test_new_manager():
    """Testaa uutta ElectionDataManageria"""
    print("🧪 TESTATAAN UUTTA ELECTION DATA MANAGERIA")
    
    # Alusta
    ipfs = MockIPFS()
    manager = ElectionDataManager(ipfs)
    
    # 1. Alusta vaali - dynaamisella päivämäärällä
    meta_data = create_test_election_meta()
    
    print(f"📅 Vaalipäivä: {meta_data['election']['date']}")
    print(f"🏛️ Vaalin nimi: {meta_data['election']['name']['fi']}")
    
    root_cid = manager.initialize_election(meta_data)
    
    # 2. Lisää dataa
    question = {
        "id": 1,
        "category": {"fi": "Testi", "en": "Test"},
        "question": {
            "fi": "Tämä on testikysymys?",
            "en": "This is a test question?"
        },
        "scale": {"min": -5, "max": 5}
    }
    manager.add_question(question)
    
    candidate = {
        "id": 1,
        "name": "Testi Ehdokas",
        "party": "Testi Puolue",
        "district": "Testi"
    }
    manager.add_candidate(candidate)
    
    # 3. Tarkista status
    status = manager.get_election_status()
    print(f"\n📊 VAALIN TILA:")
    print(f"Status: {status['status']}")
    print(f"Election ID: {status['election_id']}")
    print(f"Root CID: {status['root_cid']}")
    
    for file_name, file_info in status['files'].items():
        print(f"📁 {file_name}:")
        for key, value in file_info.items():
            print(f"   {key}: {value}")
    
    # 4. Tarkista eheys
    print(f"\n🔒 EHETYSTARKISTUS:")
    for file_name in manager.list_all_files().keys():
        data = manager.get_election_data(file_name)
        is_valid = manager.verify_integrity(data)
        print(f"  {file_name}: {'✅ VALID' if is_valid else '❌ INVALID'}")
    
    print(f"\n🎉 UUSI MANAGER TESTATTU ONNISTUNEESTI!")

if __name__ == "__main__":
    test_new_manager()
