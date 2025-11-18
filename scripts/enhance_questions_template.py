# scripts/enhance_questions_template.py
#!/usr/bin/env python3
"""
Kysymysten template-parannus - spesifisti questions.base.json:lle
"""
import json
from pathlib import Path
from datetime import datetime

def enhance_questions_template():
    """Paranna kysymysten template täydellisyyteen"""
    template_path = Path("base_templates/questions/questions.base.json")
    
    print(f"🔧 Parannetaan: {template_path}")
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            current_data = json.load(f)
        
        # 1. Päivitä metadata
        enhanced_data = enhance_metadata(current_data)
        
        # 2. Täydennä ELO-rakenne
        enhanced_data = enhance_elo_rating(enhanced_data)
        
        # 3. Lisää timestamp-kentät
        enhanced_data = enhance_timestamps(enhanced_data)
        
        # 4. Täydennä scale-osio
        enhanced_data = enhance_scale_section(enhanced_data)
        
        # 5. Lisää esimerkki
        enhanced_data = add_examples(enhanced_data)
        
        # Tallenna parannettu template
        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, indent=2, ensure_ascii=False)
        
        print("✅ Kysymysten template parannettu onnistuneesti!")
        
        # Tulosta muutokset
        print_changes(current_data, enhanced_data)
        
    except Exception as e:
        print(f"❌ Virhe: {e}")

def enhance_metadata(data):
    """Paranna metadata-osiota"""
    if "metadata" not in data:
        data["metadata"] = {}
    
    metadata = data["metadata"]
    metadata.update({
        "template_version": "2.1.0",
        "placeholder_guidance": {
            "fi": "Korvaa kaikki {{ISOMPI_KIRJAIMIN}} olevat arvot. Käytä uniikkeja ID:itä.",
            "en": "Replace all {{UPPERCASE}} values. Use unique IDs.",
            "sv": "Ersätt alla {{VERSALER}} värden. Använd unika ID:n."
        },
        "schema_type": "question_base"
    })
    
    return data

def enhance_elo_rating(data):
    """Täydennä ELO-rating rakenne"""
    if "questions" in data and len(data["questions"]) > 0:
        question_template = data["questions"][0]
        
        if "elo_rating" in question_template:
            question_template["elo_rating"].update({
                "comparison_delta": 0,
                "vote_delta": 0,
                "total_comparisons": 0,
                "total_votes": 0,
                "up_votes": 0,
                "down_votes": 0
            })
    
    return data

def enhance_timestamps(data):
    """Lisää timestamp-kentät"""
    if "questions" in data and len(data["questions"]) > 0:
        question_template = data["questions"][0]
        question_template["timestamps"] = {
            "created_local": "{{CREATION_TIMESTAMP}}",
            "modified_local": "{{MODIFICATION_TIMESTAMP}}",
            "last_compared": "{{LAST_COMPARISON_TIMESTAMP}}"
        }
        question_template["status"] = "{{STATUS_ACTIVE_OR_DRAFT}}"
    
    return data

def enhance_scale_section(data):
    """Täydennä scale-osio label-käännöksillä"""
    if "questions" in data and len(data["questions"]) > 0:
        question_template = data["questions"][0]
        
        if "content" in question_template and "scale" in question_template["content"]:
            question_template["content"]["scale"].update({
                "step": 1,
                "labels": {
                    "fi": {
                        "min": "Täysin eri mieltä",
                        "neutral": "Neutraali",
                        "max": "Täysin samaa mieltä"
                    },
                    "en": {
                        "min": "Strongly disagree",
                        "neutral": "Neutral",
                        "max": "Strongly agree"
                    },
                    "sv": {
                        "min": "Helt avig",
                        "neutral": "Neutral",
                        "max": "Helt enig"
                    }
                }
            })
    
    return data

def add_examples(data):
    """Lisää minimaalinen esimerkki"""
    data["examples"] = {
        "minimal_working_example": {
            "local_id": "q_education_001",
            "content": {
                "category": "education",
                "question": {
                    "fi": "Mitä mieltä olet korkeakoulujen maksullisuudesta?",
                    "en": "What is your opinion on university tuition fees?",
                    "sv": "Vad anser du om universitetsavgifter?"
                }
            }
        }
    }
    return data

def print_changes(before, after):
    """Tulosta tehdyt muutokset"""
    print("\n📝 TEHDYT MUUTOKSET:")
    
    # Metadata
    if before["metadata"].get("template_version") != after["metadata"].get("template_version"):
        print(f"  • template_version: {before['metadata'].get('template_version')} → {after['metadata'].get('template_version')}")
    
    # ELO rating
    if "elo_rating" in before["questions"][0]:
        before_elo_keys = set(before["questions"][0]["elo_rating"].keys())
        after_elo_keys = set(after["questions"][0]["elo_rating"].keys())
        new_elo_fields = after_elo_keys - before_elo_keys
        if new_elo_fields:
            print(f"  • ELO-kentät lisätty: {', '.join(new_elo_fields)}")
    
    # Uudet osiot
    new_sections = []
    if "timestamps" in after["questions"][0] and "timestamps" not in before["questions"][0]:
        new_sections.append("timestamps")
    if "examples" in after and "examples" not in before:
        new_sections.append("examples")
    
    if new_sections:
        print(f"  • Uudet osiot: {', '.join(new_sections)}")

if __name__ == "__main__":
    enhance_questions_template()
