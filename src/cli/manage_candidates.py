#!/usr/bin/env python3
import click
import json
from datetime import datetime
import os
import sys
import uuid
from pathlib import Path

# LISÄTTY: Lisää src hakemisto Python-polkuun
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config_manager import get_election_id, get_data_path
from core.file_utils import read_json_file, write_json_file, ensure_directory

# MULTINODE: Tuo uudet moduulit
try:
    from nodes.core.node_identity import NodeIdentity
    from nodes.core.network_manager import NetworkManager
    from nodes.protocols.consensus import ConsensusManager
    MULTINODE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Multinode modules not available: {e}")
    MULTINODE_AVAILABLE = False

# KORJATTU: Tarkista ensin jos data_validator on saatavilla
try:
    from core.data_validator import validate_candidate_uniqueness, get_candidate_by_id_or_name
except ImportError:
    # Fallback jos data_validator ei ole saatavilla
    def validate_candidate_uniqueness(candidates_file, new_candidate_name):
        """Yksinkertainen validointi jos data_validator puuttuu"""
        if not os.path.exists(candidates_file):
            return True
        
        try:
            data = read_json_file(candidates_file, {"candidates": []})
            existing_names = [
                c["basic_info"]["name"]["fi"].lower().strip() 
                for c in data.get("candidates", [])
                if "basic_info" in c and "name" in c["basic_info"] and "fi" in c["basic_info"]["name"]
            ]
            return new_candidate_name.lower().strip() not in existing_names
        except Exception:
            return True
    
    def get_candidate_by_id_or_name(candidates_file, identifier):
        """Yksinkertainen haku jos data_validator puuttuu"""
        if not os.path.exists(candidates_file):
            return None
        
        try:
            data = read_json_file(candidates_file, {"candidates": []})
            for candidate in data.get("candidates", []):
                if (candidate.get("id") == identifier or 
                    candidate.get("basic_info", {}).get("name", {}).get("fi") == identifier or
                    candidate.get("basic_info", {}).get("name", {}).get("en") == identifier):
                    return candidate
            return None
        except Exception:
            return None


class CandidateManager:
    """Ehdokkaiden hallinta config-järjestelmän kanssa - MULTINODE VERSION"""
    
    def __init__(self, election_id=None, enable_multinode=False, bootstrap_debug=False):
        self.election_id = election_id or get_election_id()
        self.data_path = get_data_path(self.election_id)
        self.candidates_file = Path(self.data_path) / "candidates.json"
        
        # MULTINODE: Alusta node-järjestelmä
        self.enable_multinode = enable_multinode
        self.bootstrap_debug = bootstrap_debug
        self.node_identity = None
        self.network_manager = None
        self.consensus_manager = None
        
        if self.enable_multinode and MULTINODE_AVAILABLE:
            self._initialize_multinode()
    
    def _initialize_multinode(self):
        """Alustaa multinode-järjestelmän ehdokkaiden hallintaan"""
        try:
            print("🌐 Alustetaan multinode-ehdokkaiden hallinta...")
            
            # Lataa olemassa oleva node identity tai luo uusi
            self.node_identity = self._load_or_create_node_identity()
            
            # Luo verkkomanageri
            self.network_manager = NetworkManager(self.node_identity)
            
            # Luo konsensusmanageri
            self.consensus_manager = ConsensusManager(self.network_manager)
            
            # Yhdistä verkkoon
            bootstrap_peers = self._get_bootstrap_peers()
            self.network_manager.connect_to_network(bootstrap_peers)
            
            print(f"✅ Multinode ehdokkaiden hallinta alustettu: {self.node_identity.node_id}")
            print(f"   📡 Network peers: {self.network_manager.get_peer_count()}")
            
        except Exception as e:
            print(f"⚠️  Multinode initialization failed: {e}")
            self.enable_multinode = False
    
    def _load_or_create_node_identity(self):
        """Lataa olemassa oleva node identity tai luo uusi"""
        try:
            # Yritä ladata olemassa oleva identity
            identity_files = list(Path(f"data/nodes/{self.election_id}").glob("*_identity.json"))
            if identity_files:
                latest_file = max(identity_files, key=lambda f: f.stat().st_mtime)
                identity = NodeIdentity(self.election_id, "worker")
                if identity.load_identity(latest_file.stem.replace("_identity", "")):
                    print(f"✅ Loaded existing node identity: {identity.node_id}")
                    return identity
            
            # Luo uusi identity
            identity = NodeIdentity(
                election_id=self.election_id,
                node_type="worker", 
                node_name=f"candidate_manager_{self.election_id}",
                domain="candidate_management"
            )
            identity.save_identity()
            return identity
            
        except Exception as e:
            print(f"⚠️  Failed to load/create node identity: {e}")
            # Fallback: Luo uusi identity
            identity = NodeIdentity(self.election_id, "worker")
            identity.save_identity()
            return identity
    
    def _get_bootstrap_peers(self):
        """Hae bootstrap-peerit - YKSINKERTAISTETTU"""
        if self.bootstrap_debug:
            print("🔧 DEBUG: Using debug bootstrap for candidate management")
            # Luo mock-peerit debug-tilassa
            debug_peers = []
            for i in range(2):
                peer = NodeIdentity(
                    election_id=self.election_id,
                    node_type="coordinator",
                    node_name=f"debug_candidate_peer_{i+1}",
                    domain="debug_candidates"
                )
                debug_peers.append(peer)
            return debug_peers
        else:
            print("🔧 Using empty bootstrap peers for candidate management")
            return []
    
    def _propose_candidate_change(self, action, candidate_data, justification):
        """Lähetä ehdokasmuutos konsensusproposalina verkkoon"""
        if not self.enable_multinode or not self.consensus_manager:
            return True, "Multinode not enabled - change applied locally"
        
        try:
            # Varmista että candidate_data on serialisoitavissa
            serializable_data = candidate_data.copy() if hasattr(candidate_data, 'copy') else candidate_data
            
            # Jos se on dictionary, varmista että kaikki arvot ovat serialisoitavissa
            if isinstance(serializable_data, dict):
                serializable_data = {
                    key: (value.isoformat() if hasattr(value, 'isoformat') else value)
                    for key, value in serializable_data.items()
                }
        
            proposal_data = {
                "action": action,
                "candidate_data": serializable_data,
                "justification": justification,
                "proposer": self.node_identity.node_id,
                "timestamp": datetime.now().isoformat()
            }
            
            proposal_id = self.consensus_manager.create_proposal(
                "candidate_management",
                proposal_data,
                timeout_seconds=30
            )
            
            print(f"📤 Candidate change proposed to network: {proposal_id}")
            print(f"   🎯 Action: {action}")
            print(f"   📝 Justification: {justification}")
            
            # Odota konsensusta (mock-toteutus)
            import time
            time.sleep(2)
            
            # Tarkista proposalin status
            proposal_status = self.consensus_manager.get_proposal_status(proposal_id)
            if proposal_status and proposal_status.get("status") == "approved":
                return True, f"Change approved by network consensus: {proposal_id}"
            else:
                return False, f"Change rejected or timed out: {proposal_id}"
                
        except Exception as e:
            print(f"⚠️  Consensus proposal failed: {e}")
            import traceback
            traceback.print_exc()
            return True, "Fallback: Change applied locally"
    
    def load_candidates(self):
        """Lataa ehdokkaat"""
        if not self.candidates_file.exists():
            return {"candidates": []}
        return read_json_file(self.candidates_file)
    
    def save_candidates(self, candidates_data):
        """Tallenna ehdokkaat"""
        ensure_directory(self.candidates_file.parent)
        write_json_file(self.candidates_file, candidates_data)
    
    def add_candidate(self, name_fi, name_en=None, party="sitoutumaton", domain="yleinen", is_active=True):
        """Lisää uusi ehdokas - MULTINODE: Lähetä konsensusproposalina"""
        candidates_data = self.load_candidates()
        
        # Tarkista uniikkius
        if not validate_candidate_uniqueness(self.candidates_file, name_fi):
            return False, "Ehdokas samalla nimellä on jo olemassa"
        
        # Luo uusi ehdokas
        candidate_id = f"cand_{uuid.uuid4().hex[:8]}"
        new_candidate = {
            "id": candidate_id,
            "basic_info": {
                "name": {
                    "fi": name_fi,
                    "en": name_en or name_fi
                },
                "party": party,
                "domain": domain,
                "is_active": is_active,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            },
            "status": "active" if is_active else "inactive",
            "answers_count": 0
        }
        
        # MULTINODE: Lähetä muutos konsensusproposalina
        if self.enable_multinode:
            success, consensus_message = self._propose_candidate_change(
                "add_candidate",
                new_candidate,
                f"Add new candidate: {name_fi} ({party})"
            )
            if not success:
                return False, f"Network rejected candidate: {consensus_message}"
            print(f"🌐 {consensus_message}")
        
        candidates_data["candidates"].append(new_candidate)
        self.save_candidates(candidates_data)
        
        return True, new_candidate
    
    def remove_candidate(self, candidate_identifier):
        """Poista ehdokas - MULTINODE: Lähetä konsensusproposalina"""
        candidates_data = self.load_candidates()
        
        # Etsi ehdokas ID:llä tai nimellä
        candidate_to_remove = get_candidate_by_id_or_name(self.candidates_file, candidate_identifier)
        if not candidate_to_remove:
            return False, "Ehdokasta ei löydy"
        
        # MULTINODE: Lähetä poisto konsensusproposalina
        if self.enable_multinode:
            success, consensus_message = self._propose_candidate_change(
                "remove_candidate",
                candidate_to_remove,
                f"Remove candidate: {candidate_to_remove['basic_info']['name']['fi']}"
            )
            if not success:
                return False, f"Network rejected removal: {consensus_message}"
            print(f"🌐 {consensus_message}")
        
        candidate_id = candidate_to_remove["id"]
        initial_count = len(candidates_data["candidates"])
        candidates_data["candidates"] = [
            candidate for candidate in candidates_data["candidates"]
            if candidate["id"] != candidate_id
        ]
        
        removed_count = initial_count - len(candidates_data["candidates"])
        if removed_count > 0:
            self.save_candidates(candidates_data)
            return True, f"Poistettu ehdokas: {candidate_to_remove['basic_info']['name']['fi']}"
        else:
            return False, "Ehdokasta ei löytynyt"
    
    def update_candidate(self, candidate_identifier, name_fi=None, name_en=None, party=None, domain=None, is_active=None):
        """Päivitä ehdokas - MULTINODE: Lähetä konsensusproposalina"""
        candidates_data = self.load_candidates()
        updated = False
        
        # Etsi ehdokas
        candidate_to_update = None
        candidate_index = -1
        
        for i, candidate in enumerate(candidates_data["candidates"]):
            if (candidate["id"] == candidate_identifier or 
                candidate["basic_info"]["name"]["fi"] == candidate_identifier or
                candidate["basic_info"]["name"]["en"] == candidate_identifier):
                candidate_to_update = candidate
                candidate_index = i
                break
        
        if not candidate_to_update:
            return False, "Ehdokasta ei löydy"
        
        # Luo päivitysdata
        update_data = {
            "original_candidate": candidate_to_update.copy(),
            "updates": {}
        }
        
        # Päivitä kentät
        if name_fi is not None:
            candidates_data["candidates"][candidate_index]["basic_info"]["name"]["fi"] = name_fi
            update_data["updates"]["name_fi"] = name_fi
            updated = True
        
        if name_en is not None:
            candidates_data["candidates"][candidate_index]["basic_info"]["name"]["en"] = name_en
            update_data["updates"]["name_en"] = name_en
            updated = True
        
        if party is not None:
            candidates_data["candidates"][candidate_index]["basic_info"]["party"] = party
            update_data["updates"]["party"] = party
            updated = True
        
        if domain is not None:
            candidates_data["candidates"][candidate_index]["basic_info"]["domain"] = domain
            update_data["updates"]["domain"] = domain
            updated = True
        
        if is_active is not None:
            candidates_data["candidates"][candidate_index]["basic_info"]["is_active"] = is_active
            candidates_data["candidates"][candidate_index]["status"] = "active" if is_active else "inactive"
            update_data["updates"]["is_active"] = is_active
            updated = True
        
        if updated:
            candidates_data["candidates"][candidate_index]["basic_info"]["updated_at"] = datetime.now().isoformat()
            update_data["updates"]["updated_at"] = datetime.now().isoformat()
            
            # MULTINODE: Lähetä päivitys konsensusproposalina
            if self.enable_multinode:
                success, consensus_message = self._propose_candidate_change(
                    "update_candidate",
                    update_data,
                    f"Update candidate: {candidate_to_update['basic_info']['name']['fi']}"
                )
                if not success:
                    return False, f"Network rejected update: {consensus_message}"
                print(f"🌐 {consensus_message}")
            
            self.save_candidates(candidates_data)
            return True, f"Ehdokas päivitetty: {candidate_to_update['basic_info']['name']['fi']}"
        else:
            return False, "Ei muutoksia"
    
    def list_candidates(self, party_filter=None):
        """Listaa ehdokkaat"""
        candidates_data = self.load_candidates()
        candidates = candidates_data.get("candidates", [])
        
        if party_filter:
            candidates = [c for c in candidates if c["basic_info"]["party"] == party_filter]
        
        return candidates
    
    def get_candidate_stats(self):
        """Hae ehdokastilastot"""
        candidates_data = self.load_candidates()
        candidates = candidates_data.get("candidates", [])
        
        # Puolueet
        parties = set(c["basic_info"]["party"] for c in candidates)
        
        # Aktiiviset vs. passiiviset
        active_count = sum(1 for c in candidates if c["basic_info"]["is_active"])
        inactive_count = len(candidates) - active_count
        
        # Lataa vastaustilastot
        answers_file = Path(self.data_path) / "candidate_answers.json"
        candidates_with_answers = 0
        if answers_file.exists():
            answers_data = read_json_file(answers_file)
            candidates_with_answers = len(set(a["candidate_id"] for a in answers_data.get("answers", [])))
        
        stats = {
            "total_candidates": len(candidates),
            "parties": len(parties),
            "active_candidates": active_count,
            "inactive_candidates": inactive_count,
            "candidates_with_answers": candidates_with_answers,
            "answer_coverage": round((candidates_with_answers / len(candidates) * 100) if candidates else 0, 1)
        }
        
        # MULTINODE: Lisää verkontilastoja
        if self.enable_multinode and self.network_manager:
            network_stats = self.network_manager.get_network_stats()
            stats["network"] = {
                "node_id": self.node_identity.node_id,
                "peer_count": network_stats["peer_count"],
                "connection_status": network_stats["connection_status"]
            }
        
        return stats


@click.command()
@click.option('--election', required=False, help='Vaalin tunniste (valinnainen, käytetään configista)')
@click.option('--add', is_flag=True, help='Lisää uusi ehdokas')
@click.option('--remove', help='Poista ehdokas (ID tai nimi)')
@click.option('--update', help='Päivitä ehdokas (ID tai nimi)')
@click.option('--list', 'list_candidates', is_flag=True, help='Listaa kaikki ehdokkaat')
@click.option('--name-fi', help='Ehdokkaan nimi suomeksi')
@click.option('--name-en', help='Ehdokkaan nimi englanniksi')
@click.option('--party', help='Puolue')
@click.option('--domain', help='Alue/domain')
@click.option('--inactive', is_flag=True, help='Merkitse ehdokas epäaktiiviseksi')
@click.option('--active', is_flag=True, help='Merkitse ehdokas aktiiviseksi')
@click.option('--enable-multinode', is_flag=True, help='Ota multinode käyttöön')
@click.option('--bootstrap-debug', is_flag=True, help='Käytä debug-bootstrap peeritä')
def manage_candidates(election, add, remove, update, list_candidates, name_fi, name_en, party, domain, inactive, active, enable_multinode, bootstrap_debug):
    """Ehdokkaiden hallinta - MULTINODE VERSION
    
    Esimerkkejä:
        python manage_candidates.py --list  # Peruslistaus
        python manage_candidates.py --add --name-fi "Matti Meikäläinen" --party "Demo"  # Peruslisäys
        python manage_candidates.py --add --name-fi "Verkkoehdokas" --party "Testi" --enable-multinode  # Multinode-lisäys
        python manage_candidates.py --list --enable-multinode  # Listaus verkontilastoilla
    """
    
    # Hae election_id configista jos parametria ei annettu
    election_id = get_election_id(election)
    if not election_id:
        print("❌ Vaali-ID:tä ei annettu eikä config tiedostoa löydy.")
        print("💡 Käytä: --election VAALI_ID tai asenna järjestelmä ensin: python src/cli/install.py --first-install")
        return
    
    # MULTINODE: Tarkista saatavuus
    if enable_multinode and not MULTINODE_AVAILABLE:
        print("❌ Multinode requested but modules not available")
        click.confirm("Continue without multinode?", abort=True)
        enable_multinode = False
    
    manager = CandidateManager(
        election_id=election_id,
        enable_multinode=enable_multinode,
        bootstrap_debug=bootstrap_debug
    )
    
    if add:
        if not name_fi:
            print("❌ --name-fi vaaditaan uuden ehdokkaan lisäämiseksi")
            return
        
        # Aktiivisuustila
        is_active = True
        if inactive:
            is_active = False
        if active:
            is_active = True
        
        success, result = manager.add_candidate(
            name_fi=name_fi,
            name_en=name_en,
            party=party or "sitoutumaton",
            domain=domain or "yleinen",
            is_active=is_active
        )
        
        if success:
            print("✅ Ehdokas lisätty!")
            print(f"👤 Nimi: {result['basic_info']['name']['fi']}")
            print(f"🆔 ID: {result['id']}")
            print(f"🏛️  Puolue: {result['basic_info']['party']}")
            print(f"🎯 Alue: {result['basic_info']['domain']}")
            print(f"📊 Tila: {'Aktiivinen' if result['basic_info']['is_active'] else 'Epäaktiivinen'}")
        else:
            print(f"❌ {result}")
    
    elif remove:
        success, result = manager.remove_candidate(remove)
        if success:
            print(f"✅ {result}")
        else:
            print(f"❌ {result}")
    
    elif update:
        if not any([name_fi, name_en, party, domain, inactive, active]):
            print("❌ Anna vähintään yksi päivitettävä kenttä (--name-fi, --name-en, --party, --domain, --active, --inactive)")
            return
        
        # Aktiivisuustila
        is_active = None
        if inactive:
            is_active = False
        if active:
            is_active = True
        
        success, result = manager.update_candidate(
            candidate_identifier=update,
            name_fi=name_fi,
            name_en=name_en,
            party=party,
            domain=domain,
            is_active=is_active
        )
        
        if success:
            print(f"✅ {result}")
        else:
            print(f"❌ {result}")
    
    elif list_candidates:
        candidates = manager.list_candidates(party)
        stats = manager.get_candidate_stats()
        
        print(f"👑 REKISTERÖIDYT EHDOKKAAT - {election_id}")
        if enable_multinode:
            print(f"🌐 MULTINODE MODE - Node: {manager.node_identity.node_id if manager.node_identity else 'N/A'}")
        print("=" * 60)
        
        # Ryhmittele puolueittain
        parties = {}
        for candidate in candidates:
            party_name = candidate["basic_info"]["party"]
            if party_name not in parties:
                parties[party_name] = []
            parties[party_name].append(candidate)
        
        for party_name, party_candidates in parties.items():
            print(f"\n🏛️  PUOLUE: {party_name}")
            print("-" * 40)
            
            for candidate in party_candidates:
                basic_info = candidate["basic_info"]
                status_icon = "✅" if basic_info["is_active"] else "❌"
                signed_icon = "⚠️ " if candidate.get("status") != "signed" else "✅"
                
                print(f"   {status_icon} {basic_info['name']['fi']}")
                print(f"      🆔 {candidate['id']}")
                print(f"      {signed_icon} {candidate.get('status', 'AKTIIVINEN').upper()} | {signed_icon} EI ALLEKIRJOITETTU")
                print(f"      📝 Vastauksia: {candidate.get('answers_count', 0)}")
                print(f"      🎯 Alue: {basic_info['domain']}")
        
        print(f"\n📊 YHTEENVETO:")
        print(f"   👥 Ehdokkaita: {stats['total_candidates']}")
        print(f"   🏛️  Puolueita: {stats['parties']}")
        print(f"   📝 Vastanneita: {stats['candidates_with_answers']}")
        print(f"   📈 Vastauskattavuus: {stats['answer_coverage']}%")
        
        # MULTINODE: Näytä verkontilastot
        if enable_multinode and "network" in stats:
            print(f"\n🌐 VERKKOTILASTOT:")
            print(f"   🆔 Node ID: {stats['network']['node_id']}")
            print(f"   📡 Peerit: {stats['network']['peer_count']}")
            print(f"   🔗 Tila: {stats['network']['connection_status']}")
    
    else:
        print("❌ Anna komento: --add, --remove, --update tai --list")
        print("💡 Kokeile: python src/cli/manage_candidates.py --list")
        if MULTINODE_AVAILABLE:
            print("🌐 Multinode: python src/cli/manage_candidates.py --list --enable-multinode")


if __name__ == "__main__":
    manage_candidates()
