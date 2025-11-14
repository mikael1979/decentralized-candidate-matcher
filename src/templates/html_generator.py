#!/usr/bin/env python3
"""
Staattisen HTML-profiilisivujen generaattori - PÄIVITETTY VERSIO
Käyttää uusia modulaarisia komponentteja
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Tuodaan modulaariset komponentit
try:
    from src.templates.html_templates import HTMLTemplates, PARTY_COLOR_THEMES
    from src.templates.profile_manager import ProfileManager
    from src.templates.ipfs_publisher import IPFSPublisher
except ImportError:
    from html_templates import HTMLTemplates, PARTY_COLOR_THEMES
    from profile_manager import ProfileManager
    from ipfs_publisher import IPFSPublisher

class HTMLProfileGenerator:
    def __init__(self, election_id: str = "Jumaltenvaalit2026"):
        self.election_id = election_id
        self.templates = HTMLTemplates()
        self.profile_manager = ProfileManager(election_id)
        self.ipfs_publisher = IPFSPublisher(election_id)
    
    def generate_and_publish_party_profile(self, party_data: Dict, custom_colors: Dict = None) -> Dict:
        """Generoi ja julkaise puolueen profiili IPFS:ään"""
        
        # Hae puolueen ehdokkaat ja generoi kortit
        candidates = self.profile_manager._get_party_candidates(party_data.get("party_id"))
        candidate_cards = self.profile_manager.generate_candidate_cards(candidates)
        
        # Hae IPFS-CID:t
        ipfs_cids = self.profile_manager._get_ipfs_cids()
        
        # Generoi HTML
        colors = custom_colors or PARTY_COLOR_THEMES["default"]
        page_id = f"party_{party_data['party_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        html_content = self.templates.generate_party_html(
            party_data, colors, page_id, candidate_cards, ipfs_cids, self.election_id
        )
        
        # Tallenna ja julkaise
        filename = f"party_{party_data['party_id']}.html"
        filepath = self.ipfs_publisher.save_local_file(html_content, filename)
        ipfs_cid = self.ipfs_publisher.publish_html_to_ipfs(html_content, filename)
        
        # Päivitä metadata
        profile_id = f"party_{party_data['party_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        metadata = {
            "profile_id": profile_id,
            "entity_id": party_data["party_id"],
            "entity_type": "party",
            "entity_name": party_data["name"]["fi"],
            "filepath": filepath,
            "filename": filename,
            "ipfs_cid": ipfs_cid,
            "ipfs_gateway_url": f"https://ipfs.io/ipfs/{ipfs_cid}" if ipfs_cid and not ipfs_cid.startswith("mock_") else None,
            "generated_at": datetime.now().isoformat(),
            "election_id": self.election_id,
            "color_theme": custom_colors or PARTY_COLOR_THEMES["default"]
        }
        
        self.profile_manager._update_profile_metadata(metadata)
        
        print(f"✅ Puolueen profiili tallennettu: {filepath}")
        if ipfs_cid:
            print(f"🌐 IPFS-CID: {ipfs_cid}")
        
        return metadata
    
    def generate_and_publish_candidate_profile(self, candidate_data: Dict, party_data: Dict = None, 
                                             custom_colors: Dict = None) -> Dict:
        """Generoi ja julkaise ehdokkaan profiili IPFS:ään"""
        
        # Generoi vastauskortit
        answers = candidate_data.get("answers", [])
        answer_cards = self.profile_manager.generate_answer_cards(answers)
        
        # Hae IPFS-CID:t
        ipfs_cids = self.profile_manager._get_ipfs_cids()
        
        # Generoi HTML
        colors = custom_colors or PARTY_COLOR_THEMES["default"]
        page_id = f"candidate_{candidate_data['candidate_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        html_content = self.templates.generate_candidate_html(
            candidate_data, party_data, colors, page_id, answer_cards, ipfs_cids, self.election_id
        )
        
        # Tallenna ja julkaise
        filename = f"candidate_{candidate_data['candidate_id']}.html"
        filepath = self.ipfs_publisher.save_local_file(html_content, filename)
        ipfs_cid = self.ipfs_publisher.publish_html_to_ipfs(html_content, filename)
        
        # Päivitä metadata
        profile_id = f"candidate_{candidate_data['candidate_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        metadata = {
            "profile_id": profile_id,
            "entity_id": candidate_data["candidate_id"],
            "entity_type": "candidate",
            "entity_name": candidate_data["basic_info"]["name"]["fi"],
            "filepath": filepath,
            "filename": filename,
            "ipfs_cid": ipfs_cid,
            "ipfs_gateway_url": f"https://ipfs.io/ipfs/{ipfs_cid}" if ipfs_cid and not ipfs_cid.startswith("mock_") else None,
            "generated_at": datetime.now().isoformat(),
            "election_id": self.election_id,
            "party_id": candidate_data["basic_info"].get("party"),
            "color_theme": custom_colors or PARTY_COLOR_THEMES["default"]
        }
        
        self.profile_manager._update_profile_metadata(metadata)
        
        print(f"✅ Ehdokkaan profiili tallennettu: {filepath}")
        if ipfs_cid:
            print(f"🌐 IPFS-CID: {ipfs_cid}")
        
        return metadata

    # Yhteensopivuusmetodit vanhaa koodia varten
    def generate_party_profile(self, party_data: Dict, custom_colors: Dict = None) -> str:
        """Vanha metodi yhteensopivuuden vuoksi"""
        candidates = self.profile_manager._get_party_candidates(party_data.get("party_id"))
        candidate_cards = self.profile_manager.generate_candidate_cards(candidates)
        ipfs_cids = self.profile_manager._get_ipfs_cids()
        colors = custom_colors or PARTY_COLOR_THEMES["default"]
        page_id = f"party_{party_data['party_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return self.templates.generate_party_html(
            party_data, colors, page_id, candidate_cards, ipfs_cids, self.election_id
        )
    
    def generate_candidate_profile(self, candidate_data: Dict, party_data: Dict = None, 
                                 custom_colors: Dict = None) -> str:
        """Vanha metodi yhteensopivuuden vuoksi"""
        answers = candidate_data.get("answers", [])
        answer_cards = self.profile_manager.generate_answer_cards(answers)
        ipfs_cids = self.profile_manager._get_ipfs_cids()
        colors = custom_colors or PARTY_COLOR_THEMES["default"]
        page_id = f"candidate_{candidate_data['candidate_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return self.templates.generate_candidate_html(
            candidate_data, party_data, colors, page_id, answer_cards, ipfs_cids, self.election_id
        )
    
    def save_base_json(self) -> str:
        """Delegoi ProfileManagerille"""
        return self.profile_manager.save_base_json()
    
    def get_base_json(self) -> Dict:
        """Delegoi ProfileManagerille"""
        return self.profile_manager.get_base_json()
