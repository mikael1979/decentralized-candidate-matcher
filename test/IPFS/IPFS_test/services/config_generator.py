import os
import json
import hashlib
from datetime import datetime
from cryptography.hazmat.primitives import serialization

def create_all_configs(election_data, admin_data, system_id, public_pem, install_data, private_key):
    os.makedirs('config', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # Luo meta.json konfiguraatioon
    config_meta = {
        "election": election_data,
        "system_info": {
            "system_id": system_id,
            "public_key": public_pem,
            "created": datetime.now().isoformat()
        },
        "admin": admin_data,
        "version": install_data["version"]
    }
    
    with open('config/meta.json', 'w', encoding='utf-8') as f:
        json.dump(config_meta, f, indent=2, ensure_ascii=False)
    
    # Luo meta.json data-kansioon (kopio)
    with open('data/meta.json', 'w', encoding='utf-8') as f:
        json.dump(config_meta, f, indent=2, ensure_ascii=False)
    
    # Luo kysymykset
    questions = install_data["default_questions"]
    with open('config/questions.json', 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    
    # Luo ehdokkaat
    candidates = install_data["default_candidates"]
    with open('config/candidates.json', 'w', encoding='utf-8') as f:
        json.dump(candidates, f, indent=2, ensure_ascii=False)
    
    # Luo adminit
    admins = [admin_data]
    with open('config/admins.json', 'w', encoding='utf-8') as f:
        json.dump(admins, f, indent=2, ensure_ascii=False)
    
    print("✅ Konfiguraatiotiedostot luotu")
