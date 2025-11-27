#!/usr/bin/env python3
"""
Validoi vaalien eheys case managerin jälkeen
"""
import sys
from pathlib import Path

# Lisää src hakemisto Python-polkuun
current_dir = Path(__file__).parent
src_dir = current_dir.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

try:
    from core.election_case_manager import ElectionCaseManager
except ImportError as e:
    print(f"❌ Import-virhe: {e}")
    sys.exit(1)

def validate_election_integrity():
    """Validoi kaikkien vaalien eheys"""
    
    print("🔍 VALIDOIDAAN VAAILIEN EHKEYS")
    print("=" * 50)
    
    case_mgr = ElectionCaseManager()
    
    # Tarkista case konfliktit
    conflicts = case_mgr.detect_case_conflicts()
    
    if conflicts["case_conflicts_found"] > 0:
        print("❌ CASE KONFLIKTEJA LÖYDETTY:")
        for conflict in conflicts["conflicts"]:
            print(f"   - {conflict['case_insensitive_name']}: {conflict['conflicting_names']}")
        return False
    
    print("✅ EI CASE KONFLIKTEJA")
    
    # Hae kaikki vaalit
    config_path = Path("config/elections")
    if not config_path.exists():
        print("❌ CONFIG-HAKEMISTOA EI LÖYDY")
        return False
    
    elections = [d.name for d in config_path.iterdir() if d.is_dir() and not d.name.startswith('_')]
    print(f"📊 LÖYDETTY {len(elections)} VAAILIA:")
    
    all_consistent = True
    
    for election in sorted(elections):
        consistency = case_mgr.validate_election_name_consistency(election)
        
        if consistency["is_consistent"]:
            print(f"   ✅ {election}: JOHDONMAKAINEN")
        else:
            print(f"   ❌ {election}: ONGELMIA")
            for issue in consistency["issues"]:
                print(f"      - {issue}")
            all_consistent = False
    
    # Tarkista data-hakemistot
    data_path = Path("data/elections")
    if data_path.exists():
        data_elections = [d.name for d in data_path.iterdir() if d.is_dir()]
        print(f"\\n📊 DATA-HAKEMISTOT: {len(data_elections)} VAAILIA")
        
        for election in sorted(data_elections):
            config_exists = (config_path / election).exists()
            if config_exists:
                print(f"   ✅ {election}: CONFIG JA DATA OVAT OLEMASSA")
            else:
                print(f"   ⚠️  {election}: DATA ON MUTTA CONFIG PUUTTUU")
                all_consistent = False
    else:
        print("\\n⚠️  DATA-HAKEMISTOA EI OLEMASSA")
        # Tämä ei välttämättä ole virhe, jos ei ole dataa vielä
    
    print("\\n" + "=" * 50)
    if all_consistent:
        print("🎉 KAIKKI VAAILIT EHJIÄ JA JOHDONMAKAISIA!")
        return True
    else:
        print("⚠️  JOITAKIN ONGELMIA LÖYDETTY - TARKISTA YLLÄOLEVAT")
        return False

if __name__ == "__main__":
    success = validate_election_integrity()
    sys.exit(0 if success else 1)
