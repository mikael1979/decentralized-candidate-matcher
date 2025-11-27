#!/usr/bin/env python3
"""
Media-tiedostojen vahvistus QuorumManagerille
"""
from typing import Dict, Any


class MediaVerifier:
    """Media-tiedostojen vahvistusprosessin hallinta"""
    
    def add_media_verification(self, verification_process: Dict, media_data: Dict) -> Dict:
        """Lisää media-vahvistus vahvistusprosessiin"""
        if "media_verifications" not in verification_process:
            verification_process["media_verifications"] = []
        
        media_verification = {
            "media_id": media_data.get("media_id"),
            "media_type": media_data.get("media_type"),
            "file_hash": media_data.get("file_hash"),
            "verified_by": media_data.get("verified_by", []),
            "verification_status": "pending"
        }
        
        verification_process["media_verifications"].append(media_verification)
        return verification_process
    
    def verify_media(self, verification_process: Dict, media_id: str, node_id: str) -> Dict:
        """Vahvista media-tiedosto"""
        media_verifications = verification_process.get("media_verifications", [])
        
        for media in media_verifications:
            if media.get("media_id") == media_id:
                if node_id not in media.get("verified_by", []):
                    media["verified_by"].append(node_id)
                
                # Päivitä status jos tarpeeksi vahvistuksia
                if len(media["verified_by"]) >= 3:  # 3 vahvistusta vaaditaan
                    media["verification_status"] = "verified"
                
                break
        
        return verification_process
    
    def get_media_verification_status(self, verification_process: Dict) -> Dict:
        """Hae media-vahvistusten tila"""
        media_verifications = verification_process.get("media_verifications", [])
        verified_count = sum(1 for m in media_verifications 
                           if m.get("verification_status") == "verified")
        pending_count = len(media_verifications) - verified_count
        
        return {
            "total_media_files": len(media_verifications),
            "verified_media_files": verified_count,
            "pending_media_files": pending_count
        }
