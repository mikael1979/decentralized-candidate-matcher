# src/managers/quorum_manager.py
#!/usr/bin/env python3
"""
Hajautettu kvoorumi-pohjainen puoluevahvistusjärjestelmä - PÄIVITETTY TAQ:lla
Nyt sisältää config-päivitysten tuen
"""
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from .crypto_manager import CryptoManager

class QuorumManager:
    def __init__(self, election_id: str):
        self.election_id = election_id
        self.crypto = CryptoManager()
        
        # Kvoorumikonfiguraatio - PÄIVITETTY config-päivityksillä
        self.quorum_config = {
            "min_nodes_for_verification": 3,
            "approval_threshold_percent": 60,
            "verification_timeout_hours": 24,
            "rejection_quorum_percent": 40,
            "node_weight_calculation": "based_on_history",
            "taq_enabled": True,
            
            # UUSI: Config-päivitysten asetukset
            "config_update_settings": {
                "config_update_minor": {
                    "base_threshold": 0.51,
                    "min_approvals": 2,
                    "timeout_hours": 24,
                    "description": "Pienet muutokset (UI, tekstit)"
                },
                "config_update_major": {
                    "base_threshold": 0.75,
                    "min_approvals": 5, 
                    "timeout_hours": 48,
                    "description": "Kriittiset muutokset (turvallisuus, rajat)"
                },
                "config_update_emergency": {
                    "base_threshold": 0.40,
                    "min_approvals": 2,
                    "timeout_hours": 6,
                    "description": "Hätätilannekorjaukset"
                }
            }
        }
    
    def initialize_party_verification(self, party_data: Dict) -> Dict:
        """Alusta puolueen kvoorumivahvistus - PÄIVITETTY TAQ:lla"""
        
        # TARKISTA TAQ-BONUS
        taq_bonus = self._get_taq_bonus_for_party(party_data)
        
        verification_process = {
            "party_id": party_data["party_id"],
            "party_name": party_data["name"]["fi"],
            "public_key_fingerprint": party_data["crypto_identity"]["key_fingerprint"],
            "verification_started": datetime.now().isoformat(),
            "verification_timeout": self._calculate_timeout_with_taq(taq_bonus),
            "current_phase": "media_verification",
            "quorum_votes": [],
            "media_verifications": [],
            "final_decision": None,
            "decision_timestamp": None,
            "taq_bonus": taq_bonus,
            "required_approvals": self._calculate_required_approvals_with_taq(taq_bonus)
        }
        
        print(f"🎯 KV OORUMI ALUSTETTU: {party_data['party_id']}")
        if taq_bonus.get("taq_enabled"):
            print(f"   🚀 TAQ-BONUS AKTIIVINEN: {taq_bonus.get('time_saving', '0%')} nopeutus")
            print(f"   👥 VAHVISTUKSET: {verification_process['required_approvals']}/3")
        else:
            print(f"   ℹ️  Normaali kvoorumi: 3/3 vahvistusta, 24h aikaraja")
        
        return verification_process

    # UUSI: Config-päivitysten tuki
    def initialize_config_update_verification(self, config_proposal: Dict) -> Dict:
        """Alusta config-päivityksen kvoorumivahvistus"""
        
        proposal_type = config_proposal["type"]
        config_settings = self.quorum_config["config_update_settings"].get(
            proposal_type, 
            self.quorum_config["config_update_settings"]["config_update_minor"]
        )
        
        # Laske TAQ-parametrit config-päivitykselle
        taq_parameters = self._calculate_config_taq_parameters(config_proposal)
        
        verification_process = {
            "proposal_id": config_proposal["proposal_id"],
            "proposal_type": proposal_type,
            "config_hash_before": config_proposal["current_config_hash"],
            "config_hash_after": config_proposal["proposed_config_hash"],
            "verification_started": datetime.now().isoformat(),
            "verification_timeout": self._calculate_config_timeout(proposal_type),
            "current_phase": "quorum_voting",
            "quorum_votes": [],
            "final_decision": None,
            "decision_timestamp": None,
            "taq_parameters": taq_parameters,
            "required_approvals": taq_parameters["min_approvals"],
            "changes": config_proposal["changes"],
            "justification": config_proposal["justification"]
        }
        
        print(f"🎯 CONFIG-PÄIVITYS KV OORUMI: {config_proposal['proposal_id']}")
        print(f"   📊 Tyyppi: {proposal_type}")
        print(f"   🎯 Kynnys: {taq_parameters['base_threshold']}")
        print(f"   👥 Vaadittu: {taq_parameters['min_approvals']}")
        print(f"   ⏰ Aikaraja: {config_settings['timeout_hours']}h")
        
        return verification_process
    
    def _calculate_config_taq_parameters(self, config_proposal: Dict) -> Dict:
        """Laske TAQ-parametrit config-päivitykselle"""
        proposal_type = config_proposal["type"]
        base_params = self.quorum_config["config_update_settings"][proposal_type].copy()
        
        # Aikapohjainen adaptointi
        base_params["time_adjusted_threshold"] = self._get_time_adjusted_threshold(
            base_params["base_threshold"]
        )
        
        # Kriittisten kohtien tunnistus
        critical_keys = ["max_candidates", "security_measures", "crypto_settings", "network_config"]
        changes = config_proposal["changes"]
        
        if any(key in str(changes.keys()) for key in critical_keys):
            base_params["base_threshold"] = max(base_params["base_threshold"], 0.80)
            base_params["min_approvals"] = max(base_params["min_approvals"], 5)
            print(f"   ⚠️  Kriittinen muutos - nostettu kynnystä")
        
        # Media-bonus config-päivityksille
        if config_proposal.get("media_bonus_applied"):
            base_params["base_threshold"] = base_params["base_threshold"] * 0.8  # 20% helpompi
            base_params["min_approvals"] = max(2, base_params["min_approvals"] - 1)
            print(f"   📰 Media-bonus aktivoitu - alennettu kynnystä")
        
        return base_params
    
    def _calculate_config_timeout(self, proposal_type: str) -> str:
        """Laske config-päivityksen aikaraja"""
        config_settings = self.quorum_config["config_update_settings"]
        timeout_hours = config_settings.get(proposal_type, config_settings["config_update_minor"])["timeout_hours"]
        return (datetime.now() + timedelta(hours=timeout_hours)).isoformat()
    
    def _get_time_adjusted_threshold(self, base_threshold: float) -> float:
        """Säädä kynnystä ajan mukaan - yksinkertaistettu toteutus"""
        # Toteutus: Ensimmäisen 24h normaali, sitten aleneva
        return base_threshold
    
    def cast_vote(self, verification_process: Dict, node_id: str, 
                 vote: str, node_public_key: str, justification: str = "") -> bool:
        """Äänestä puolueen vahvistamisesta TAI config-päivityksestä - PÄIVITETTY"""
        
        if vote not in ["approve", "reject", "abstain"]:
            return False
        
        # Tarkista että node ei ole jo äänestänyt
        existing_vote = next((v for v in verification_process["quorum_votes"] 
                            if v["node_id"] == node_id), None)
        if existing_vote:
            print(f"❌ Node {node_id} on jo äänestänyt")
            return False
        
        # Tarkista aikaraja
        timeout = datetime.fromisoformat(verification_process["verification_timeout"])
        if datetime.now() > timeout:
            print("⏰ Äänestysaika on päättynyt")
            verification_process["final_decision"] = "timeout"
            return False
        
        # Laske noden painoarvo
        node_weight = self._calculate_node_weight(node_id, node_public_key)
        
        # Luo äänirakenne
        vote_record = {
            "node_id": node_id,
            "vote": vote,
            "weight": node_weight,
            "justification": justification,
            "timestamp": datetime.now().isoformat(),
            "node_public_key_fingerprint": self.crypto.calculate_fingerprint(node_public_key),
            "vote_signature": self._sign_vote(node_id, vote, node_public_key)
        }
        
        verification_process["quorum_votes"].append(vote_record)
        
        # Tarkista onko päätös saavutettu - eri logiikka config-päivityksille
        if "proposal_type" in verification_process:  # Config-päivitys
            return self._check_config_quorum_decision(verification_process)
        else:  # Perus puoluevahvistus
            return self._check_quorum_decision_with_taq(verification_process)
    
    def _check_config_quorum_decision(self, verification_process: Dict) -> bool:
        """Tarkista onko config-päivityksen kvoorumipäätös saavutettu"""
        
        votes = verification_process["quorum_votes"]
        if not votes:
            return False
        
        # Käytä TAQ-määrittelemää vaadittujen hyväksyntöjen määrää
        required_approvals = verification_process.get("required_approvals", 3)
        base_threshold = verification_process["taq_parameters"]["base_threshold"]
        
        total_votes = len(votes)
        approve_count = len([v for v in votes if v["vote"] == "approve"])
        reject_count = len([v for v in votes if v["vote"] == "reject"])
        
        approval_ratio = approve_count / total_votes if total_votes > 0 else 0
        
        print(f"📊 CONFIG-ÄÄNESTYSTILANNE: {approve_count}/{required_approvals} hyväksyntää")
        print(f"   📈 Hyväksymisprosentti: {approval_ratio:.1%} (vaaditaan {base_threshold:.1%})")
        
        # Tarkista minimihyvaksynnät JA kynnys
        if (approve_count >= required_approvals and 
            approval_ratio >= base_threshold):
            verification_process["final_decision"] = "approved"
            verification_process["decision_timestamp"] = datetime.now().isoformat()
            print(f"🎉 CONFIG-PÄIVITYS HYVÄKSYTTY!")
            print(f"   ✅ {approve_count}/{required_approvals} ääntä, {approval_ratio:.1%} hyväksyntä")
            return True
        
        # Tarkista hylkäys (enemmistö hylkää)
        elif reject_count > approve_count and total_votes >= 3:
            verification_process["final_decision"] = "rejected"
            verification_process["decision_timestamp"] = datetime.now().isoformat()
            print(f"❌ CONFIG-PÄIVITYS HYLÄTTY! {reject_count}/{total_votes} ääntä")
            return True
        
        return False
    
    def _get_taq_bonus_for_party(self, party_data: Dict) -> Dict:
        """Hae TAQ-bonus puolueelle"""
        try:
            from core.taq_media_bonus import TAQMediaBonus
            taq_manager = TAQMediaBonus(self.election_id)
            
            # Tarkista onko puolueella mediajulkaisuja
            publications = party_data.get("media_publications", [])
            if not publications:
                return {"taq_enabled": False}
                
            # Käytä viimeisintä julkaisua
            latest_pub = publications[-1]
            media_domain = latest_pub.get("media_domain", "")
            
            bonus = taq_manager.calculate_media_bonus(media_domain)
            return bonus if bonus else {"taq_enabled": False}
            
        except ImportError as e:
            print(f"⚠️  TAQ Media Bonus ei saatavilla: {e}")
            return {"taq_enabled": False}
        except Exception as e:
            print(f"⚠️  TAQ-bonuksen haku epäonnistui: {e}")
            return {"taq_enabled": False}
    
    def _calculate_timeout_with_taq(self, taq_bonus: Dict) -> str:
        """Laske timeout TAQ-bonuksen perusteella"""
        base_hours = self.quorum_config["verification_timeout_hours"]
        
        if taq_bonus.get("taq_enabled"):
            bonus_multiplier = taq_bonus.get("bonus_multiplier", 1.0)
            # Käytä bonus_multiplieria timeoutin lyhentämiseen
            taq_hours = base_hours * bonus_multiplier
            timeout = datetime.now() + timedelta(hours=taq_hours)
            print(f"⏰ TAQ-TIMEOUT: {taq_hours:.1f}h (normaali: {base_hours}h)")
        else:
            timeout = datetime.now() + timedelta(hours=base_hours)
        
        return timeout.isoformat()
    
    def _calculate_required_approvals_with_taq(self, taq_bonus: Dict) -> int:
        """Laske tarvittavat hyväksynnät TAQ-bonuksen perusteella"""
        base_approvals = self.quorum_config["min_nodes_for_verification"]
        
        if taq_bonus.get("taq_enabled"):
            taq_approvals = taq_bonus.get("required_approvals", base_approvals)
            print(f"👥 TAQ-VAHVISTUKSET: {taq_approvals}/{base_approvals}")
            return taq_approvals
        
        return base_approvals
    
    def _check_quorum_decision_with_taq(self, verification_process: Dict) -> bool:
        """Tarkista onko kvoorumipäätös saavutettu - PÄIVITETTY TAQ:lla"""
        
        votes = verification_process["quorum_votes"]
        if not votes:
            return False
        
        # Käytä TAQ-määrittelemää vaadittujen hyväksyntöjen määrää
        required_approvals = verification_process.get("required_approvals", 
                                                     self.quorum_config["min_nodes_for_verification"])
        
        total_weight = sum(vote["weight"] for vote in votes)
        approve_weight = sum(vote["weight"] for vote in votes if vote["vote"] == "approve")
        reject_weight = sum(vote["weight"] for vote in votes if vote["vote"] == "reject")
        
        approval_ratio = (approve_weight / total_weight) * 100 if total_weight > 0 else 0
        rejection_ratio = (reject_weight / total_weight) * 100 if total_weight > 0 else 0
        
        approval_threshold = self.quorum_config["approval_threshold_percent"]
        rejection_threshold = self.quorum_config["rejection_quorum_percent"]
        
        # Tarkista ehdot - PÄIVITETTY: käytä TAQ-vaatimia hyväksyntöjä
        approve_count = len([v for v in votes if v["vote"] == "approve"])
        has_min_approvals = approve_count >= required_approvals
        has_approval_quorum = approval_ratio >= approval_threshold
        
        # Tarkista hylkäys (yli puolet hylkää)
        total_votes = len(votes)
        reject_count = len([v for v in votes if v["vote"] == "reject"])
        has_rejection_quorum = rejection_ratio >= rejection_threshold
        
        taq_enabled = verification_process.get("taq_bonus", {}).get("taq_enabled", False)
        
        print(f"📊 ÄÄNESTYSTILANNE: {approve_count}/{required_approvals} hyväksyntää" + 
              f" ({'TAQ' if taq_enabled else 'normaali'})")
        
        if has_min_approvals and has_approval_quorum:
            verification_process["final_decision"] = "approved"
            verification_process["decision_timestamp"] = datetime.now().isoformat()
            print(f"🎉 PUOLUE HYVÄKSYTTY! {approve_count}/{required_approvals} ääntä")
            if taq_enabled:
                print("   🚀 TAQ-BONUS AUTTOI - nopeampi vahvistus!")
            return True
        
        elif has_rejection_quorum and total_votes >= 3:
            verification_process["final_decision"] = "rejected" 
            verification_process["decision_timestamp"] = datetime.now().isoformat()
            print(f"❌ PUOLUE HYLKÄTTY! {reject_count}/{total_votes} ääntä")
            return True
        
        return False
    
    def add_media_verification(self, verification_process: Dict, 
                             publication_record: Dict, node_id: str) -> bool:
        """Lisää mediavahvistus kvoorumiprosessiin"""
        
        media_verification = {
            "publication_id": publication_record["publication_id"],
            "media_domain": publication_record["media_domain"],
            "trust_score": publication_record["trust_score"],
            "verified_by_node": node_id,
            "verification_timestamp": datetime.now().isoformat(),
            "evidence_url": publication_record.get("media_url", "")
        }
        
        verification_process["media_verifications"].append(media_verification)
        
        # Siirrä seuraavaan vaiheeseen jos mediavahvistukset saavutettu
        media_verifications = len(verification_process["media_verifications"])
        if (media_verifications >= 2 and 
            verification_process["current_phase"] == "media_verification"):
            verification_process["current_phase"] = "quorum_voting"
        
        return True
    
    def _calculate_node_weight(self, node_id: str, node_public_key: str) -> int:
        """Laske noden painoarvo äänestyksessä"""
        # Yksinkertaistettu - oikeassa järjestelmässä perustuisi historiaan
        base_weight = 10
        
        # Lisää painoa jos node on vanha ja luotettu
        if node_id.startswith("node_zeus") or node_id.startswith("node_athena"):
            base_weight += 5
        
        return base_weight
    
    def _sign_vote(self, node_id: str, vote: str, node_public_key: str) -> str:
        """Allekirjoita ääni (yksinkertaistettu)"""
        vote_data = f"{node_id}:{vote}:{datetime.now().isoformat()}"
        return hashlib.sha256(vote_data.encode()).hexdigest()
    
    def get_verification_status(self, verification_process: Dict) -> Dict:
        """Hae vahvistusprosessin tila - PÄIVITETTY config-tuella"""
        
        votes = verification_process["quorum_votes"]
        total_votes = len(votes)
        
        status = {
            "party_id": verification_process.get("party_id", verification_process.get("proposal_id")),
            "current_phase": verification_process["current_phase"],
            "total_votes": total_votes,
            "approve_votes": len([v for v in votes if v["vote"] == "approve"]),
            "reject_votes": len([v for v in votes if v["vote"] == "reject"]),
            "abstain_votes": len([v for v in votes if v["vote"] == "abstain"]),
            "media_verifications": len(verification_process.get("media_verifications", [])),
            "time_remaining_hours": self._calculate_time_remaining(verification_process),
            "final_decision": verification_process.get("final_decision"),
            "quorum_met": verification_process.get("final_decision") is not None,
            "taq_bonus": verification_process.get("taq_bonus", {}),
            "required_approvals": verification_process.get("required_approvals", 3),
            "verification_timeout": verification_process.get("verification_timeout")
        }
        
        # Config-spesifiset kentät
        if "proposal_type" in verification_process:
            status["proposal_type"] = verification_process["proposal_type"]
            status["changes"] = verification_process.get("changes", {})
            status["justification"] = verification_process.get("justification", "")
        
        return status
    
    def _calculate_time_remaining(self, verification_process: Dict) -> float:
        """Laske jäljellä oleva aika tunneissa"""
        timeout = datetime.fromisoformat(verification_process["verification_timeout"])
        remaining = timeout - datetime.now()
        return max(0, remaining.total_seconds() / 3600)
