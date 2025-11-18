# scripts/final_template_report.py
#!/usr/bin/env python3
"""
Lopullinen template-status raportti parannuksen jälkeen
"""
import json
import re
from pathlib import Path

def generate_final_report():
    """Generoi lopullinen template-raportti"""
    base_dir = Path("base_templates")
    template_files = list(base_dir.rglob("*.base.json"))
    
    print("🎯 LOPULLINEN TEMPLATE STATUS RAPORTTI")
    print("=" * 60)
    
    valid_count = 0
    total_placeholders = 0
    
    for template_file in sorted(template_files):
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Analysoi template
            placeholder_count = count_placeholders(data)
            version = data.get("metadata", {}).get("template_version", "unknown")
            has_examples = "examples" in data
            has_guidance = "placeholder_guidance" in data.get("metadata", {})
            
            valid_count += 1
            total_placeholders += placeholder_count
            
            status_icon = "✅" 
            
            print(f"{status_icon} {template_file.relative_to(base_dir)}")
            print(f"   📊 Versio: {version}")
            print(f"   🏷️  Placeholdereita: {placeholder_count}")
            print(f"   📝 Esimerkkejä: {'✅' if has_examples else '❌'}")
            print(f"   💡 Ohjeet: {'✅' if has_guidance else '❌'}")
            
        except Exception as e:
            print(f"❌ {template_file.relative_to(base_dir)}")
            print(f"   💥 Virhe: {e}")
    
    # Yhteenveto
    print(f"\n📈 YHTEENVETO:")
    print(f"   📁 Templateja: {len(template_files)}")
    print(f"   ✅ Validit: {valid_count}/{len(template_files)}")
    print(f"   🏷️  Placeholdereita yhteensä: {total_placeholders}")
    print(f"   📊 Keskiarvo: {total_placeholders/len(template_files):.1f} placeholderia/template")
    
    return valid_count == len(template_files)

def count_placeholders(data):
    """Laske placeholderien määrä"""
    json_str = json.dumps(data)
    placeholders = re.findall(r'\{\{[A-Z][A-Z_]*\}\}', json_str)
    return len(set(placeholders))

if __name__ == "__main__":
    print("Generoidaan lopullinen raportti...\n")
    all_valid = generate_final_report()
    
    if all_valid:
        print("\n🎉 KAIKKI TEMPLATET VALIDEJA JA PARANNETTUJA!")
    else:
        print("\n⚠️  JOITAKIN TEMPLATEJA VAATII VIELÄ KORJAUSTA")
