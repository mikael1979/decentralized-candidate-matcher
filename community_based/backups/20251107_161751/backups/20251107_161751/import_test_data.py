#!/usr/bin/env python3
"""
Testidatan import-ohjelma kreikkalaisten jumalien vaaleille
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

class TestDataImporter:
    """Lataa testidatan järjestelmään"""
    
    def __init__(self, runtime_dir: str = "runtime"):
        self.runtime_dir = Path(runtime_dir)
        self.runtime_dir.mkdir(exist_ok=True)
        
    def import_all_data(self):
        """Tuo kaikki testidatat järjestelmään"""
        print("🏛️  TUODAAN KREIKKALAISTEN JUMALIEN TESTIDATA...")
        
        try:
            # 1. Tuo puolueet
            self.import_parties()
            
            # 2. Tuo kysymykset
            self.import_questions()
            
            # 3. Tuo ehdokkaat
            self.import_candidates()
            
            # 4. Päivitä meta-tiedot
            self.update_metadata()
            
            print("✅ KAIKKI TESTIDATAT TUOTU ONNISTUNEESTI!")
            self.print_summary()
            
        except Exception as e:
            print(f"❌ VIRHE DATAN TUONNISSA: {e}")
            sys.exit(1)
    
    def import_parties(self):
        """Tuo puolueet"""
        print("📋 Tuodaan puolueet...")
        
        # Lataa testidata
        with open('parties.test.json', 'r', encoding='utf-8') as f:
            test_parties = json.load(f)
        
        # Tallenna runtime-kansioon
        output_file = self.runtime_dir / "parties.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(test_parties, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Tuotu {len(test_parties['parties'])} puoluetta")
    
    def import_questions(self):
        """Tuo kysymykset"""
        print("❓ Tuodaan kysymykset...")
        
        # Lataa testidata
        with open('questions.test.json', 'r', encoding='utf-8') as f:
            test_questions = json.load(f)
        
        # Tallenna runtime-kansioon
        output_file = self.runtime_dir / "questions.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(test_questions, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Tuotu {len(test_questions['questions'])} kysymystä")
    
    def import_candidates(self):
        """Tuo ehdokkaat"""
        print("👑 Tuodaan ehdokkaat...")
        
        # Lataa testidata
        with open('candidates.test.json', 'r', encoding='utf-8') as f:
            test_candidates = json.load(f)
        
        # Tallenna runtime-kansioon
        output_file = self.runtime_dir / "candidates.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(test_candidates, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Tuotu {len(test_candidates['candidates'])} ehdokasta")
    
    def update_metadata(self):
        """Päivitä järjestelmän meta-tiedot"""
        print("📊 Päivitetään meta-tiedot...")
        
        # Luo/Lataa meta.json
        meta_file = self.runtime_dir / "meta.json"
        
        if meta_file.exists():
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta_data = json.load(f)
        else:
            meta_data = {
                "election": {
                    "id": "greek_gods_2024",
                    "name": {
                        "fi": "Kreikkalaisten Jumalien Vaalit 2024",
                        "en": "Greek Gods Election 2024",
                        "sv": "Grekiska Gudarnas Val 2024"
                    },
                    "date": "2024-01-15",
                    "type": "divine_council",
                    "timelock_enabled": True,
                    "edit_deadline": "2024-01-20",
                    "grace_period_hours": 48,
                    "governance_model": "community_driven"
                },
                "system_info": {
                    "system_id": "system_greek_gods",
                    "created": datetime.now().isoformat()
                },
                "version": "1.0.0"
            }
        
        # Päivitä testidatan tiedot
        meta_data["test_data_imported"] = {
            "timestamp": datetime.now().isoformat(),
            "description": "Greek gods test dataset",
            "questions_count": 20,
            "candidates_count": 12,
            "parties_count": 3
        }
        
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(meta_data, f, indent=2, ensure_ascii=False)
        
        print("✅ Meta-tiedot päivitetty")
    
    def print_summary(self):
        """Tulosta yhteenveto tuoduista datoista"""
        print("\n" + "="*50)
        print("🎉 TESTIDATAN YHTEENVETO")
        print("="*50)
        
        # Lataa tiedot summarya varten
        with open(self.runtime_dir / "parties.json", 'r', encoding='utf-8') as f:
            parties = json.load(f)
        
        with open(self.runtime_dir / "questions.json", 'r', encoding='utf-8') as f:
            questions = json.load(f)
        
        with open(self.runtime_dir / "candidates.json", 'r', encoding='utf-8') as f:
            candidates = json.load(f)
        
        print(f"🏛️  POHJA: Kreikkalaisten jumalien vaalit")
        print(f"📋 Puolueita: {len(parties['parties'])}")
        print(f"❓ Kysymyksiä: {len(questions['questions'])}")
        print(f"👑 Ehdokkaita: {len(candidates['candidates'])}")
        
        print(f"\n📁 Data tallennettu hakemistoon: {self.runtime_dir}")
        print(f"⏰ Tuontiaika: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n🚀 KÄYTTÖÖNOTTO:")
        print("python test_elo_system.py  # Testaa ELO-järjestelmää")
        print("python demo_comparisons.py # Tee vertailuja")
        print("python demo_voting.py      # Anna ääniä")

def main():
    """Pääohjelma"""
    if len(sys.argv) > 1:
        runtime_dir = sys.argv[1]
    else:
        runtime_dir = "runtime"
    
    importer = TestDataImporter(runtime_dir)
    importer.import_all_data()

if __name__ == "__main__":
    main()
