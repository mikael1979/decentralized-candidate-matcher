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
def voting_engine(election, start, results, compare, list_sessions):
    """Vaalikoneen ydin - käyttäjien vastausten keräys ja tulosten laskenta"""
    
    # Hae election_id configista jos parametria ei annettu
    election_id = get_election_id(election)
    if not election_id:
        print("❌ Vaali-ID:tä ei annettu eikä config tiedostoa löydy.")
        print("💡 Käytä: --election VAALI_ID tai asenna järjestelmä ensin: python src/cli/install.py --first-install")
        sys.exit(1)
    
    print(f"🗳️  VAALIKONE: {election_id}")
    print("=" * 50)
    
    if start:
        start_voting_session(election_id)
    elif results:
        show_results(election_id, results)
    elif compare:
        compare_candidates(election_id, compare)
    elif list_sessions:
        list_voting_sessions(election_id)
    else:
        print("❌ Anna komento: --start, --results, --compare tai --list-sessions")
        print("💡 Kokeile: python src/cli/voting_engine.py --start")


def start_voting_session(election_id):
    """Käynnistä uusi voting-sessio"""
    data_path = get_data_path(election_id)
    
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
    save_voting_session(election_id, session_id, user_answers, results)
    
    # Näytä tulokset
    show_results(election_id, session_id)


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
        candidate_name = candidate.get("name_fi", candidate.get("name_en", "Nimetön"))
        candidate_party = candidate.get("party", "sitoutumaton")
        
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
        
        # Laska prosentti
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


def save_voting_session(election_id, session_id, user_answers, results):
    """Tallenna voting-sessio"""
    sessions_path = Path(get_data_path(election_id)) / "voting_sessions.json"
    ensure_directory(sessions_path.parent)
    
    sessions_data = {"sessions": []}
    if sessions_path.exists():
        sessions_data = read_json_file(sessions_path)
    
    session_data = {
        "session_id": session_id,
        "election_id": election_id,
        "timestamp": datetime.now().isoformat(),
        "user_answers": user_answers,
        "results": results
    }
    
    sessions_data["sessions"].append(session_data)
    write_json_file(sessions_path, sessions_data)
    
    print(f"💾 Sessio tallennettu: {session_id}")


def show_results(election_id, session_id):
    """Näytä voting-session tulokset"""
    sessions_path = Path(get_data_path(election_id)) / "voting_sessions.json"
    
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
    
    print(f"\n🏆 TULOKSET - {session_id}")
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


def compare_candidates(election_id, session_id):
    """Vertaa ehdokkaita session perusteella"""
    # Toteutus myöhemmin
    print(f"🔍 Vertailu-toiminto tulossa myöhemmin...")
    print(f"   Vaali: {election_id}")
    print(f"   Sessio: {session_id}")


def list_voting_sessions(election_id):
    """Listaa kaikki voting-sessiot"""
    sessions_path = Path(get_data_path(election_id)) / "voting_sessions.json"
    
    if not sessions_path.exists():
        print(f"❌ Ei voting-sessioita vaalille: {election_id}")
        return
    
    sessions_data = read_json_file(sessions_path)
    sessions = sessions_data.get("sessions", [])
    
    print(f"📋 VOTING-SESSIOT - {election_id}")
    print("=" * 50)
    
    for session in sessions:
        session_id = session.get("session_id")
        timestamp = session.get("timestamp", "")
        answer_count = len(session.get("user_answers", {}))
        
        print(f"🆔 {session_id}")
        print(f"   📅 {timestamp}")
        print(f"   ❓ {answer_count} vastausta")
        print()


if __name__ == "__main__":
    voting_engine()
