# src/cli/install/utils/election_utils.py
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
                print(format_election_display(election_data))
    
    # Näytä muut vaalit
    other_elections = hierarchy.get("other_elections", {})
    if other_elections:
        print(f"\n🎭 MUUT VAALIT:")
        print("-" * 30)
        
        for category, election_data in other_elections.items():
            if isinstance(election_data, dict) and "election_id" in election_data:
                # Poista indentti "muiden" vaalien kohdalla
                formatted = format_election_display(election_data)
                print(f"  {formatted.lstrip()}")


def validate_election_id(election_id, elections_data):
    """
    Tarkista että election_id on olemassa vaalilistassa
    """
    if not elections_data or not election_id:
        return False
        
    hierarchy = elections_data.get("hierarchy", {})
    
    # Tarkista mantereiden vaalit
    for continent_data in hierarchy.get("continents", {}).values():
        for country_data in continent_data.get("countries", {}).values():
            for e_id, election_data in country_data.get("elections", {}).items():
                if election_data.get("election_id") == election_id:
                    return True
    
    # Tarkista muut vaalit
    for category, election_data in hierarchy.get("other_elections", {}).items():
        if isinstance(election_data, dict) and election_data.get("election_id") == election_id:
            return True
    
    return False


def get_election_info(election_id, elections_data):
    """
    Hae vaalin tiedot
    
    Args:
        election_id: Haettava vaalin tunniste
        elections_data: Elections listan data
        
    Returns:
        dict: Vaalin tiedot tai None jos ei löydy
    """
    if not elections_data or not election_id:
        return None
        
    hierarchy = elections_data.get("hierarchy", {})
    
    # Etsi mantereiden vaaleista
    for continent_data in hierarchy.get("continents", {}).values():
        for country_data in continent_data.get("countries", {}).values():
            for e_id, election_data in country_data.get("elections", {}).items():
                if election_data.get("election_id") == election_id:
                    return election_data
    
    # Etsi muista vaaleista
    other_elections = hierarchy.get("other_elections", {})
    if isinstance(other_elections, dict):
        for category, election_data in other_elections.items():
            if isinstance(election_data, dict) and election_data.get("election_id") == election_id:
                return election_data
    
    return None


def format_election_display(election_data):
    """
    Muotoile vaalin näyttäminen käyttäjälle
    
    Args:
        election_data: Vaalin tiedot
        
    Returns:
        str: Muotoiltu merkkijono
    """
    if not election_data:
        return "Unknown election"
    
    name = election_data.get("name", {}).get("fi", "Nimetön vaali")
    election_id = election_data.get("election_id", "unknown")
    status = election_data.get("status", "unknown")
    
    status_icons = {
        "active": "🟢",
        "upcoming": "🟡", 
        "completed": "🔴",
        "unknown": "⚪"
    }
    
    icon = status_icons.get(status, "⚪")
    return f"    {icon} {name} ({election_id})"
