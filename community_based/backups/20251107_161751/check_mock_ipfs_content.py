#!/usr/bin/env python3
# check_mock_ipfs_content.py
"""
Tarkista mitä dataa master-koneella on mock-IPFS:ässä
"""

import json
from pathlib import Path

def check_mock_ipfs_content():
    """Tarkista mock-IPFS sisältö"""
    
    print("🔍 TARKISTETAAN MOCK-IPFS SISÄLTÖÄ...")
    
    mock_file = Path("mock_ipfs_data.json")
    if not mock_file.exists():
        print("❌ mock_ipfs_data.json ei löydy")
        print("💡 Mock-IPFS ei ole vielä synkronoitu")
        return False
    
    try:
        with open(mock_file, 'r', encoding='utf-8') as f:
            mock_data = json.load(f)
        
        print(f"✅ Mock-IPFS data: {len(mock_data)} CID:ä")
        
        # Etsi kysymysdataa
        questions_found = 0
        system_data_found = 0
        
        for cid, data in mock_data.items():
            content = data.get('data', {})
            
            if 'questions' in content:
                questions_count = len(content.get('questions', []))
                print(f"📥 Kysymysdata CID: {cid}")
                print(f"   - {questions_count} kysymystä")
                print(f"   - Lähde: {content.get('source', 'unknown')}")
                questions_found += 1
                
            elif 'system_locked' in content:
                print(f"🔒 System lock CID: {cid}")
                print(f"   - Lukittu: {content.get('locked_at', 'unknown')}")
                system_data_found += 1
                
            elif 'metadata' in content:
                metadata = content.get('metadata', {})
                if 'election_id' in metadata:
                    print(f"📋 Metadata CID: {cid}")
                    print(f"   - Vaali: {metadata.get('election_id')}")
                    system_data_found += 1
        
        if questions_found == 0:
            print("❌ Ei kysymysdataa mock-IPFS:ässä")
            print("💡 Synkronoi kysymykset: python manage_questions.py sync")
        else:
            print(f"✅ Löytyi {questions_found} kysymysdatasetia")
            
        print(f"📊 Yhteensä: {questions_found + system_data_found} data-objektia")
            
    except Exception as e:
        print(f"❌ Virhe ladattaessa mock-dataa: {e}")

if __name__ == "__main__":
    check_mock_ipfs_content()
