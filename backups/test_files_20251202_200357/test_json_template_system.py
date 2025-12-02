#!/usr/bin/env python3
"""
Testaa JSON-pohjaista template-järjestelmää.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.templates.html_templates import HTMLTemplates
from src.templates.json_template_manager import get_json_template_manager

def test_json_template_system():
    """Testaa JSON-templatejärjestelmän perustoiminnot."""
    print("🧪 TESTATAAN JSON-TEMPLATE-JÄRJESTELMÄÄ")
    print("=" * 50)
    
    # Testaa templatejen lataus
    tm = get_json_template_manager()
    templates = tm.list_templates()
    print(f"📋 Ladatut templatet: {templates}")
    
    for template_name in templates:
        info = tm.get_template_info(template_name)
        print(f"  - {template_name}: {info.get('description', 'Ei kuvausta')}")
    
    # Testaa CSS-generointi
    print("\n🎨 TESTAA CSS-GENEROINTI:")
    color_theme = {
        'primary_color': '#2c3e50',
        'secondary_color': '#3498db',
        'accent_color': '#e74c3c', 
        'background_color': '#ecf0f1',
        'text_color': '#2c3e50'
    }
    
    try:
        css = HTMLTemplates.generate_css(color_theme)
        print(f"✅ CSS-generointi onnistui")
        print(f"   Pituus: {len(css)} merkkiä")
        print(f"   Sisältää muuttujat: {'--primary-color' in css and '--secondary-color' in css}")
        print("   Esimerkki:")
        print("   " + "\n   ".join(css.split('\n')[:5]))
    except Exception as e:
        print(f"❌ CSS-generointi epäonnistui: {e}")
        return False
    
    # Testaa ehdokas-generointi
    print("\n👤 TESTAA EHDOkas-GENEROINTI:")
    candidate_data = {
        'name': 'Liisa Esimerkki',
        'age': 35,
        'profession': 'Ohjelmistokehittäjä',
        'campaign_theme': 'Digitaalinen tasa-arvo',
        'platform_points': ['Avoin lähdekoodi', 'Tietosuoja', 'Digitaalinen opetus']
    }
    
    try:
        candidate_html = HTMLTemplates.generate_candidate_html(candidate_data)
        print(f"✅ Ehdokas-generointi onnistui")
        print(f"   Pituus: {len(candidate_html)} merkkiä")
        print(f"   Sisältää nimen: {'Liisa Esimerkki' in candidate_html}")
        print("   Esimerkki:")
        print("   " + candidate_html.split('\n')[0][:80] + "...")
    except Exception as e:
        print(f"❌ Ehdokas-generointi epäonnistui: {e}")
        return False
    
    # Testaa puolue-generointi
    print("\n🏛️ TESTAA PUOLUE-GENEROINTI:")
    party_data = {
        'name': 'Demo Puolue',
        'slogan': 'Demokratiaa kaikille',
        'founded_year': '2020',
        'chairperson': 'Matti Malli', 
        'website': 'https://demopuolue.fi',
        'platform': ['Avoimuus', 'Läpinäkyvyys', 'Kestävä kehitys'],
        'candidates': [candidate_data],
        'election_date': '2024-03-01'
    }
    
    try:
        party_html = HTMLTemplates.generate_party_html(party_data, css)
        print(f"✅ Puolue-generointi onnistui")
        print(f"   Pituus: {len(party_html)} merkkiä")
        print(f"   Sisältää puolueen nimen: {'Demo Puolue' in party_html}")
        print(f"   Sisältää CSS:ää: {'<style>' in party_html}")
        print("   Esimerkki (otsikko):")
        for line in party_html.split('\n')[:3]:
            print("   " + line)
    except Exception as e:
        print(f"❌ Puolue-generointi epäonnistui: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n🎉 KAIKKI TESTIT LÄPÄISTY!")
    return True

if __name__ == "__main__":
    success = test_json_template_system()
    sys.exit(0 if success else 1)
