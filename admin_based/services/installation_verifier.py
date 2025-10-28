import os
import json

def verify_files() -> bool:
    """Tarkista että kaikki tarvittavat tiedostot ovat paikallaan"""
    required_dirs = ['data', 'config', 'keys']
    required_files = [
        'keys/private_key.pem',
        'keys/public_key.pem',
        'keys/system_info.json',
        'config/questions.json',
        'config/candidates.json',
        'config/meta.json',
        'config/admins.json',
        'data/meta.json',
        'data/system_chain.json'
    ]
    
    all_ok = True
    for d in required_dirs:
        if not os.path.exists(d):
            print(f"❌ Hakemistoa puuttuu: {d}")
            all_ok = False
    
    for f in required_files:
        if not os.path.exists(f):
            print(f"❌ Tiedostoa puuttuu: {f}")
            all_ok = False
    
    status = "✅" if all_ok else "❌"
    print(f"{status} Tiedostotarkistus: {'PASS' if all_ok else 'FAIL'}")
    return all_ok

def verify_configuration() -> bool:
    """Tarkista konfiguraation sisäinen yhteensopivuus"""
    try:
        with open('config/meta.json', 'r', encoding='utf-8') as f:
            meta = json.load(f)
        
        with open('keys/system_info.json', 'r', encoding='utf-8') as f:
            system_info = json.load(f)
        
        # Tarkista että system_id:t täsmäävät
        meta_system_id = meta.get('system_info', {}).get('system_id')
        key_system_id = system_info.get('system_id')
        
        if meta_system_id != key_system_id:
            print("❌ System ID ei täsmää config/meta.json ja keys/system_info.json välillä")
            return False
        
        # Tarkista vaali-ID:t
        meta_election_id = meta.get('election', {}).get('id')
        key_election_id = system_info.get('election_id')
        
        if meta_election_id != key_election_id:
            print("❌ Election ID ei täsmää config/meta.json ja keys/system_info.json välillä")
            return False
        
        print("✅ Konfiguraation sisäinen yhteensopivuus: PASS")
        return True
        
    except Exception as e:
        print(f"❌ Konfiguraation tarkistus epäonnistui: {e}")
        return False

def verify_installation() -> bool:
    print("\n🔍 ASENNUKSEN TARKISTUS")
    print("-" * 30)
    
    # Tarkista tiedostot
    files_ok = verify_files()
    
    # Tarkista konfiguraatio
    config_ok = verify_configuration()
    
    # Yhteenveto
    overall_ok = files_ok and config_ok
    status = "✅" if overall_ok else "❌"
    print(f"\n{status} Asennuksen tarkistus: {'PASS' if overall_ok else 'FAIL'}")
    
    return overall_ok
