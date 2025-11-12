#!/usr/bin/env python3
"""
Yksinkertainen testi analytics-toiminnoille ilman monimutkaisia importteja
"""
import sys
import os
import json
from datetime import datetime

def simple_analytics():
    """Yksinkertainen analytics-testi"""
    print("🧪 Testataan analytics-toimintoja (yksinkertainen versio)...")
    
    try:
        # Tarkista tiedostot
        files_to_check = [
            "data/runtime/questions.json",
            "data/runtime/candidates.json", 
            "data/runtime/parties.json"
        ]
        
        stats = {
            "generated_at": datetime.now().isoformat(),
            "file_stats": {},
            "content_stats": {}
        }
        
        for file_path in files_to_check:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                stats["file_stats"][os.path.basename(file_path)] = {
                    "exists": True,
                    "size_kb": round(os.path.getsize(file_path) / 1024, 2)
                }
                
                if "questions" in data:
                    stats["content_stats"]["questions"] = len(data["questions"])
                    if data["questions"]:
                        ratings = [q.get("elo_rating", {}).get("current_rating", 1000) for q in data["questions"]]
                        stats["content_stats"]["avg_elo_rating"] = round(sum(ratings) / len(ratings), 1)
                
                elif "candidates" in data:
                    stats["content_stats"]["candidates"] = len(data["candidates"])
                    total_answers = sum(len(c.get("answers", [])) for c in data["candidates"])
                    stats["content_stats"]["total_answers"] = total_answers
                
                elif "parties" in data:
                    stats["content_stats"]["parties"] = len(data["parties"])
            else:
                stats["file_stats"][os.path.basename(file_path)] = {"exists": False}
        
        # Näytä tilastot
        print("\n📈 JÄRJESTELMÄNTILASTOT:")
        print(f"   ❓ Kysymyksiä: {stats['content_stats'].get('questions', 0)}")
        if 'avg_elo_rating' in stats['content_stats']:
            print(f"   ⭐ Keskim. ELO: {stats['content_stats']['avg_elo_rating']}")
        print(f"   👑 Ehdokkaita: {stats['content_stats'].get('candidates', 0)}")
        print(f"   📝 Vastauksia: {stats['content_stats'].get('total_answers', 0)}")
        print(f"   🏛️  Puolueita: {stats['content_stats'].get('parties', 0)}")
        
        # Terveysraportti
        print(f"\n🏥 TERVEYSRAPORTTI:")
        issues = []
        
        if stats['content_stats'].get('candidates', 0) == 0:
            issues.append("Ei ehdokkaita")
        
        if stats['content_stats'].get('questions', 0) < 2:
            issues.append("Liian vähän kysymyksiä")
        
        if issues:
            print(f"   ❗ Ongelmia: {len(issues)}")
            for issue in issues:
                print(f"      - {issue}")
            print("   💡 Suositus: Lisää dataa järjestelmään")
        else:
            print("   ✅ Järjestelmä terve!")
        
        return True
        
    except Exception as e:
        print(f"❌ Analytics-testi epäonnistui: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = simple_analytics()
    sys.exit(0 if success else 1)
