# tests/integration/test_media_registry.py
#!/usr/bin/env python3
"""
Testaa julkisten avainten mediavahvistusjärjestelmää
"""
import sys
import os
import json

sys.path.insert(0, os.path.abspath('.'))

try:
    from src.managers.media_registry import MediaRegistry
except ImportError as e:
    print(f"Import-virhe: {e}")
    sys.exit(1)

def test_media_registry():
    """Testaa mediavahvistusjärjestelmää"""
    print("🧪 Testataan mediavahvistusjärjestelmää...")
    
    try:
        media_registry = MediaRegistry("Jumaltenvaalit2026")
        
        # 1. Rekisteröi mediajulkaisu
        publication = media_registry.register_media_publication(
            party_id="party_olympos",
            party_name="Olympos-jumalat",
            public_key_fingerprint="bd3c031fd3272a67",
            media_url="https://yle.fi/uutiset/olympos-jumalat-vaalit",
            publication_data={
                "title": "Olympos-jumalat osallistuvat Jumaltenvaaleihin",
                "publication_date": "2025-01-15",
                "content_hash": "a1b2c3d4e5f67890",
                "verification_challenge": "jumalat-2026-verify-001"
            }
        )
        
        print("✅ Mediajulkaisu rekisteröity!")
        print(f"   Julkaisu-ID: {publication['publication_id']}")
        print(f"   Media: {publication['media_domain']}")
        print(f"   Luotettavuuspisteet: {publication['trust_score']}/10")
        
        # 2. Vahvista julkaisu
        verification = media_registry.verify_publication(
            publication_id=publication["publication_id"],
            node_id="node_zeus",
            verification_method="manual"
        )
        
        print(f"   Vahvistus: {verification['status']}")
        print(f"   Luottamustaso: {verification['confidence_score']}")
        
        # 3. Tarkista julkaisun luotettavuus
        publication["verified_by_nodes"].append("node_zeus")
        trust_assessment = media_registry.check_publication_trust(publication)
        
        print(f"   Kokonaisluotettavuus: {trust_assessment['trust_score']}/100")
        print(f"   Luotettavuustaso: {trust_assessment['trust_level']}")
        print(f"   Suositus: {trust_assessment['recommendation']}")
        
        # 4. Testaa eri mediat
        test_publications = [
            {
                "url": "https://vaalit.fi/julkaisut/ukosen-jumalat",
                "expected_trust": 10
            },
            {
                "url": "https://blogspot.com/test-julkaisu", 
                "expected_trust": 3
            },
            {
                "url": "https://hs.fi/vaalit/jumalat",
                "expected_trust": 9
            }
        ]
        
        print("\n🧪 Testataan eri medioita...")
        for test in test_publications:
            test_pub = media_registry.register_media_publication(
                party_id="party_test",
                party_name="Testi Puolue",
                public_key_fingerprint="test123",
                media_url=test["url"],
                publication_data={"title": "Testijulkaisu"}
            )
            
            print(f"   {test_pub['media_domain']}: {test_pub['trust_score']}/10 (odotus: {test['expected_trust']})")
        
        # 5. Tallenna testitulokset
        media_file = "test_media_publications.json"
        with open(media_file, 'w') as f:
            json.dump({
                "publication": publication,
                "verification": verification,
                "trust_assessment": trust_assessment,
                "test_publications": test_publications
            }, f, indent=2)
        
        print(f"📁 Mediajulkaisut tallennettu: {media_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Mediavahvistustesti epäonnistui: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_media_registry()
    sys.exit(0 if success else 1)
