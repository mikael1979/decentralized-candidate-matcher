# src/core/media_verification.py
class MediaVerificationManager:
    def __init__(self, election_id: str):
        self.election_id = election_id
        self.trusted_sources = self._load_trusted_sources()
    
    def _load_trusted_sources(self) -> dict:
        """Lataa luotetut mediat - laajennettu versio"""
        return {
            "newspapers": ["hs.fi", "yle.fi", "mtv.fi", "ilta-sanomat.fi", "huv.fi"],
            "online_media": ["verkkolehti.fi", "uutisblogi.com", "murobbs.muropaketti.com"],
            "international": ["bbc.com", "reuters.com", "apnews.com", "theguardian.com"],
            "community": ["paikallislehti.fi", "kylayhteiso.net", "kuntalehti.fi"]
        }
    
    def verify_media_publication(self, publication_url: str, party_data: dict) -> dict:
        """Tarkista mediajulkaisu - OPTIMAALINEN BONUS"""
        
        # KÄYTÄ olemassa olevaa logiikkaa enhanced_party_managerista
        from managers.enhanced_party_manager import EnhancedPartyManager
        base_manager = EnhancedPartyManager(self.election_id)
        
        # Tarkista ensin perusmedia (nykyinen toiminta)
        base_verification = base_manager.verify_media_basic(publication_url)
        
        # Sitten TAQ-bonus
        source_type = self._classify_source(publication_url)
        bonus_multiplier = self._calculate_bonus(source_type) if source_type else 1.0
        
        return {
            **base_verification,
            "taq_verified": bool(source_type),
            "taq_source_type": source_type,
            "taq_bonus_multiplier": bonus_multiplier,
            "taq_trust_level": self._calculate_trust_level(source_type) if source_type else 0.0
        }
    
    def _classify_source(self, url: str) -> str:
        """Parannettu luokittelu olemassa olevan koodin pohjalta"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            if domain.startswith('www.'):
                domain = domain[4:]
                
            for source_type, domains in self.trusted_sources.items():
                if any(trusted_domain in domain for trusted_domain in domains):
                    return source_type
            return ""
        except Exception:
            return ""
    
    def _calculate_bonus(self, source_type: str) -> float:
        """Laske bonuskerroin vahvistusajalle"""
        bonuses = {
            "newspapers": 0.6,      # 40% nopeampi (1-0.6=0.4)
            "international": 0.65,   # 35% nopeampi
            "online_media": 0.7,     # 30% nopeampi  
            "community": 0.8         # 20% nopeampi
        }
        return bonuses.get(source_type, 1.0)
    
    def _calculate_trust_level(self, source_type: str) -> float:
        """Laske luottamustaso"""
        trust_levels = {
            "newspapers": 0.9,
            "international": 0.8, 
            "online_media": 0.7,
            "community": 0.6
        }
        return trust_levels.get(source_type, 0.5)
