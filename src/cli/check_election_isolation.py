#!/usr/bin/env python3
"""
CLI-komento vaalien eristystarkistukseen
"""
import sys
import os
import click

# Lisää src hakemisto Python-polkuun
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..', '..')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

try:
    from core.election_isolation_manager import ElectionIsolationManager
except ImportError as e:
    print(f"❌ Import-virhe: {e}")
    sys.exit(1)

@click.command()
@click.option('--election-id', help='Tarkista tietty vaali')
@click.option('--full-scan', is_flag=True, help='Tee täysi systeemin tarkistus')
def check_isolation(election_id, full_scan):
    """Tarkista vaalien eristys ja estä päällekkäisyydet"""
    
    print("🔍 VAALIEN ERISTYS TARKISTUS")
    print("=" * 50)
    
    isolation_mgr = ElectionIsolationManager()
    
    if election_id:
        # Tarkista yksittäinen vaali
        print(f"🎯 Tarkistetaan vaalia: {election_id}")
        health_report = isolation_mgr.get_election_health_report(election_id)
        
        if health_report["overall_health"]:
            print("✅ VAALI TERVE - Ei päällekkäisyyksiä")
        else:
            print("❌ VAALISSA ONGELMIA:")
            for risk in health_report["config_health"]["risk_details"]:
                print(f"   - {risk}")
            for risk in health_report["data_health"]["risk_details"]:
                print(f"   - {risk}")
    
    if full_scan:
        # Täysi systeemin tarkistus
        print("🔍 TEHDÄÄN TÄYSI SYSTEEMIN TARKISTUS...")
        contamination_report = isolation_mgr.detect_cross_election_contamination()
        
        if contamination_report["contamination_risks_found"] == 0:
            print("✅ SYSTEEMI TERVE - Ei päällekkäisyyksiä havaittu")
        else:
            print(f"🚨 LÖYDETTY {contamination_report['contamination_risks_found']} PÄÄLLEKKÄISYYS RISKIÄ:")
            for risk in contamination_report["risks"]:
                print(f"\\n🗳️  Vaali: {risk['election']} ({risk['type']})")
                for detail in risk["risks"]:
                    print(f"   - {detail}")

if __name__ == '__main__':
    check_isolation()
