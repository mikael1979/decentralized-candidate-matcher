"""
Vaalitietojen käsittely.
"""

def show_elections_hierarchy(elections_data):
    """
    Näytä vaalihierarkia käyttäjälle
    
    Args:
        elections_data: Elections listan data
    """
    print("\n🌍 KÄYTÖSSÄ OLEVAT VAALIT:")
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
        
        for category, election_data in other_elections.items():
            if isinstance(election_data, dict) and "election_id" in election_data:
                election_name = election_data["name"]["fi"]
                status = election_data["status"]
                status_icon = "🟢" if status == "active" else "🟡" if status == "upcoming" else "🔴"
                print(f"  {status_icon} {election_name} ({election_data['election_id']})")


def validate_election_id(election_id, elections_data):
    """
    Tarkista että election_id on olemassa vaalilistassa
    """
    hierarchy = elections_data.get("hierarchy", {})
    
    # Tarkista mantereiden vaalit
    for continent_data in hierarchy.get("continents", {}).values():
        for country_data in continent_data.get("countries", {}).values():
            for e_id, election_data in country_data.get("elections", {}).items():
                if election_data["election_id"] == election_id:
                    return True
    
    # Tarkista muut vaalit
    for category, election_data in hierarchy.get("other_elections", {}).items():
        if isinstance(election_data, dict) and election_data.get("election_id") == election_id:
            return True
    
    return False
