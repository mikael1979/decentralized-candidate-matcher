# src/managers/media_registry.py
#!/usr/bin/env python3
"""
Julkisten avainten mediavahvistusjärjestelmä - Päivitetty konfiguroitavaksi
"""
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
from pathlib import Path

class MediaRegistry:
    def __init__(self, election_id: str):
        self.election_id = election_id
        self.trusted_media = self._load_trusted_media_config()
    
    def _load_trusted_media_config(self) -> Dict:
        """Lataa luotetut mediat konfiguraatiosta"""
        try:
            from core.taq_media_bonus import TAQMediaBonus
            taq_manager = TAQMediaBonus(self.election_id)
            
            # Muunna TAQ trusted_sources vanhaan muotoon
            trusted_media = {}
            for source_type, config in taq_manager.trusted_sources.items():
                for domain in config.get("domains", []):
                    trusted_media[domain] = {
                        "trust_score": int(config["trust_level"] * 10),
                        "category": source_type,
                        "verification_api": None
                    }
            return trusted_media
            
        except ImportError:
            # Fallback vanhaan konfiguraatioon
            return {
                "yle.fi": {"trust_score": 10, "category": "newspapers", "verification_api": None},
                "hsl.fi": {"trust_score": 10, "category": "newspapers", "verification_api": None},
                "vaalit.fi": {"trust_score": 10, "category": "newspapers", "verification_api": "https://vaalit.fi/api/verify"},
                "hs.fi": {"trust_score": 9, "category": "newspapers", "verification_api": None},
                "mtv.fi": {"trust_score": 8, "category": "online_media", "verification_api": None}
            }
    
    def register_media_publication(self, party_id: str, party_name: str,
                                 public_key_fingerprint: str, media_url: str,
                                 publication_data: Dict) -> Dict:
        """Rekisteröi mediassa julkaistu julkisen avaimen tiedote"""
        
        # Tarkista media-domain
        domain = self._extract_domain(media_url)
        trust_info = self.trusted_media.get(domain, {"trust_score": 3, "category": "unknown"})
        
        publication_id = f"pub_{hashlib.sha256(media_url.encode()).hexdigest()[:12]}"
        
        publication_record = {
            "publication_id": publication_id,
            "party_id": party_id,
            "party_name": party_name,
            "media_url": media_url,
            "media_domain": domain,
            "public_key_fingerprint": public_key_fingerprint,
            "publication_data": publication_data,
            "publication_timestamp": datetime.now().isoformat(),
            "verification_status": "pending",
            "trust_score": trust_info["trust_score"],
            "media_category": trust_info["category"],
            "verified_by_nodes": [],
            "verification_evidence": []
        }
        
        return publication_record
    
    def verify_publication(self, publication_id: str, node_id: str,
                          verification_method: str = "manual") -> Dict:
        """Vahvista mediassa julkaistu tiedote"""
        
        # Simuloi media-verifikaatio (oikeassa järjestelmässä API-kutsu)
        verification_result = {
            "publication_id": publication_id,
            "node_id": node_id,
            "verification_method": verification_method,
            "verification_timestamp": datetime.now().isoformat(),
            "status": "verified",  # simulated
            "confidence_score": 0.85,
            "evidence": {
                "screenshot_url": f"https://archive.org/{publication_id}",
                "archive_timestamp": datetime.now().isoformat(),
                "verification_notes": "Manual verification completed"
            }
        }
        
        return verification_result
    
    def check_publication_trust(self, publication_record: Dict) -> Dict:
        """Arvioi julkaisun luotettavuus"""
        trust_score = publication_record["trust_score"]
        verifications = len(publication_record["verified_by_nodes"])
        
        # Laske luotettavuuspisteet
        base_trust = trust_score * 10  # Media luotettavuus
        verification_bonus = verifications * 5  # Vahvistusten bonus
        total_score = base_trust + verification_bonus
        
        trust_level = "high" if total_score >= 80 else "medium" if total_score >= 50 else "low"
        
        return {
            "trust_score": total_score,
            "trust_level": trust_level,
            "media_trust": trust_score,
            "verification_count": verifications,
            "recommendation": "accept" if trust_level == "high" else "review"
        }
    
    def _extract_domain(self, url: str) -> str:
        """Poimi domain URL:stä"""
        return url.split('//')[-1].split('/')[0].lower()
