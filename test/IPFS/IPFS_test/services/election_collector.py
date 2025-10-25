import re
from services.console_ui import input_election_date

def collect_election_info() -> dict:
    print("\n🗳️  VAALIN PERUSTIEDOT")
    print("-" * 30)
    
    while True:
        election_id = input("Vaalin tunniste (esim. kunnallisvaalit-2025): ").strip()
        if election_id and re.match(r'^[a-z0-9-]+$', election_id):
            break
        print("❌ Tunniste voi sisältää vain pieniä kirjaimia, numeroita ja väliviivoja")
    
    while True:
        name_fi = input("Vaalin nimi (suomeksi): ").strip()
        if name_fi:
            break
        print("❌ Nimi on pakollinen")
    
    name_en = input("Vaalin nimi (englanniksi): ").strip() or name_fi
    name_sv = input("Vaalin nimi (ruotsiksi): ").strip() or name_fi
    
    election_date = input_election_date()
    
    return {
        "id": election_id,
        "name": {
            "fi": name_fi,
            "en": name_en,
            "sv": name_sv
        },
        "date": election_date,
        "type": "municipal",  # Oletustyyppi
        "description": {
            "fi": f"{name_fi} - Kunnallisvaalit",
            "en": f"{name_en} - Municipal elections", 
            "sv": f"{name_sv} - Kommunala val"
        }
    }
