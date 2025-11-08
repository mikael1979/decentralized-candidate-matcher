#!/usr/bin/env python3
# force_sync_to_mock.py
"""
Pakota kysymysten synkronointi mock-IPFS:ään
"""

import json
from pathlib import Path
from datetime import datetime

def force_sync_to_mock():
    """Pakota kysymysten synkronointi mock-IPFS:ään"""
    
    print("🚀 PAKOTETAAN KYSYMYSTEN SYNKRONOINTI MOCK-IPFS:ÄÄN...")
    
    # 1. Lataa kysymykset
    questions_file = Path("runtime/questions.json")
    if not questions_file.exists():
        print("❌ runtime/questions.json ei löydy")
        return False
    
    try:
        with open(questions_file, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
        
        questions = questions_data.get("questions", [])
        print(f"✅ Kysymykset ladattu: {len(questions)} kpl")
        
    except Exception as e:
        print(f"❌ Virhe ladattaessa kysymyksiä: {e}")
        return False
    
    # 2. Alusta mock-IPFS
    try:
        from mock_ipfs import MockIPFS
        ipfs = MockIPFS()
        print("✅ Mock-IPFS alustettu")
    except ImportError:
        print("❌ Mock-IPFS ei saatavilla")
        return False
    
    # 3. Luo IPFS-data
    ipfs_data = {
        "metadata": {
            "version": "2.0.0",
            "created": datetime.now().isoformat(),
            "election_id": "Jumaltenvaalit_2026",
            "source": "master_force_sync",
            "total_questions": len(questions)
        },
        "questions": questions,
        "sync_timestamp": datetime.now().isoformat()
    }
    
    # 4. Lähetä mock-IPFS:ään
    try:
        cid = ipfs.upload(ipfs_data)
        print(f"✅ Kysymykset lähetetty mock-IPFS:ään")
        print(f"📦 CID: {cid}")
        
        # 5. Tallenna myös questions.json:ään IPFS-CID
        for question in questions:
            question["ipfs_cid"] = cid
        
        with open(questions_file, 'w', encoding='utf-8') as f:
            json.dump(questions_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ IPFS-CID:t päivitetty kysymyksiin")
        
    except Exception as e:
        print(f"❌ Virhe lähettäessä mock-IPFS:ään: {e}")
        return False
    
    # 6. Tarkista että data on mock-IPFS:ässä
    try:
        downloaded_data = ipfs.download(cid)
        if downloaded_data:
            print(f"✅ Data varmistettu mock-IPFS:stä")
            print(f"📥 Ladattu: {len(downloaded_data.get('questions', []))} kysymystä")
        else:
            print("❌ Dataa ei löydy mock-IPFS:stä")
    except Exception as e:
        print(f"⚠️  Virhe varmistettaessa dataa: {e}")
    
    print(f"\n🎯 KYSYMYKSET SYNKRONOITU MOCK-IPFS:ÄÄN!")
    print(f"📊 {len(questions)} kysymystä saatavilla mock-IPFS:stä")
    
    return True

def main():
    """Pääohjelma"""
    print("🔄 PAKOTETTU SYNKRONOINTI MOCK-IPFS:ÄÄN")
    print("=" * 60)
    
    response = input("Haluatko pakottaa kysymysten synkronoinnin mock-IPFS:ään? (K/e): ").strip().lower()
    
    if response in ['', 'k', 'kyllä', 'y', 'yes']:
        success = force_sync_to_mock()
        if success:
            print(f"\n💡 SEURAAVAT VAIHEET:")
            print("1. Tarkista mock-IPFS: python check_mock_ipfs_content.py")
            print("2. Kopioi mock_ipfs_data.json -> mock_ipfs_data.master.json")
            print("3. Siirrä työasemalle ja suorita: python sync_questions_from_master.py")
        return success
    else:
        print("\n🔧 Synkronointi peruttu")
        return True

if __name__ == "__main__":
    main()
