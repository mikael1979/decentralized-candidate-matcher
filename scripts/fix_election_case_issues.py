#!/usr/bin/env python3
"""
Korjaa vaalien case sensitivity ongelmat
"""
import sys
import os
import shutil
from pathlib import Path

# Lisää src hakemisto Python-polkuun
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..', 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

try:
    from core.election_case_manager import ElectionCaseManager
except ImportError as e:
    print(f"❌ Import-virhe: {e}")
    print("💡 Varmista että src/core/election_case_manager.py on olemassa")
    sys.exit(1)

def fix_case_issues(dry_run=True):
    """Korjaa case ongelmat"""
    
    print("🔧 KORJATAAN VAALIEN CASE ONGELMIA")
    print("=" * 50)
    
    case_mgr = ElectionCaseManager()
    
    # Hae konfliktit
    conflicts = case_mgr.detect_case_conflicts()
    recommendations = case_mgr.get_election_name_recommendations()
    
    if conflicts["case_conflicts_found"] == 0:
        print("✅ EI CASE ONGELMIA LÖYDETTY")
        return
    
    print(f"🚨 LÖYDETTY {conflicts['case_conflicts_found']} CASE ONGELMAA:")
    
    for conflict in conflicts["conflicts"]:
        print(f"\\n📁 Konflikti: {conflict['case_insensitive_name']}")
        print(f"   Versiot: {', '.join(conflict['conflicting_names'])}")
    
    print(f"\\n💡 KORJAUSSUOSITUKSET: {recommendations['total_recommendations']}")
    
    if dry_run:
        print("\\n🔍 DRY RUN - ei tehdä muutoksia")
        print("   Käytä --apply tehdäksesi muutokset")
        return
    
    # Toteuta korjaukset
    print("\\n🛠️  TOTEUTETAAN KORJAUKSET...")
    
    for rec in recommendations["recommendations"]:
        from_name = rec["from"]
        to_name = rec["to"]
        
        print(f"\\n🔄 Muutetaan '{from_name}' -> '{to_name}'")
        
        # 1. Korjaa config-hakemisto
        config_from = Path("config/elections") / from_name
        config_to = Path("config/elections") / to_name
        
        if config_from.exists():
            if not config_to.exists():
                print(f"   📁 Siirretään config: {from_name} -> {to_name}")
                shutil.move(str(config_from), str(config_to))
            else:
                print(f"   ⚠️  Config on jo olemassa: {to_name}")
                print(f"   📋 Yhdistetään tiedostot...")
                
                # Laske tiedostot ennen yhdistämistä
                files_before = list(config_from.iterdir())
                
                # Yhdistä tiedostot
                files_moved = 0
                for file in files_before:
                    if file.is_file():
                        target_file = config_to / file.name
                        if not target_file.exists():
                            shutil.move(str(file), str(target_file))
                            files_moved += 1
                        else:
                            print(f"      Tiedosto {file.name} on jo olemassa - säilytetään")
                
                print(f"      Siirretty {files_moved}/{len(files_before)} tiedostoa")
                
                # Poista tyhjä hakemisto
                try:
                    remaining_files = list(config_from.iterdir())
                    if len(remaining_files) == 0:
                        print(f"      🗑️  Poistetaan tyhjä hakemisto: {from_name}")
                        config_from.rmdir()
                    else:
                        print(f"      ⚠️  Hakemistossa on vielä {len(remaining_files)} tiedostoa - jätetään")
                        for remaining_file in remaining_files:
                            print(f"         - {remaining_file.name}")
                except Exception as e:
                    print(f"      ❌ Hakemiston poisto epäonnistui: {e}")
        
        # 2. Korjaa data-hakemisto
        data_from = Path("data/elections") / from_name
        data_to = Path("data/elections") / to_name
        
        if data_from.exists():
            if not data_to.exists():
                print(f"   💾 Siirretään data: {from_name} -> {to_name}")
                shutil.move(str(data_from), str(data_to))
            else:
                print(f"   ⚠️  Data on jo olemassa: {to_name}")
                print(f"   📋 Yhdistetään tiedostot...")
                
                # Laske tiedostot ennen yhdistämistä
                files_before = list(data_from.iterdir())
                
                # Yhdistä tiedostot
                files_moved = 0
                for file in files_before:
                    if file.is_file():
                        target_file = data_to / file.name
                        if not target_file.exists():
                            shutil.move(str(file), str(target_file))
                            files_moved += 1
                        else:
                            print(f"      Tiedosto {file.name} on jo olemassa - säilytetään")
                
                print(f"      Siirretty {files_moved}/{len(files_before)} tiedostoa")
                
                # Poista tyhjä hakemisto
                try:
                    remaining_files = list(data_from.iterdir())
                    if len(remaining_files) == 0:
                        print(f"      🗑️  Poistetaan tyhjä hakemisto: {from_name}")
                        data_from.rmdir()
                    else:
                        print(f"      ⚠️  Hakemistossa on vielä {len(remaining_files)} tiedostoa - jätetään")
                        for remaining_file in remaining_files:
                            print(f"         - {remaining_file.name}")
                except Exception as e:
                    print(f"      ❌ Hakemiston poisto epäonnistui: {e}")
        else:
            print(f"   ℹ️  Data-hakemistoa ei löydy: {from_name}")
    
    print("\\n✅ KORJAUKSET VALMIS!")
    print("   Tarkista vaalit uudelleen komennolla:")
    print("   python scripts/validate_election_integrity.py")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Korjaa vaalien case ongelmat")
    parser.add_argument("--apply", action="store_true", help="Toteuta muutokset (oletus: dry run)")
    
    args = parser.parse_args()
    
    fix_case_issues(dry_run=not args.apply)
