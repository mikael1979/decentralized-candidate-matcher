#!/usr/bin/env python3
"""
Integraatiotesti analytics-toiminnoille
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import os

# Korjattu import-polku
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
    from src.managers.analytics_manager import AnalyticsManager
except ImportError as e:
    print(f"❌ Import-virhe: {e}")
    sys.exit(1)

def test_analytics():
    """Testaa analytics-toimintoja"""
    print("🧪 Testataan analytics-toimintoja...")
    
    try:
        analytics = AnalyticsManager("Jumaltenvaalit2026")
        
        # Järjestelmän tilastot
        stats = analytics.get_system_stats()
        print("\n📈 JÄRJESTELMÄNTILASTOT:")
        print(f"   Ehdokkaita: {stats['content_stats'].get('candidates', 0)}")
        print(f"   Kysymyksiä: {stats['content_stats'].get('questions', 0)}")
        print(f"   Puolueita: {stats['content_stats'].get('parties', 0)}")
        
        # Kysymysten analytics
        question_analytics = analytics.get_question_analytics()
        if question_analytics:
            print(f"\n❓ KYSYMYSTEN ANALYTICS:")
            print(f"   Yhteensä: {question_analytics['total_questions']} kysymystä")
            print(f"   Kategoriat: {len(question_analytics['categories'])} kpl")
        
        # Terveysraportti
        health_report = analytics.generate_health_report()
        print(f"\n🏥 TERVEYSRAPORTTI:")
        print(f"   Tila: {health_report['system_health']}")
        print(f"   Ongelmia: {len(health_report['issues'])}")
        print(f"   Suosituksia: {len(health_report['recommendations'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Analytics-testi epäonnistui: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_analytics()
    sys.exit(0 if success else 1)
