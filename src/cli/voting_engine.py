#!/usr/bin/env python3
import click
import json
import sys
from pathlib import Path
from datetime import datetime

# Lisää src hakemisto Python-polkuun
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.file_utils import read_json_file, write_json_file, ensure_directory

def validate_answer_value(answer_value):
    """Tarkista että vastausarvo on validi (-5 - +5)"""
    try:
        value = int(answer_value)
        return -5 <= value <= 5
    except (ValueError, TypeError):
        return False

@click.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--start', is_flag=True, help='Aloita vaalikone')
@click.option('--results', help='Näytä tulokset (session-ID)')
@click.option('--compare', help='Vertaa ehdokkaita (session-ID)')
@click.option('--list-sessions', is_flag=True, help='Listaa kaikki voting-sessiot')
def voting_engine(election, start, results, compare, list_sessions):
    """Vaalikoneen ydin - käyttäjien vastausten keräys ja tulosten laskenta"""
    
    if start:
        start_voting_session(election)
    elif results:
        show_results(election, results)
    elif compare:
        compare_candidates(election, compare)
    elif list_sessions:
        list_voting_sessions(election)
    else:
        click.echo("💡 KÄYTTÖ:")
        click.echo("   --start          # Aloita uusi vaalikone")
        click.echo("   --results ID     # Näytä tulokset")
        click.echo("   --compare ID     # Vertaa ehdokkaita")
        click.echo("   --list-sessions  # Listaa kaikki sessiot")

def start_voting_session(election):
    """Aloita uusi vaalikonesessio"""
    click.echo(f"🗳️  VAALIKONE: {election}")
    click.echo("=" * 50)
    
    # Lataa kysymykset
    questions = load_questions(election)
    if not questions:
        click.echo("❌ Ei kysymyksiä saatavilla")
        return
    
    # Lataa ehdokkaat
    candidates = load_candidates(election)
    if not candidates:
        click.echo("❌ Ei ehdokkaita saatavilla")
        return
    
    click.echo(f"📝 Kysymyksiä: {len(questions)}")
    click.echo(f"👑 Ehdokkaita: {len(candidates)}")
    click.echo()
    
    # Kerää käyttäjän vastaukset
    user_answers = collect_user_answers(questions)
    
    if not user_answers:
        click.echo("❌ Et vastannut yhteenkään kysymykseen")
        return
    
    # Laske yhteensopivuus
    results = calculate_compatibility(user_answers, candidates)
    
    # Tallenna tulokset
    session_id = save_results(election, user_answers, results)
    
    # Näytä tulokset
    show_results_table(results, candidates)
    
    click.echo(f"\n🎯 VAALIKONE SUORITETTU!")
    click.echo(f"📊 Sessio ID: {session_id}")
    click.echo(f"💡 Käytä: python src/cli/voting_engine.py --results {session_id}")

def load_questions(election):
    """Lataa kysymykset"""
    questions_file = "data/runtime/questions.json"
    if not Path(questions_file).exists():
        return []
    
    data = read_json_file(questions_file, {"questions": []})
    return [q for q in data.get("questions", []) if q.get("content")]

def load_candidates(election):
    """Lataa ehdokkaat"""
    candidates_file = "data/runtime/candidates.json"
    if not Path(candidates_file).exists():
        return []
    
    data = read_json_file(candidates_file, {"candidates": []})
    return [c for c in data.get("candidates", []) if c.get("basic_info")]

def collect_user_answers(questions):
    """Kerää käyttäjän vastaukset kysymyksiin"""
    user_answers = {}
    
    click.echo("🤔 VASTA KYSYMYKSIIN (-5 ... +5)")
    click.echo("-" * 40)
    
    for i, question in enumerate(questions, 1):
        q_content = question["content"]
        q_id = question["local_id"]
        
        click.echo(f"\n{i}. {q_content['question']['fi']}")
        if "en" in q_content['question'] and q_content['question']['en'] and not q_content['question']['en'].startswith('[EN]'):
            click.echo(f"   EN: {q_content['question']['en']}")
        
        click.echo("   Asteikko: -5 (Täysin eri mieltä) ... +5 (Täysin samaa mieltä)")
        
        while True:
            try:
                answer = click.prompt("   Vastaus (-5 - +5)", type=int)
                if validate_answer_value(answer):
                    # KORJATTU: Kategorian käsittely
                    category = q_content.get('category', {})
                    if isinstance(category, dict):
                        category_text = category.get('fi', 'Yleinen')
                    else:
                        category_text = str(category)
                    
                    user_answers[q_id] = {
                        "question_id": q_id,
                        "answer_value": answer,
                        "question_text": q_content['question']['fi'],
                        "category": category_text
                    }
                    break
                else:
                    click.echo("   ❌ Vastauksen tulee olla välillä -5 - +5")
            except ValueError:
                click.echo("   ❌ Anna numero välillä -5 - +5")
    
    return user_answers

def calculate_compatibility(user_answers, candidates):
    """Laske yhteensopivuus käyttäjän ja ehdokkaiden välillä"""
    results = []
    
    for candidate in candidates:
        compatibility = calculate_candidate_compatibility(user_answers, candidate)
        results.append({
            "candidate_id": candidate["candidate_id"],
            "candidate_name": candidate["basic_info"]["name"]["fi"],
            "party": candidate["basic_info"].get("party", "Sitoutumaton"),
            "compatibility_score": compatibility["score"],
            "matching_answers": compatibility["matching"],
            "total_questions": compatibility["total"],
            "match_percentage": compatibility["percentage"]
        })
    
    # Järjestä parhaimman yhteensopivuuden mukaan
    results.sort(key=lambda x: x["compatibility_score"], reverse=True)
    return results

def calculate_candidate_compatibility(user_answers, candidate):
    """Laske yhteensopivuus yhden ehdokkaan kanssa"""
    candidate_answers = {ans["question_id"]: ans for ans in candidate.get("answers", [])}
    
    total_score = 0
    matching_answers = 0
    total_questions = len(user_answers)
    
    for q_id, user_answer in user_answers.items():
        if q_id in candidate_answers:
            cand_answer = candidate_answers[q_id]
            # Laske etäisyys (pienempi = parempi)
            distance = abs(user_answer["answer_value"] - cand_answer["answer_value"])
            # Muunna pisteeksi (10 - etäisyys)
            score = max(0, 10 - distance)
            total_score += score
            matching_answers += 1
    
    percentage = (matching_answers / total_questions * 100) if total_questions > 0 else 0
    
    return {
        "score": total_score,
        "matching": matching_answers,
        "total": total_questions,
        "percentage": percentage
    }

def show_results_table(results, candidates):
    """Näytä tulokset taulukkona"""
    click.echo("\n🏆 TULOKSET")
    click.echo("=" * 70)
    click.echo(f"{'Sija':<4} {'Ehdokas':<20} {'Puolue':<15} {'Pisteet':<8} {'Osumat':<8} {'%':<6}")
    click.echo("-" * 70)
    
    for i, result in enumerate(results[:10], 1):  # Näytä 10 parasta
        click.echo(f"{i:<4} {result['candidate_name']:<20} {result['party']:<15} "
                  f"{result['compatibility_score']:<8} {result['matching_answers']:<8} "
                  f"{result['match_percentage']:.1f}%")
    
    # Näytä yleiskuvaus
    if results:
        best = results[0]
        click.echo(f"\n🎯 PARAS YHTEENSOPIVUUS: {best['candidate_name']} ({best['party']})")
        click.echo(f"📊 Pisteet: {best['compatibility_score']} | Osumia: {best['matching_answers']}/{best['total_questions']}")

def save_results(election, user_answers, results):
    """Tallenna käyttäjän tulokset"""
    ensure_directory("data/runtime/voting_sessions")
    
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    results_file = f"data/runtime/voting_sessions/{session_id}.json"
    
    data = {
        "session_id": session_id,
        "election_id": election,
        "timestamp": datetime.now().isoformat(),
        "user_answers": user_answers,
        "results": results,
        "metadata": {
            "total_questions": len(user_answers),
            "total_candidates": len(results),
            "best_match": results[0] if results else None
        }
    }
    
    write_json_file(results_file, data)
    return session_id

def show_results(election, session_id):
    """Näytä tallennetut tulokset"""
    results_file = f"data/runtime/voting_sessions/{session_id}.json"
    
    if not Path(results_file).exists():
        click.echo(f"❌ Sessiota ei löydy: {session_id}")
        return
    
    data = read_json_file(results_file, {})
    candidates = load_candidates(election)
    
    click.echo(f"📊 VAALIKONEEN TULOKSET - Sessio {session_id}")
    click.echo("=" * 50)
    click.echo(f"📅 Aikaleima: {data.get('timestamp', 'N/A')}")
    click.echo(f"📝 Vastattuja kysymyksiä: {len(data.get('user_answers', {}))}")
    click.echo()
    
    show_results_table(data.get('results', []), candidates)

def compare_candidates(election, session_id):
    """Vertaa ehdokkaita yksityiskohtaisesti"""
    results_file = f"data/runtime/voting_sessions/{session_id}.json"
    
    if not Path(results_file).exists():
        click.echo(f"❌ Sessiota ei löydy: {session_id}")
        return
    
    data = read_json_file(results_file, {})
    user_answers = data.get('user_answers', {})
    candidates = load_candidates(election)
    
    click.echo(f"🔍 EHDOKKAIDEN VERTAILU - Sessio {session_id}")
    click.echo("=" * 50)
    
    # Näytä 3 parasta ehdokasta
    top_candidates = data.get('results', [])[:3]
    
    for i, candidate_result in enumerate(top_candidates, 1):
        candidate = next((c for c in candidates if c["candidate_id"] == candidate_result["candidate_id"]), None)
        if not candidate:
            continue
            
        click.echo(f"\n{i}. {candidate_result['candidate_name']} ({candidate_result['party']})")
        click.echo(f"   Yhteensopivuus: {candidate_result['compatibility_score']} pistettä")
        click.echo(f"   Vastausten osumia: {candidate_result['matching_answers']}/{candidate_result['total_questions']}")
        click.echo(f"   Osumaprosentti: {candidate_result['match_percentage']:.1f}%")
        
        # Näytä eroavaisuudet
        show_answer_differences(user_answers, candidate)

def show_answer_differences(user_answers, candidate):
    """Näytä vastauseroavaisuudet"""
    candidate_answers = {ans["question_id"]: ans for ans in candidate.get("answers", [])}
    differences = []
    
    for q_id, user_answer in user_answers.items():
        if q_id in candidate_answers:
            cand_answer = candidate_answers[q_id]
            diff = abs(user_answer["answer_value"] - cand_answer["answer_value"])
            if diff >= 3:  # Näytä vain suuret erot
                differences.append({
                    "question": user_answer["question_text"],
                    "user_answer": user_answer["answer_value"],
                    "candidate_answer": cand_answer["answer_value"],
                    "difference": diff
                })
    
    if differences:
        click.echo("   📋 SUURIMMAT EROAVUUDET:")
        for diff in differences[:3]:  # Näytä 3 suurinta eroa
            click.echo(f"      - {diff['question'][:50]}...")
            click.echo(f"        Sinä: {diff['user_answer']} | Ehdokas: {diff['candidate_answer']}")

def list_voting_sessions(election):
    """Listaa kaikki voting-sessiot"""
    sessions_dir = Path("data/runtime/voting_sessions")
    if not sessions_dir.exists():
        click.echo("❌ Ei voting-sessioita")
        return
    
    sessions = list(sessions_dir.glob("session_*.json"))
    if not sessions:
        click.echo("❌ Ei voting-sessioita")
        return
    
    click.echo(f"📋 VOTING-SESSIOT - {election}")
    click.echo("=" * 50)
    
    for session_file in sorted(sessions)[-10:]:  # Näytä 10 viimeisintä
        data = read_json_file(session_file, {})
        session_id = session_file.stem
        timestamp = data.get('timestamp', 'N/A')
        questions = len(data.get('user_answers', {}))
        
        click.echo(f"🆔 {session_id}")
        click.echo(f"   📅 {timestamp}")
        click.echo(f"   📝 {questions} kysymystä")
        
        if data.get('results'):
            best = data['results'][0]
            click.echo(f"   🏆 {best['candidate_name']} ({best['compatibility_score']} pistettä)")
        click.echo()

if __name__ == '__main__':
    voting_engine()
