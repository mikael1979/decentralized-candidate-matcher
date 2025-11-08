# Korjaa metadata - create_fix_metadata.py
#!/usr/bin/env python3
"""
Korjaa metadata Jumaltenvaaleihin
"""

import json
from pathlib import Path

def fix_metadata():
    print("🔧 KORJATAAN METADATAA...")
    
    # Päivitä runtime/meta.json
    meta_file = Path("runtime/meta.json")
    if meta_file.exists():
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta_data = json.load(f)
        
        # Aseta Jumaltenvaalit aktiiviseksi
        if 'election' in meta_data:
            meta_data['election']['id'] = 'Jumaltenvaalit_2026'
            meta_data['election']['name'] = {
                'fi': 'Kreikkalaisten Jumalien Vaalit 2026',
                'en': 'Greek Gods Election 2026', 
                'sv': 'Grekiska Gudarnas Val 2026'
            }
            meta_data['election']['date'] = '2026-01-15'
            meta_data['election']['type'] = 'divine_council'
        
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(meta_data, f, indent=2, ensure_ascii=False)
        
        print("✅ Metadata päivitetty Jumaltenvaaleihin")
    
    # Päivitä system_metadata.json
    system_meta_file = Path("runtime/system_metadata.json")
    if system_meta_file.exists():
        with open(system_meta_file, 'r', encoding='utf-8') as f:
            system_meta = json.load(f)
        
        if 'election_specific' in system_meta:
            system_meta['election_specific']['election_id'] = 'Jumaltenvaalit_2026'
        
        with open(system_meta_file, 'w', encoding='utf-8') as f:
            json.dump(system_meta, f, indent=2, ensure_ascii=False)
        
        print("✅ System metadata päivitetty")
    
    print("🎯 Kaikki metadata korjattu!")

if __name__ == "__main__":
    fix_metadata()
