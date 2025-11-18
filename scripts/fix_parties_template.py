# scripts/fix_parties_template.py
#!/usr/bin/env python3
"""
Korjaa parties.base.json template JSON-virheen
"""
import json
from pathlib import Path

def fix_parties_template():
    """Korjaa parties.base.json JSON-virhe"""
    template_path = Path("base_templates/governance/parties.base.json")
    
    print(f"🔧 Korjataan: {template_path}")
    
    try:
        # Lue tiedosto raakatekstinä löytääksemme virheen
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Korjaa mahdolliset JSON-virheet
        # 1. Tarkista puuttuvat lainausmerkit
        content = content.replace('"website": "{{WEBSITE}}",', '"website": "{{WEBSITE}}",')
        content = content.replace('"contact_email": "{{CONTACT_EMAIL}}",', '"contact_email": "{{CONTACT_EMAIL}}",')
        
        # 2. Yritä ladata korjattu JSON
        fixed_data = json.loads(content)
        
        # 3. Lisää puuttuvat metadata-kentät
        if "metadata" not in fixed_data:
            fixed_data["metadata"] = {}
        
        metadata = fixed_data["metadata"]
        metadata.update({
            "template_version": "2.1.0",
            "schema_type": "party_base",
            "placeholder_guidance": {
                "fi": "Korvaa kaikki {{ISOMPI_KIRJAIMIN}} olevat arvot todellisilla tiedoilla",
                "en": "Replace all {{UPPERCASE}} values with actual data",
                "sv": "Ersätt alla {{VERSALER}} värden med faktiska data"
            },
            "last_updated": "{{TIMESTAMP}}"
        })
        
        # 4. Lisää esimerkki
        if "examples" not in fixed_data:
            fixed_data["examples"] = {
                "minimal_working_example": {
                    "party_id": "party_example_001",
                    "name": {
                        "fi": "Esimerkki Puolue",
                        "en": "Example Party", 
                        "sv": "Exempelparti"
                    }
                }
            }
        
        # Tallenna korjattu template
        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(fixed_data, f, indent=2, ensure_ascii=False)
        
        print("✅ Parties template korjattu onnistuneesti!")
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON-virhe: {e}")
        print("💡 Tarkista tiedosto manuaalisesti")
    except Exception as e:
        print(f"❌ Virhe: {e}")

if __name__ == "__main__":
    fix_parties_template()
