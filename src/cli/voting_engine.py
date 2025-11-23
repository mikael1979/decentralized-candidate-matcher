#!/usr/bin/env python3
import click
import json
import sys
from pathlib import Path
from datetime import datetime

# Lisää src hakemisto Python-polkuun
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.file_utils import read_json_file, write_json_file, ensure_directory
from core.config_manager import get_election_id, get_data_path

# MULTINODE: Tuo uudet moduulit
try:
    from nodes.core.node_identity import NodeIdentity
    from nodes.core.network_manager import NetworkManager
    from nodes.protocols.consensus import ConsensusManager
    MULTINODE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Multinode modules not available: {e}")
    MULTINODE_AVAILABLE = False


class VotingSessionManager:
    """Voting session management with multinode support"""
    
    def __init__(self, election_id=None, enable_multinode=False):
        self.election_id = election_id or get_election_id()
        self.data_path = get_data_path(self.election_id)
        
        # MULTINODE: Alusta node-järjestelmä
        self.enable_multinode = enable_multinode
        self.node_identity = None
        self.network_manager = None
        self.consensus_manager = None
        
        if self.enable_multinode and MULTINODE_AVAILABLE:
            self._initialize_multinode()
    
    def _initialize_multinode(self):
        """Alustaa multinode-järjestelmän voting-sessioihin"""
        try:
            print("🌐 Alustetaan multinode-voting...")
            
            # Lataa olemassa oleva node identity tai luo uusi
            self.node_identity = self._load_or_create_node_identity()
            
            # Luo verkkomanageri
            self.network_manager = NetworkManager(self.node_identity)
            
            # Luo konsensusmanageri
            self.consensus_manager = ConsensusManager(self.network_manager)
            
            # Yhdistä verkkoon (tyhjät bootstrap-peerit voting-sessioille)
            self.network_manager.connect_to_network([])
            
            print(f"✅ Multinode voting alustettu: {self.node_identity.node_id}")
            
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
                identity = NodeIdentity(self.election_id, "voter")
                if identity.load_identity(latest_file.stem.replace("_identity", "")):
                    print(f"✅ Loaded existing node identity: {identity.node_id}")
                    return identity
            
            # Luo uusi identity voting-sessioita varten
            identity = NodeIdentity(
                election_id=self.election_id,
                node_type="voter", 
                node_name=f"voting_engine_{datetime.now().strftime('%H%M%S')}",
                domain="voting_sessions"
            )
            identity.save_identity()
            return identity
            
        except Exception as e:
            print(f"⚠️  Failed to load/create node identity: {e}")
            # Fallback: Luo uusi identity
            identity = NodeIdentity(self.election_id, "voter")
            identity.save_identity()
            return identity
    
    def _broadcast_voting_session(self, session_data):
        """Lähetä voting-sessio verkkoon multinode-tilassa"""
        if not self.enable_multinode or not self.network_manager:
            return
        
        try:
            # Lähetä voting-session tiedot verkkoon
            self.network_manager.broadcast_message("voting_session_completed", {
                "session_id": session_data["session_id"],
                "election_id": self.election_id,
                "timestamp": session_data["timestamp"],
                "answer_count": len(session_data["user_answers"]),
                "node_id": self.node_identity.node_id
            })
            
            print(f"📤 Voting session broadcast to network: {session_data['session_id']}")
            
        except Exception as e:
            print(f"⚠️  Failed to broadcast voting session: {e}")
    
    def _sync_voting_data(self):
        """Synkronoi voting-data verkosta multinode-tilassa"""
        if not self.enable_multinode or not self.network_manager:
            return
        
        try:
            # Kysy verkosta uusimmat voting-sessiot
            self.network_manager.broadcast_message("voting_data_request", {
                "election_id": self.election_id,
                "request_type": "session_list",
                "node_id": self.node_identity.node_id
            })
            
            print("🔄 Syncing voting data from network...")
            
        except Exception as e:
            print(f"⚠️  Failed to sync voting data: {e}")


def validate_answer_value(answer_value):
    """Tarkista että vastausarvo on validi (-5 - +5)"""
    try:
        value = int(answer_value)
        return -5 <= value <= 5
    except (ValueError, TypeError):
        return False


@click.command()
@click.option('--election', required=False, help='Vaalin tunniste (valinnainen, käytetään configista jos ei anneta)')
@click.option('--start', is_flag=True, help='Aloita vaalikone')
@click.option('--results', help='Näytä tulokset (session-ID)')
@click.option('--compare', help='Vertaa ehdokkaita (session-ID)')
@click.option('--list-sessions', is_flag=True, help='Listaa kaikki voting-sessiot')
@click.option('--enable-multinode', is_flag=True, help='Ota multinode käyttöön')
@click.option('--network-stats', is_flag=True, help='Näytä verkontilastot')
def voting_engine(election, start, results, compare, list_sessions, enable_multinode, network_stats):
    """Vaalikoneen ydin - multinode-tuki voting-sessioille"""
    
    # Hae election_id configista jos parametria ei annettu
    election_id = get_election_id(election)
    if not election_id:
        print("❌ Vaali-ID:tä ei annettu eikä config tiedostoa löydy.")
        print("💡 Käytä: --election VAALI_ID tai asenna järjestelmä ensin: python src/cli/install.py --first-install")
        sys.exit(1)
    
    # MULTINODE: Tarkista saatavuus
    if enable_multinode and not MULTINODE_AVAILABLE:
        print("❌ Multinode requested but modules not available")
        click.confirm("Continue without multinode?", abort=True)
        enable_multinode = False
    
    # Alusta voting manager
    voting_manager = VotingSessionManager(election_id, enable_multinode)
    
    print(f"🗳️  VAALIKONE: {election_id}")
    if enable_multinode:
        print(f"🌐 MULTINODE MODE - Node: {voting_manager.node_identity.node_id if voting_manager.node_identity else 'N/A'}")
    print("=" * 50)
    
    if start:
        start_voting_session(voting_manager)
    elif results:
        show_results(voting_manager, results)
    elif compare:
        compare_candidates(voting_manager, compare)
    elif list_sessions:
        list_voting_sessions(voting_manager)
    elif network_stats and enable_multinode:
        show_network_stats(voting_manager)
    else:
        print("❌ Anna komento: --start, --results, --compare, --list-sessions tai --network-stats")
        print("💡 Kokeile: python src/cli/voting_engine.py --start")
        if MULTINODE_AVAILABLE:
            print("🌐 Multinode: python src/cli/voting_engine.py --start --enable-multinode")


def start_voting_session(voting_manager):
    """Käynnistä uusi voting-sessio multinode-tuella"""
    election_id = voting_manager.election_id
    data_path = voting_manager.data_path
    
    # Lataa kysymykset
    questions_file = Path(data_path) / "questions.json"
    if not questions_file.exists():
        print(f"❌ Kysymyksiä ei löydy vaalille: {election_id}")
        print("💡 Lisää kysymyksiä ensin: python src/cli/manage_questions.py --election {election_id} --add")
        return
    
    questions_data = read_json_file(questions_file)
    questions = questions_data.get("questions", [])
    
    if not questions:
        print("❌ Ei kysymyksiä saatavilla.")
        return
    
    # Lataa ehdokkaat
    candidates_file = Path(data_path) / "candidates.json"
    candidates_data = read_json_file(candidates_file)
    candidates = candidates_data.get("candidates", [])
    
    if not candidates:
        print("❌ Ei ehdokkaita saatavilla.")
        return
    
    print(f"📝 Kysymyksiä: {len(questions)}")
    print(f"👑 Ehdokkaita: {len(candidates)}")
    
    # MULTINODE: Synkronoi data verkosta
    if voting_manager.enable_multinode:
        voting_manager._sync_voting_data()
    
    print()
    print("🤔 VASTA KYSYMYKSIIN (-5 ... +5)")
    print("-" * 40)
    
    user_answers = {}
    
    for i, question in enumerate(questions, 1):
        question_id = question.get("id", f"q_{i}")
        question_text = question.get("question_fi", f"Kysymys {i}")
        category = question.get("category", "Yleinen")
        
        print(f"\n{i}. {question_text}")
        print(f"   Kategoria: {category}")
        print(f"   Asteikko: -5 (Täysin eri mieltä) ... +5 (Täysin samaa mieltä)")
        
        while True:
            try:
                answer = input("   Vastaus (-5 - +5): ").strip()
                if validate_answer_value(answer):
                    user_answers[question_id] = int(answer)
                    break
                else:
                    print("   ❌ Virheellinen arvo! Käytä lukua -5 ja +5 välillä.")
            except KeyboardInterrupt:
                print("\n\n❌ Voting keskeytetty.")
                return
    
    # Laske tulokset
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    results = calculate_results(election_id, user_answers, session_id)
    
    # Tallenna sessio
    save_voting_session(voting_manager, session_id, user_answers, results)
    
    # MULTINODE: Lähetä sessio verkkoon
    if voting_manager.enable_multinode:
        session_data = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "user_answers": user_answers
        }
        voting_manager._broadcast_voting_session(session_data)
    
    # Näytä tulokset
    show_results(voting_manager, session_id)


def calculate_results(election_id, user_answers, session_id):
    """Laske ehdokkaiden yhteensopivuus"""
    data_path = get_data_path(election_id)
    
    # Lataa ehdokkaat ja vastaukset
    candidates_file = Path(data_path) / "candidates.json"
    answers_file = Path(data_path) / "candidate_answers.json"
    
    candidates_data = read_json_file(candidates_file)
    answers_data = read_json_file(answers_file)
    
    candidates = candidates_data.get("candidates", [])
    candidate_answers = answers_data.get("answers", [])
    
    results = []
    
    for candidate in candidates:
        candidate_id = candidate.get("id")
        basic_info = candidate.get("basic_info", {})
        name_info = basic_info.get("name", {})
        candidate_name = name_info.get("fi", name_info.get("en", "Nimetön"))
        candidate_party = basic_info.get("party", "sitoutumaton")
        
        # Etsi ehdokkaan vastaukset
        c_answers = {}
        for answer in candidate_answers:
            if answer.get("candidate_id") == candidate_id:
                c_answers[answer.get("question_id")] = {
                    "value": answer.get("value", 0),
                    "confidence": answer.get("confidence", 1)
                }
        
        # Laske pisteet
        total_score = 0
        matches = 0
        
        for q_id, user_answer in user_answers.items():
            if q_id in c_answers:
                candidate_answer = c_answers[q_id]["value"]
                confidence = c_answers[q_id]["confidence"]
                
                # Laske etäisyys (0-10 asteikolla) ja muunna pisteiksi
                distance = abs(user_answer - candidate_answer)
                max_distance = 10  # -5 to +5 = 10 units
                
                # Pisteet: 10 - etäisyys, skaalattu luottamuksella
                question_score = (10 - distance) * (confidence / 5.0)
                total_score += question_score
                matches += 1
        
        # Laske prosentti
        percentage = (matches / len(user_answers)) * 100 if user_answers else 0
        
        results.append({
            "candidate_id": candidate_id,
            "name": candidate_name,
            "party": candidate_party,
            "score": round(total_score, 1),
            "matches": matches,
            "percentage": round(percentage, 1)
        })
    
    # Järjestä tulokset
    results.sort(key=lambda x: x["score"], reverse=True)
    
    return results


def save_voting_session(voting_manager, session_id, user_answers, results):
    """Tallenna voting-sessio"""
    sessions_path = Path(voting_manager.data_path) / "voting_sessions.json"
    ensure_directory(sessions_path.parent)
    
    sessions_data = {"sessions": []}
    if sessions_path.exists():
        sessions_data = read_json_file(sessions_path)
    
    session_data = {
        "session_id": session_id,
        "election_id": voting_manager.election_id,
        "timestamp": datetime.now().isoformat(),
        "user_answers": user_answers,
        "results": results,
        "node_id": voting_manager.node_identity.node_id if voting_manager.node_identity else "local"
    }
    
    sessions_data["sessions"].append(session_data)
    write_json_file(sessions_path, sessions_data)
    
    print(f"💾 Sessio tallennettu: {session_id}")


def show_results(voting_manager, session_id):
    """Näytä voting-session tulokset"""
    sessions_path = Path(voting_manager.data_path) / "voting_sessions.json"
    
    if not sessions_path.exists():
        print(f"❌ Sessionta ei löydy: {session_id}")
        return
    
    sessions_data = read_json_file(sessions_path)
    target_session = None
    
    for session in sessions_data.get("sessions", []):
        if session.get("session_id") == session_id:
            target_session = session
            break
    
    if not target_session:
        print(f"❌ Sessionta ei löydy: {session_id}")
        return
    
    results = target_session.get("results", [])
    node_id = target_session.get("node_id", "local")
    
    print(f"\n🏆 TULOKSET - {session_id}")
    if node_id != "local":
        print(f"🌐 Node: {node_id}")
    print("=" * 70)
    print(f"{'Sija':<4} {'Ehdokas':<20} {'Puolue':<15} {'Pisteet':<8} {'Osumat':<8} {'%':<6}")
    print("-" * 70)
    
    for i, result in enumerate(results, 1):
        print(f"{i:<4} {result['name']:<20} {result['party']:<15} {result['score']:<8} {result['matches']:<8} {result['percentage']:<6.1f}%")
    
    if results:
        best_match = results[0]
        total_questions = len(target_session.get("user_answers", {}))
        print(f"\n🎯 PARAS YHTEENSOPIVUUS: {best_match['name']} ({best_match['party']})")
        print(f"📊 Pisteet: {best_match['score']} | Osumia: {best_match['matches']}/{total_questions}")
    
    print(f"\n🎯 VAALIKONE SUORITETTU!")
    print(f"📊 Sessio ID: {session_id}")
    print(f"💡 Käytä: python src/cli/voting_engine.py --results {session_id}")
    
    # MULTINODE: Näytä verkontilastot
    if voting_manager.enable_multinode and voting_manager.network_manager:
        stats = voting_manager.network_manager.get_network_stats()
        print(f"🌐 Verkko: {stats['peer_count']} peeriä | Tila: {stats['connection_status']}")


def compare_candidates(voting_manager, session_id):
    """Vertaa ehdokkaita session perusteella"""
    print(f"🔍 Vertailu-toiminto tulossa myöhemmin...")
    print(f"   Vaali: {voting_manager.election_id}")
    print(f"   Sessio: {session_id}")
    
    # MULTINODE: Tuleva ominaisuus - vertaile eri nodejen tuloksia
    if voting_manager.enable_multinode:
        print("   🌐 Multinode-vertailu: Käytössä")


def list_voting_sessions(voting_manager):
    """Listaa kaikki voting-sessiot multinode-tilastoilla"""
    sessions_path = Path(voting_manager.data_path) / "voting_sessions.json"
    
    if not sessions_path.exists():
        print(f"❌ Ei voting-sessioita vaalille: {voting_manager.election_id}")
        return
    
    sessions_data = read_json_file(sessions_path)
    sessions = sessions_data.get("sessions", [])
    
    # Laske tilastot
    total_sessions = len(sessions)
    node_sessions = {}
    
    for session in sessions:
        node_id = session.get("node_id", "local")
        if node_id not in node_sessions:
            node_sessions[node_id] = 0
        node_sessions[node_id] += 1
    
    print(f"📋 VOTING-SESSIOT - {voting_manager.election_id}")
    if voting_manager.enable_multinode:
        print(f"🌐 MULTINODE: {len(node_sessions)} eri nodea")
    print("=" * 50)
    
    for session in sessions:
        session_id = session.get("session_id")
        timestamp = session.get("timestamp", "")
        answer_count = len(session.get("user_answers", {}))
        node_id = session.get("node_id", "local")
        
        node_icon = "🌐" if node_id != "local" else "💻"
        print(f"{node_icon} {session_id}")
        print(f"   📅 {timestamp}")
        print(f"   ❓ {answer_count} vastausta")
        if node_id != "local":
            print(f"   🆔 Node: {node_id}")
        print()
    
    # MULTINODE: Näytä tilastot
    if voting_manager.enable_multinode:
        print("📊 SESSIO-TILASTOT:")
        for node_id, count in node_sessions.items():
            print(f"   {node_id}: {count} sessiota")


def show_network_stats(voting_manager):
    """Näytä verkontilastot multinode-tilassa"""
    if not voting_manager.enable_multinode or not voting_manager.network_manager:
        print("❌ Multinode ei käytössä")
        return
    
    stats = voting_manager.network_manager.get_network_stats()
    
    print(f"🌐 VERKONTILASTOT - {voting_manager.election_id}")
    print("=" * 40)
    print(f"🆔 Node ID: {stats['node_id']}")
    print(f"📡 Peerit: {stats['peer_count']}")
    print(f"🔗 Tila: {stats['connection_status']}")
    print(f"📤 Lähetetyt viestit: {stats['messages_sent']}")
    print(f"📥 Vastaanotetut viestit: {stats['messages_received']}")
    print(f"🔌 Yhteysyritykset: {stats['connection_attempts']}")
    
    # Näytä konsensustilastot jos saatavilla
    if voting_manager.consensus_manager:
        consensus_stats = voting_manager.consensus_manager.get_consensus_stats()
        print(f"\n🤝 KONSENSUS-TILASTOT:")
        print(f"   📋 Proposalit: {consensus_stats['proposals_created']}")
        print(f"   ✅ Saavutetut konsensukset: {consensus_stats['consensus_reached']}")
        print(f"   ❌ Epäonnistuneet: {consensus_stats['consensus_failed']}")
        print(f"   ⏳ Aktiiviset: {consensus_stats['active_proposals']}")


if __name__ == "__main__":
    voting_engine()
