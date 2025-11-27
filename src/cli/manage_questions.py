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

from core import get_election_id, get_data_path
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


class QuestionManager:
    """Kysymysten hallinta config-järjestelmän kanssa - MULTINODE VERSION"""
    
    def __init__(self, election_id=None, enable_multinode=False, bootstrap_debug=False):
        self.election_id = election_id or get_election_id()
        self.data_path = get_data_path(self.election_id)
        self.questions_file = Path(self.data_path) / "questions.json"
        
        # MULTINODE: Alusta node-järjestelmä
        self.enable_multinode = enable_multinode
        self.bootstrap_debug = bootstrap_debug
        self.node_identity = None
        self.network_manager = None
        self.consensus_manager = None
        
        if self.enable_multinode and MULTINODE_AVAILABLE:
            self._initialize_multinode()
    
    def _initialize_multinode(self):
        """Alustaa multinode-järjestelmän kysymysten hallintaan"""
        try:
            print("🌐 Alustetaan multinode-kysymysten hallinta...")
            
            # Lataa olemassa oleva node identity tai luo uusi
            self.node_identity = self._load_or_create_node_identity()
            
            # Luo verkkomanageri
            self.network_manager = NetworkManager(self.node_identity)
            
            # Luo konsensusmanageri
            self.consensus_manager = ConsensusManager(self.network_manager)
            
            # Yhdistä verkkoon
            bootstrap_peers = self._get_bootstrap_peers()
            self.network_manager.connect_to_network(bootstrap_peers)
            
            print(f"✅ Multinode kysymysten hallinta alustettu: {self.node_identity.node_id}")
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
                node_name=f"question_manager_{self.election_id}",
                domain="question_management"
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
            print("🔧 DEBUG: Using debug bootstrap for question management")
            # Luo mock-peerit debug-tilassa
            debug_peers = []
            for i in range(2):
                peer = NodeIdentity(
                    election_id=self.election_id,
                    node_type="coordinator",
                    node_name=f"debug_qm_peer_{i+1}",
                    domain="debug_questions"
                )
                debug_peers.append(peer)
            return debug_peers
        else:
            print("🔧 Using empty bootstrap peers for question management")
            return []
    
    def _propose_question_change(self, action, question_data, justification):
        """Lähetä kysymysmuutos konsensusproposalina verkkoon"""
        if not self.enable_multinode or not self.consensus_manager:
            return True, "Multinode not enabled - change applied locally"
        
        try:
            proposal_data = {
                "action": action,
                "question_data": question_data,
                "justification": justification,
                "proposer": self.node_identity.node_id,
                "timestamp": datetime.now().isoformat()
            }
            
            proposal_id = self.consensus_manager.create_proposal(
                "question_management",
                proposal_data,
                timeout_seconds=30
            )
            
            print(f"📤 Question change proposed to network: {proposal_id}")
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
            return True, "Fallback: Change applied locally"
    
    def load_questions(self):
        """Lataa kysymykset"""
        if not self.questions_file.exists():
            return {"questions": []}
        return read_json_file(self.questions_file)
    
    def save_questions(self, questions_data):
        """Tallenna kysymykset"""
        ensure_directory(self.questions_file.parent)
        write_json_file(self.questions_file, questions_data)
    
    def add_question(self, question_fi, category="Yleinen", question_en=None, elo_rating=1000):
        """Lisää uusi kysymys - MULTINODE: Lähetä konsensusproposalina"""
        questions_data = self.load_questions()
        
        # Tarkista onko kysymys jo olemassa
        for question in questions_data["questions"]:
            if question.get("question_fi") == question_fi:
                return False, "Kysymys samalla tekstillä on jo olemassa"
        
        # Luo uusi kysymys
        question_id = f"q_{uuid.uuid4().hex[:8]}"
        new_question = {
            "id": question_id,
            "question_fi": question_fi,
            "question_en": question_en or question_fi,
            "category": category,
            "elo_rating": elo_rating,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # MULTINODE: Lähetä muutos konsensusproposalina
        if self.enable_multinode:
            success, consensus_message = self._propose_question_change(
                "add_question",
                new_question,
                f"Add new question: {question_fi}"
            )
            if not success:
                return False, f"Network rejected question: {consensus_message}"
            print(f"🌐 {consensus_message}")
        
        questions_data["questions"].append(new_question)
        self.save_questions(questions_data)
        
        return True, new_question
    
    def remove_question(self, question_identifier):
        """Poista kysymys - MULTINODE: Lähetä konsensusproposalina"""
        questions_data = self.load_questions()
        
        # Etsi kysymys ID:llä tai tekstillä
        question_to_remove = None
        for question in questions_data["questions"]:
            if (question["id"] == question_identifier or 
                question["question_fi"] == question_identifier):
                question_to_remove = question
                break
        
        if not question_to_remove:
            return False, "Kysymystä ei löydy"
        
        # MULTINODE: Lähetä poisto konsensusproposalina
        if self.enable_multinode:
            success, consensus_message = self._propose_question_change(
                "remove_question",
                question_to_remove,
                f"Remove question: {question_to_remove['question_fi']}"
            )
            if not success:
                return False, f"Network rejected removal: {consensus_message}"
            print(f"🌐 {consensus_message}")
        
        initial_count = len(questions_data["questions"])
        questions_data["questions"] = [
            question for question in questions_data["questions"]
            if question["id"] != question_to_remove["id"]
        ]
        
        removed_count = initial_count - len(questions_data["questions"])
        if removed_count > 0:
            self.save_questions(questions_data)
            return True, f"Poistettu kysymys: {question_to_remove['question_fi']}"
        else:
            return False, "Kysymystä ei löytynyt"
    
    def update_question(self, question_identifier, question_fi=None, question_en=None, category=None, elo_rating=None):
        """Päivitä kysymys - MULTINODE: Lähetä konsensusproposalina"""
        questions_data = self.load_questions()
        updated = False
        
        # Etsi kysymys
        question_to_update = None
        question_index = -1
        
        for i, question in enumerate(questions_data["questions"]):
            if (question["id"] == question_identifier or 
                question["question_fi"] == question_identifier):
                question_to_update = question
                question_index = i
                break
        
        if not question_to_update:
            return False, "Kysymystä ei löydy"
        
        # Luo päivitysdata
        update_data = {
            "original_question": question_to_update.copy(),
            "updates": {}
        }
        
        # Päivitä kentät
        if question_fi is not None:
            questions_data["questions"][question_index]["question_fi"] = question_fi
            update_data["updates"]["question_fi"] = question_fi
            updated = True
        
        if question_en is not None:
            questions_data["questions"][question_index]["question_en"] = question_en
            update_data["updates"]["question_en"] = question_en
            updated = True
        
        if category is not None:
            questions_data["questions"][question_index]["category"] = category
            update_data["updates"]["category"] = category
            updated = True
        
        if elo_rating is not None:
            questions_data["questions"][question_index]["elo_rating"] = elo_rating
            update_data["updates"]["elo_rating"] = elo_rating
            updated = True
        
        if updated:
            questions_data["questions"][question_index]["updated_at"] = datetime.now().isoformat()
            update_data["updates"]["updated_at"] = datetime.now().isoformat()
            
            # MULTINODE: Lähetä päivitys konsensusproposalina
            if self.enable_multinode:
                success, consensus_message = self._propose_question_change(
                    "update_question",
                    update_data,
                    f"Update question: {question_to_update['question_fi']}"
                )
                if not success:
                    return False, f"Network rejected update: {consensus_message}"
                print(f"🌐 {consensus_message}")
            
            self.save_questions(questions_data)
            return True, f"Kysymys päivitetty: {question_to_update['question_fi']}"
        else:
            return False, "Ei muutoksia"
    
    def list_questions(self, category_filter=None):
        """Listaa kysymykset"""
        questions_data = self.load_questions()
        questions = questions_data.get("questions", [])
        
        if category_filter:
            questions = [q for q in questions if q["category"] == category_filter]
        
        return questions
    
    def get_question_stats(self):
        """Hae kysymystilastot"""
        questions_data = self.load_questions()
        questions = questions_data.get("questions", [])
        
        # Kategoriat
        categories = {}
        for question in questions:
            category = question["category"]
            categories[category] = categories.get(category, 0) + 1
        
        # ELO-jakauma
        elo_ratings = [q["elo_rating"] for q in questions if "elo_rating" in q]
        avg_elo = sum(elo_ratings) / len(elo_ratings) if elo_ratings else 1000
        
        stats = {
            "total_questions": len(questions),
            "categories": categories,
            "average_elo": round(avg_elo, 1),
            "min_elo": min(elo_ratings) if elo_ratings else 1000,
            "max_elo": max(elo_ratings) if elo_ratings else 1000
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
@click.option('--add', is_flag=True, help='Lisää uusi kysymys')
@click.option('--remove', help='Poista kysymys (ID tai teksti)')
@click.option('--update', help='Päivitä kysymys (ID tai teksti)')
@click.option('--list', 'list_questions', is_flag=True, help='Listaa kaikki kysymykset')
@click.option('--question-fi', help='Kysymys suomeksi')
@click.option('--question-en', help='Kysymys englanniksi')
@click.option('--category', help='Kysymyksen kategoria')
@click.option('--elo-rating', type=int, help='ELO-luokitus')
@click.option('--enable-multinode', is_flag=True, help='Ota multinode käyttöön')
@click.option('--bootstrap-debug', is_flag=True, help='Käytä debug-bootstrap peeritä')
def manage_questions(election, add, remove, update, list_questions, question_fi, question_en, category, elo_rating, enable_multinode, bootstrap_debug):
    """Kysymysten hallinta - MULTINODE VERSION
    
    Esimerkkejä:
        python manage_questions.py --list  # Peruslistaus
        python manage_questions.py --add --question-fi "Uusi kysymys?" --category "Testi"  # Peruslisäys
        python manage_questions.py --add --question-fi "Verkkokysymys?" --enable-multinode  # Multinode-lisäys
        python manage_questions.py --list --enable-multinode  # Listaus verkontilastoilla
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
    
    manager = QuestionManager(
        election_id=election_id,
        enable_multinode=enable_multinode,
        bootstrap_debug=bootstrap_debug
    )
    
    if add:
        if not question_fi:
            print("❌ --question-fi vaaditaan uuden kysymyksen lisäämiseksi")
            return
        
        success, result = manager.add_question(
            question_fi=question_fi,
            question_en=question_en,
            category=category or "Yleinen",
            elo_rating=elo_rating or 1000
        )
        
        if success:
            print("✅ Kysymys lisätty!")
            print(f"❓ {result['question_fi']}")
            print(f"🆔 ID: {result['id']}")
            print(f"📁 Kategoria: {result['category']}")
            print(f"🎯 ELO-luokitus: {result['elo_rating']}")
        else:
            print(f"❌ {result}")
    
    elif remove:
        success, result = manager.remove_question(remove)
        if success:
            print(f"✅ {result}")
        else:
            print(f"❌ {result}")
    
    elif update:
        if not any([question_fi, question_en, category, elo_rating]):
            print("❌ Anna vähintään yksi päivitettävä kenttä (--question-fi, --question-en, --category, --elo-rating)")
            return
        
        success, result = manager.update_question(
            question_identifier=update,
            question_fi=question_fi,
            question_en=question_en,
            category=category,
            elo_rating=elo_rating
        )
        
        if success:
            print(f"✅ {result}")
        else:
            print(f"❌ {result}")
    
    elif list_questions:
        questions = manager.list_questions(category)
        stats = manager.get_question_stats()
        
        print(f"📝 KYSYMYSLISTA - {election_id}")
        if enable_multinode:
            print(f"🌐 MULTINODE MODE - Node: {manager.node_identity.node_id if manager.node_identity else 'N/A'}")
        print("=" * 50)
        
        # Ryhmittele kategorioittain
        categories = {}
        for question in questions:
            cat = question["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(question)
        
        for category_name, category_questions in categories.items():
            print(f"\n📁 KATEGORIA: {category_name}")
            print("-" * 40)
            
            for i, question in enumerate(category_questions, 1):
                print(f"{i}. [{question['id']}] {question['question_fi']}")
                if question.get('question_en') and question['question_en'] != question['question_fi']:
                    print(f"   EN: {question['question_en']}")
                print(f"   🎯 ELO-luokitus: {question['elo_rating']}")
        
        print(f"\n📊 YHTEENVETO:")
        print(f"   ❓ Kysymyksiä: {stats['total_questions']}")
        print(f"   📁 Kategorioita: {len(stats['categories'])}")
        print(f"   📈 Keskim. ELO: {stats['average_elo']}")
        for cat, count in stats['categories'].items():
            print(f"      - {cat}: {count} kysymystä")
        
        # MULTINODE: Näytä verkontilastot
        if enable_multinode and "network" in stats:
            print(f"\n🌐 VERKKOTILASTOT:")
            print(f"   🆔 Node ID: {stats['network']['node_id']}")
            print(f"   📡 Peerit: {stats['network']['peer_count']}")
            print(f"   🔗 Tila: {stats['network']['connection_status']}")
    
    else:
        print("❌ Anna komento: --add, --remove, --update tai --list")
        print("💡 Kokeile: python src/cli/manage_questions.py --list")
        if MULTINODE_AVAILABLE:
            print("🌐 Multinode: python src/cli/manage_questions.py --list --enable-multinode")


if __name__ == "__main__":
    manage_questions()
