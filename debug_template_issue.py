#!/usr/bin/env python3
"""
Debuggaa template-ongelmaa.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.templates.json_template_manager import get_json_template_manager

def debug_template_issue():
    """Debuggaa miksi placeholderit eivät toimi."""
    tm = get_json_template_manager()
    
    print("🔍 DEBUG TEMPLATE-ONGELMAA")
    print("=" * 40)
    
    # Tarkistetaan CSS-template
    css_template = tm.get_template('css_theme')
    print("CSS Template rakenne:")
    print(f"  - Onko css_template avain: {'css_template' in css_template}")
    
    css_content = css_template.get('css_template', {})
    print(f"  - CSS template tyyppi: {type(css_content)}")
    
    # Tarkistetaan variables-osa
    variables = css_content.get('variables', '')
    print(f"  - Variables pituus: {len(variables)}")
    print(f"  - Variables sisältö (50 merkkiä): {repr(variables[:50])}")
    
    # Testaa renderöintiä manuaalisesti
    print("\n🎯 TESTAA RENDERÖINTIÄ MANUAALISESTI:")
    color_theme = {
        'primary_color': '#2c3e50',
        'secondary_color': '#3498db',
        'accent_color': '#e74c3c', 
        'background_color': '#ecf0f1',
        'text_color': '#2c3e50'
    }
    
    try:
        rendered_css = tm.render_css_template('css_theme', color_theme)
        print(f"✅ Renderöinti onnistui")
        print(f"   Renderöidyn pituus: {len(rendered_css)}")
        print("   Ensimmäiset 100 merkkiä:")
        print("   " + rendered_css[:100])
        
        # Tarkista placeholderit
        print(f"   primary_color korvattu: {'{primary_color}' not in rendered_css}")
        print(f"   #2c3e50 löytyy: {'#2c3e50' in rendered_css}")
        
    except Exception as e:
        print(f"❌ Renderöinti epäonnistui: {e}")
        import traceback
        traceback.print_exc()
    
    # Testaa HTML-templatejen renderöintiä
    print("\n🔍 DEBUG HTML-TEMPLATEJA:")
    candidate_data = {
        'name': 'Testi Nimi',
        'age': 30,
        'profession': 'Testaaja',
        'campaign_theme': 'Testiteema',
        'platform_points': '<li>Testi</li>'
    }
    
    try:
        candidate_html = tm.render_html_template('candidate_card', candidate_data)
        print(f"✅ Candidate renderöinti onnistui")
        print(f"   Pituus: {len(candidate_html)}")
        print("   Ensimmäiset 100 merkkiä:")
        print("   " + candidate_html[:100])
        print(f"   Nimi löytyy: {'Testi Nimi' in candidate_html}")
        
    except Exception as e:
        print(f"❌ Candidate renderöinti epäonnistui: {e}")

if __name__ == "__main__":
    debug_template_issue()
