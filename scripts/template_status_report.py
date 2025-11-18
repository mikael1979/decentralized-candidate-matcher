# scripts/template_status_report.py
#!/usr/bin/env python3
"""
Lopullinen template-status raportti
"""
import json
import re
from pathlib import Path

def generate_template_report():
    """Generoi kattava template-status raportti"""
    base_dir = Path("base_templates")
    template_files = list(base_dir.rglob("*.base.json"))
    
    print("🎯 TEMPLATE STATUS RAPORTTI")
    print("=" * 60)
    
    report = {
        "total_templates": len(template_files),
        "valid_templates": 0,
        "invalid_templates": [],
        "template_details": {}
    }
    
    for template_file in template_files:
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Analysoi template
            placeholder_count = count_placeholders(data)
            version = data.get("metadata", {}).get("template_version", "unknown")
            has_examples = "examples" in data
            has_metadata = "metadata" in data
            
            status = "✅ VALID"
            report["valid_templates"] += 1
            
            report["template_details"][str(template_file)] = {
                "version": version,
                "placeholders": placeholder_count,
                "has_examples": has_examples,
                "has_metadata": has_metadata,
                "status": "valid"
            }
            
            print(f"✅ {template_file.relative_to(base_dir)}")
            print(f"   Version: {version}, Placeholders: {placeholder_count}, Examples: {has_examples}")
            
        except Exception as e:
            report["invalid_templates"].append(str(template_file))
            report["template_details"][str(template_file)] = {
                "status": "invalid",
                "error": str(e)
            }
            print(f"❌ {template_file.relative_to(base_dir)}")
            print(f"   Error: {e}")
    
    # Yhteenveto
    print(f"\n📊 YHTEENVETO:")
    print(f"   Yhteensä: {report['total_templates']} templatea")
    print(f"   Validit: {report['valid_templates']}")
    print(f"   Virheelliset: {len(report['invalid_templates'])}")
    
    return report

def count_placeholders(data):
    """Laske placeholderien määrä"""
    json_str = json.dumps(data)
    placeholders = re.findall(r'\{\{[A-Z][A-Z_]*\}\}', json_str)
    return len(set(placeholders))

if __name__ == "__main__":
    report = generate_template_report()
