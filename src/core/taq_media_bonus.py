# src/core/taq_media_bonus.py
#!/usr/bin/env python3
"""
TAQ Media Bonus - Debug-versio
"""
from typing import Dict, Optional, List
import json
from pathlib import Path

class TAQMediaBonus:
    """TAQ Media Bonus - Debug-versio"""
    
    def __init__(self, election_id: str):
        self.election_id = election_id
        print("🔄 Alustetaan TAQ Media Bonus...")
        self.trusted_sources = self._load_trusted_sources()
        self.taq_config = self._load_taq_config()
        print(f"✅ TAQ ladattu: {len(self.trusted_sources)} lähdetyyppiä")
        print(f"📋 Lähdetyypit: {list(self.trusted_sources.keys())}")
    
    def _load_trusted_sources(self) -> Dict:
        """Lataa luotetut lähteet konfiguraatiosta - DEBUG VERSIO"""
        config_path = Path("config/system/trusted_sources.json")
        print(f"📁 Ladataan trusted_sources.json: {config_path}")
        
        if not config_path.exists():
            print("❌ trusted_sources.json ei löydy")
            return self._get_default_trusted_sources()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                print(f"📄 Tiedoston koko: {len(content)} merkkiä")
                
                if not content:
                    print("❌ trusted_sources.json on tyhjä")
                    return self._get_default_trusted_sources()
                    
                config = json.loads(content)
                print(f"📊 JSON ladattu, avaimet: {list(config.keys())}")
                
                # TARKISTETAAN ERI TASOJA
                if "trusted_sources" in config:
                    trusted_sources = config["trusted_sources"]
                    print(f"✅ Löytyi trusted_sources: {len(trusted_sources)} kategoriaa")
                    
                    # TARKISTETAAN JOKAINEN KATEGORIA
                    for category, details in trusted_sources.items():
                        print(f"   📁 {category}: domains={details.get('domains', [])}")
                        
                else:
                    print("❌ EI trusted_sources-kenttää")
                    trusted_sources = {}
                
                return trusted_sources
                
        except Exception as e:
            print(f"❌ trusted_sources.json virhe: {e}")
            import traceback
            traceback.print_exc()
            return self._get_default_trusted_sources()
    
    def _load_taq_config(self) -> Dict:
        """Lataa TAQ-konfiguraatio"""
        config_path = Path("config/system/taq_config.json")
        print(f"📁 Ladataan taq_config.json: {config_path}")
        
        if not config_path.exists():
            print("❌ taq_config.json ei löydy")
            return self._get_default_taq_config()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    print("❌ taq_config.json on tyhjä")
                    return self._get_default_taq_config()
                    
                config = json.loads(content)
                print("✅ TAQ-konfiguraatio ladattu onnistuneesti")
                return config
        except Exception as e:
            print(f"❌ taq_config.json virhe: {e}")
            return self._get_default_taq_config()
    
    def _get_default_trusted_sources(self) -> Dict:
        """Oletusarvoiset luotetut lähteet"""
        print("ℹ️  Käytetään oletusarvoisia luotettuja lähteitä")
        return {
            "newspapers": {
                "domains": ["yle.fi", "hsl.fi", "hs.fi", "vaalit.fi"],
                "trust_level": 0.9,
                "bonus_multiplier": 0.6,
                "description": {"fi": "Kansalliset sanomalehdet"}
            },
            "international": {
                "domains": ["bbc.com", "reuters.com", "apnews.com"],
                "trust_level": 0.85,
                "bonus_multiplier": 0.65,
                "description": {"fi": "Kansainväliset uutislähteet"}
            },
            "online_media": {
                "domains": ["mtv.fi", "ilta-sanomat.fi", "verkkolehti.fi"],
                "trust_level": 0.7,
                "bonus_multiplier": 0.7,
                "description": {"fi": "Verkkomediat"}
            },
            "community": {
                "domains": ["paikallislehti.fi", "kylayhteiso.net", "kuntalehti.fi"],
                "trust_level": 0.6,
                "bonus_multiplier": 0.8,
                "description": {"fi": "Paikallismediat"}
            }
        }
    
    def _get_default_taq_config(self) -> Dict:
        """Oletus-TAQ-konfiguraatio"""
        print("ℹ️  Käytetään oletusarvoista TAQ-konfiguraatiota")
        return {
            "media_bonus_levels": {
                "high": {"min_trust_score": 8, "required_approvals": 2, "time_saving": "40%"},
                "medium": {"min_trust_score": 5, "required_approvals": 2, "time_saving": "30%"}, 
                "low": {"min_trust_score": 0, "required_approvals": 3, "time_saving": "20%"}
            },
            "system_settings": {
                "default_trust_score": 3,
                "enable_taq_by_default": False
            }
        }
    
    def find_media_source_type(self, domain: str) -> Optional[str]:
        """Etsi mediatyyppi domainin perusteella"""
        print(f"🔍 Etsitään lähdetyyppiä domainille: '{domain}'")
        print(f"📋 Käytettävissä olevat lähdetyypit: {list(self.trusted_sources.keys())}")
        
        for source_type, config in self.trusted_sources.items():
            domains = config.get("domains", [])
            print(f"   🔎 Tarkistetaan {source_type}: {domains}")
            if domain in domains:
                print(f"   ✅ Löydetty lähdetyyppi: {source_type}")
                return source_type
        
        print(f"   ❌ Lähdetyyppiä ei löydy domainille: '{domain}'")
        return None
    
    def calculate_media_bonus(self, media_domain: str) -> Optional[Dict]:
        """Laske media-bonus konfiguraation perusteella"""
        print(f"🎯 Lasketaan media-bonusta domainille: '{media_domain}'")
        
        # Etsi mediatyyppi
        source_type = self.find_media_source_type(media_domain)
        if not source_type:
            print("❌ Ei lähdetyyppiä, palautetaan None")
            return None
        
        # Hae konfiguraatio turvallisesti
        source_config = self.trusted_sources.get(source_type, {})
        trust_level = source_config.get("trust_level", 0.5)
        bonus_multiplier = source_config.get("bonus_multiplier", 1.0)
        
        print(f"📊 Lähdetyypin {source_type} konfiguraatio:")
        print(f"   - trust_level: {trust_level}")
        print(f"   - bonus_multiplier: {bonus_multiplier}")
        
        # Hae bonus-tasot turvallisesti
        bonus_levels = self.taq_config.get("media_bonus_levels", {})
        print(f"📈 Bonus-tasot saatavilla: {list(bonus_levels.keys())}")
        
        # Määritä bonus-taso trust_levelin perusteella
        level_key = "low"  # Oletus
        if trust_level >= 0.85:
            level_key = "high"
        elif trust_level >= 0.7:
            level_key = "medium"
        
        level_config = bonus_levels.get(level_key, {})
        print(f"🎚️  Valittu bonus-taso: {level_key}")
        print(f"   - Konfiguraatio: {level_config}")
        
        # Tarkista että required_approvals on olemassa
        required_approvals = level_config.get("required_approvals")
        if required_approvals is None:
            print("⚠️  required_approvals puuttuu, käytetään oletusta 3")
            required_approvals = 3
        
        time_saving = level_config.get("time_saving", "0%")
        
        result = {
            "taq_enabled": True,
            "source_type": source_type,
            "trust_level": trust_level,
            "bonus_multiplier": bonus_multiplier,
            "required_approvals": required_approvals,
            "time_saving": time_saving,
            "media_domain": media_domain,
            "source_description": source_config.get("description", {}).get("fi", "Ei kuvausta")
        }
        
        print(f"✅ Bonus laskettu onnistuneesti:")
        for key, value in result.items():
            print(f"   - {key}: {value}")
            
        return result
