# scripts/validate_questions_template.py
#!/usr/bin/env python3
"""
Validoi kysymysten template-laatu
"""
import json
import re
from pathlib import Path

def validate_questions_template():
    """Validoi questions.base.json template"""
    template_path = Path("base_templates/questions/questions.base.json")
    
    print(f"🔍 Validoidaan: {template_path}")
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        issues = []
        
        # 1. Tarkista perusrakenne
        if "metadata" not in data:
            issues.append("❌ Puuttuva metadata-osio")
        if "questions" not in data:
            issues.append("❌ Puuttuva questions-osio")
        
        # 2. Tarkista placeholderit
        placeholder_count = count_placeholders(data)
        if placeholder_count < 5:
            issues.append(f"⚠️  Vähän placeholdereita: {placeholder_count}")
        
        # 3. Tarkista ELO-rakenne
        if data.get("questions") and len(data["questions"]) > 0:
            question = data["questions"][0]
            if "elo_rating" not in question:
                issues.append("❌ Puuttuva elo_rating")
            else:
                required_elo_fields = ["base_rating", "current_rating", "comparison_delta", "vote_delta"]
                for field in required_elo_fields:
                    if field not in question["elo_rating"]:
                        issues.append(f"❌ Puuttuva ELO-kenttä: {field}")
        
        # 4. Tulosta tulokset
        if not issues:
            print("✅ Template on erinomainen!")
            print(f"📊 Placeholdereita: {placeholder_count}")
        else:
            print("❌ Template vaatii parannusta:")
            for issue in issues:
                print(f"  {issue}")
        
        return len(issues) == 0
        
    except Exception as e:
        print(f"❌ Validointivirhe: {e}")
        return False

def count_placeholders(data):
    """Laske placeholderien määrä templatessa"""
    json_str = json.dumps(data)
    placeholders = re.findall(r'\{\{[A-Z_]+\}\}', json_str)
    return len(set(placeholders))  # Uniikit placeholderit

if __name__ == "__main__":
    is_valid = validate_questions_template()
    exit(0 if is_valid else 1)
