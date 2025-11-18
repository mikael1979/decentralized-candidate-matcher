# scripts/enhance_all_templates.py
#!/usr/bin/env python3
"""
Yleinen template-parannus työkalu - parantaa kaikki base templatet
"""
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

class TemplateEnhancer:
    def __init__(self, base_dir: Path = Path("base_templates")):
        self.base_dir = base_dir
        self.enhancement_rules = self._create_enhancement_rules()
    
    def _create_enhancement_rules(self) -> Dict[str, Dict]:
        """Luo parannussäännöt eri template-tyypeille"""
        return {
            "questions": {
                "metadata_fields": {
                    "template_version": "2.1.0",
                    "schema_type": "question_base"
                },
                "add_timestamps": True,
                "enhance_elo_rating": True,
                "add_scale_labels": True,
                "add_examples": True
            },
            "candidates": {
                "metadata_fields": {
                    "template_version": "2.1.0", 
                    "schema_type": "candidate_base"
                },
                "add_timestamps": True,
                "add_answer_explanations": True,
                "add_examples": True
            },
            "parties": {
                "metadata_fields": {
                    "template_version": "2.1.0",
                    "schema_type": "party_base"
                },
                "add_timestamps": True,
                "add_verification_system": True,
                "add_examples": True
            },
            "elections": {
                "metadata_fields": {
                    "template_version": "2.1.0",
                    "schema_type": "election_config_base"
                },
                "add_timestamps": True,
                "add_ipfs_cid_fields": True,
                "add_examples": True
            },
            "system": {
                "metadata_fields": {
                    "template_version": "2.1.0",
                    "schema_type": "system_base"
                },
                "add_timestamps": True,
                "add_integrity_fields": True
            },
            "default": {
                "metadata_fields": {
                    "template_version": "2.1.0",
                    "schema_type": "base_template"
                },
                "add_timestamps": True,
                "add_examples": True
            }
        }
    
    def enhance_all_templates(self):
        """Paranna kaikki template-tiedostot"""
        template_files = list(self.base_dir.rglob("*.base.json"))
        
        print(f"🔍 Löydetty {len(template_files)} template-tiedostoa:")
        for tf in template_files:
            print(f"  • {tf.relative_to(self.base_dir)}")
        
        print("\n🔄 Aloitetaan parannus...")
        
        enhanced_count = 0
        for template_file in template_files:
            if self.enhance_single_template(template_file):
                enhanced_count += 1
        
        print(f"\n🎉 Parannettu {enhanced_count}/{len(template_files)} template-tiedostoa")
        
        # Tulosta yhteenveto
        self.print_enhancement_summary()
    
    def enhance_single_template(self, template_path: Path) -> bool:
        """Paranna yksittäinen template-tiedosto"""
        try:
            relative_path = template_path.relative_to(self.base_dir)
            template_type = self._detect_template_type(relative_path)
            rules = self.enhancement_rules.get(template_type, self.enhancement_rules["default"])
            
            print(f"\n🔧 Parannetaan: {relative_path} [{template_type}]")
            
            with open(template_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            # Sovella parannuksia
            enhanced_data = self._apply_enhancements(template_data, rules, template_type)
            
            # Tallenna parannettu template
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(enhanced_data, f, indent=2, ensure_ascii=False)
            
            # Analysoi parannukset
            placeholder_count = self._count_placeholders(enhanced_data)
            print(f"  ✅ Parannettu - {placeholder_count} placeholderia")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Virhe: {e}")
            return False
    
    def _detect_template_type(self, relative_path: Path) -> str:
        """Tunnista template-tyyppi polun perusteella"""
        path_str = str(relative_path)
        if "questions" in path_str:
            return "questions"
        elif "candidates" in path_str:
            return "candidates" 
        elif "parties" in path_str:
            return "parties"
        elif "elections" in path_str:
            return "elections"
        elif "system" in path_str:
            return "system"
        else:
            return "default"
    
    def _apply_enhancements(self, data: Dict, rules: Dict, template_type: str) -> Dict:
        """Sovella parannuksia template-dataan"""
        enhanced_data = data.copy()
        
        # 1. Päivitä metadata
        enhanced_data = self._enhance_metadata(enhanced_data, rules["metadata_fields"])
        
        # 2. Lisää timestamp-kentät
        if rules.get("add_timestamps"):
            enhanced_data = self._add_timestamps(enhanced_data, template_type)
        
        # 3. Template-spesifiset parannukset
        if template_type == "questions" and rules.get("enhance_elo_rating"):
            enhanced_data = self._enhance_elo_rating(enhanced_data)
        
        if template_type == "questions" and rules.get("add_scale_labels"):
            enhanced_data = self._add_scale_labels(enhanced_data)
        
        if template_type == "candidates" and rules.get("add_answer_explanations"):
            enhanced_data = self._add_answer_explanations(enhanced_data)
        
        if template_type == "parties" and rules.get("add_verification_system"):
            enhanced_data = self._add_verification_system(enhanced_data)
        
        # 4. Lisää esimerkkejä
        if rules.get("add_examples"):
            enhanced_data = self._add_examples(enhanced_data, template_type)
        
        return enhanced_data
    
    def _enhance_metadata(self, data: Dict, metadata_fields: Dict) -> Dict:
        """Paranna metadata-osiota"""
        if "metadata" not in data:
            data["metadata"] = {}
        
        metadata = data["metadata"]
        
        # Päivitä versio ja schema
        metadata.update(metadata_fields)
        
        # Lisää placeholder-ohjeet jos puuttuu
        if "placeholder_guidance" not in metadata:
            metadata["placeholder_guidance"] = {
                "fi": "Korvaa kaikki {{ISOMPI_KIRJAIMIN}} olevat arvot todellisilla tiedoilla",
                "en": "Replace all {{UPPERCASE}} values with actual data", 
                "sv": "Ersätt alla {{VERSALER}} värden med faktiska data"
            }
        
        # Päivitä kuvaus jos on vanha
        if "description" in metadata and isinstance(metadata["description"], str):
            old_desc = metadata["description"]
            metadata["description"] = {
                "fi": f"{old_desc} - KÄYTTÖ: Korvaa {{...}} placeholderit",
                "en": f"{old_desc} - USAGE: Replace {{...}} placeholders",
                "sv": f"{old_desc} - ANVÄNDNING: Ersätt {{...}} platshållare"
            }
        
        return data
    
    def _add_timestamps(self, data: Dict, template_type: str) -> Dict:
        """Lisää timestamp-kentät"""
        if "metadata" in data:
            if "created" not in data["metadata"]:
                data["metadata"]["created"] = "{{TIMESTAMP}}"
            if "last_updated" not in data["metadata"]:
                data["metadata"]["last_updated"] = "{{TIMESTAMP}}"
        
        return data
    
    def _enhance_elo_rating(self, data: Dict) -> Dict:
        """Täydennä ELO-rating rakenne (kysymyksille)"""
        if "questions" in data and len(data["questions"]) > 0:
            for question in data["questions"]:
                if "elo_rating" in question:
                    question["elo_rating"].update({
                        "comparison_delta": 0,
                        "vote_delta": 0,
                        "total_comparisons": 0,
                        "total_votes": 0,
                        "up_votes": 0,
                        "down_votes": 0
                    })
        return data
    
    def _add_scale_labels(self, data: Dict) -> Dict:
        """Lisää scale-labelit (kysymyksille)"""
        if "questions" in data and len(data["questions"]) > 0:
            for question in data["questions"]:
                if "content" in question and "scale" in question["content"]:
                    scale = question["content"]["scale"]
                    if "labels" not in scale:
                        scale["labels"] = {
                            "fi": {"min": "Täysin eri mieltä", "neutral": "Neutraali", "max": "Täysin samaa mieltä"},
                            "en": {"min": "Strongly disagree", "neutral": "Neutral", "max": "Strongly agree"},
                            "sv": {"min": "Helt avig", "neutral": "Neutral", "max": "Helt enig"}
                        }
        return data
    
    def _add_answer_explanations(self, data: Dict) -> Dict:
        """Lisää vastausperustelut (ehdokkaille)"""
        if "candidates" in data and len(data["candidates"]) > 0:
            for candidate in data["candidates"]:
                if "answers" in candidate and len(candidate["answers"]) > 0:
                    for answer in candidate["answers"]:
                        if "explanation" not in answer:
                            answer["explanation"] = {
                                "fi": "{{PERUSTELU_SUOMEKSI}}",
                                "en": "{{EXPLANATION_IN_ENGLISH}}", 
                                "sv": "{{FÖRKLARING_PÅ_SVENSKA}}"
                            }
        return data
    
    def _add_verification_system(self, data: Dict) -> Dict:
        """Lisää vahvistusjärjestelmä (puolueille)"""
        if "parties" in data and len(data["parties"]) > 0:
            for party in data["parties"]:
                if "registration" not in party:
                    party["registration"] = {
                        "verification_status": "{{STATUS_PENDING_OR_VERIFIED}}",
                        "verified_by": ["{{NODE_ID}}"],
                        "verification_timestamp": "{{TIMESTAMP}}"
                    }
        return data
    
    def _add_examples(self, data: Dict, template_type: str) -> Dict:
        """Lisää minimaaliset esimerkit"""
        if "examples" not in data:
            examples = {}
            
            if template_type == "questions":
                examples["minimal_working_example"] = {
                    "local_id": "q_example_001",
                    "content": {
                        "category": "example_category",
                        "question": {
                            "fi": "Esimerkkikysymys suomeksi",
                            "en": "Example question in English",
                            "sv": "Exempelfråga på svenska"
                        }
                    }
                }
            elif template_type == "candidates":
                examples["minimal_working_example"] = {
                    "candidate_id": "cand_example_001",
                    "basic_info": {
                        "name": {
                            "fi": "Esimerkki Ehdokas",
                            "en": "Example Candidate", 
                            "sv": "Exempelkandidat"
                        }
                    }
                }
            
            if examples:
                data["examples"] = examples
        
        return data
    
    def _count_placeholders(self, data: Dict) -> int:
        """Laske placeholderien määrä"""
        json_str = json.dumps(data)
        placeholders = re.findall(r'\{\{[A-Z][A-Z_]*\}\}', json_str)
        return len(set(placeholders))
    
    # Korjataan enhance_all_templates.py summary-osio
    def print_enhancement_summary(self):
        """Tulosta parannusyhteenveto - KORJATTU VERSIO"""
        print("\n📊 PARANNUSYHTEENVETO:")
        
        template_files = list(self.base_dir.rglob("*.base.json"))
        for template_file in template_files:
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                placeholder_count = self._count_placeholders(data)
                version = data.get("metadata", {}).get("template_version", "unknown")
                filename = str(template_file.relative_to(self.base_dir))
                
                print(f"  • {filename:40} v{version:8} {placeholder_count:2} placeholderia")
                
            except Exception as e:
                filename = str(template_file.relative_to(self.base_dir))
                print(f"  • {filename:40} ❌ {e}")
def main():
    """Pääfunktio"""
    print("🎯 HAJAUTETUN VAAILIKONEEN TEMPLATE-PARANNUS")
    print("=" * 50)
    
    enhancer = TemplateEnhancer()
    enhancer.enhance_all_templates()

if __name__ == "__main__":
    main()
