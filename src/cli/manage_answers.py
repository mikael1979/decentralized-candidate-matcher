#!/usr/bin/env python3
import click
import json
import sys
import os
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

@click.group()
def manage_answers():
    """Ehdokkaiden vastausten hallinta"""
    pass

@manage_answers.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--candidate-id', required=True, help='Ehdokkaan tunniste')
@click.option('--question-id', required=True, help='Kysymyksen tunniste')
@click.option('--answer', type=click.IntRange(-5, 5), required=True, help='Vastaus (-5 - +5)')
@click.option('--confidence', type=click.IntRange(1, 5), default=3, help='Varmuus taso (1-5)')
@click.option('--explanation-fi', help='Perustelu suomeksi')
@click.option('--explanation-en', help='Perustelu englanniksi')
@click.option('--explanation-sv', help='Perustelu ruotsiksi')
def add(election, candidate_id, question_id, answer, confidence, explanation_fi, explanation_en, explanation_sv):
    """Lisää ehdokkaan vastaus kysymykseen"""
    
    # Tarkista että ehdokas on olemassa
    candidates_file = f"data/runtime/candidates.json"
    if not os.path.exists(candidates_file):
        click.echo("❌ Ehdokasrekisteriä ei ole vielä luotu")
        return
    
    with open(candidates_file, 'r', encoding='utf-8') as f:
        candidates_data = json.load(f)
    
    candidate = next((c for c in candidates_data["candidates"] if c["candidate_id"] == candidate_id), None)
    if not candidate:
        click.echo(f"❌ Ehdokasta '{candidate_id}' ei löydy")
        click.echo("💡 Käytä: python src/cli/manage_candidates.py --election Jumaltenvaalit2026 --list")
        return
    
    # Tarkista että kysymys on olemassa
    questions_file = f"data/runtime/questions.json"
    if not os.path.exists(questions_file):
        click.echo("❌ Kysymysrekisteriä ei ole vielä luotu")
        return
    
    with open(questions_file, 'r', encoding='utf-8') as f:
        questions_data = json.load(f)
    
    question = next((q for q in questions_data["questions"] if q["local_id"] == question_id), None)
    if not question:
        click.echo(f"❌ Kysymystä '{question_id}' ei löydy")
        click.echo("💡 Käytä: python src/cli/manage_questions.py --election Jumaltenvaalit2026 --list")
        return
    
    # Luo tai päivitä vastaus
    if "answers" not in candidate:
        candidate["answers"] = []
    
    # Tarkista onko vastaus jo olemassa
    existing_answer = next((a for a in candidate["answers"] if a["question_id"] == question_id), None)
    
    if existing_answer:
        # Päivitä olemassa oleva vastaus
        existing_answer["answer_value"] = answer
        existing_answer["confidence"] = confidence
        existing_answer["last_updated"] = datetime.now().isoformat()
        
        if explanation_fi:
            existing_answer["explanation"]["fi"] = explanation_fi
        if explanation_en:
            existing_answer["explanation"]["en"] = explanation_en
        if explanation_sv:
            existing_answer["explanation"]["sv"] = explanation_sv
            
        action = "päivitetty"
    else:
        # Luo uusi vastaus
        new_answer = {
            "question_id": question_id,
            "answer_value": answer,
            "confidence": confidence,
            "explanation": {
                "fi": explanation_fi or "",
                "en": explanation_en or "",
                "sv": explanation_sv or ""
            },
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        candidate["answers"].append(new_answer)
        action = "lisätty"
    
    # Tallenna
    with open(candidates_file, 'w', encoding='utf-8') as f:
        json.dump(candidates_data, f, indent=2, ensure_ascii=False)
    
    click.echo(f"✅ Vastaus {action}: {candidate_id} → {question_id}")
    click.echo(f"📊 Arvo: {answer}/5, Varmuus: {confidence}/5")
    if explanation_fi:
        click.echo(f"💬 Perustelu: {explanation_fi}")

@manage_answers.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--candidate-id', help='Näytä tietyn ehdokkaan vastaukset')
@click.option('--question-id', help='Näytä tietyn kysymyksen vastaukset')
def list(election, candidate_id, question_id):
    """Listaa ehdokkaiden vastaukset"""
    
    candidates_file = f"data/runtime/candidates.json"
    questions_file = f"data/runtime/questions.json"
    
    if not os.path.exists(candidates_file):
        click.echo("❌ Ehdokasrekisteriä ei ole vielä luotu")
        return
    
    with open(candidates_file, 'r', encoding='utf-8') as f:
        candidates_data = json.load(f)
    
    # Lataa kysymykset nimeä varten
    questions_map = {}
    if os.path.exists(questions_file):
        with open(questions_file, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
        questions_map = {q["local_id"]: q["content"]["question"]["fi"] for q in questions_data["questions"]}
    
    if candidate_id:
        # Näytä tietyn ehdokkaan vastaukset
        candidate = next((c for c in candidates_data["candidates"] if c["candidate_id"] == candidate_id), None)
        if not candidate:
            click.echo(f"❌ Ehdokasta '{candidate_id}' ei löydy")
            return
        
        click.echo(f"📝 EHDOKKAAN {candidate_id} VASTAUKSET")
        click.echo("=" * 50)
        
        if "answers" not in candidate or not candidate["answers"]:
            click.echo("❌ Ei vastauksia")
            return
        
        for answer in candidate["answers"]:
            question_text = questions_map.get(answer["question_id"], answer["question_id"])
            click.echo(f"❓ {question_text}")
            click.echo(f"   📊 Vastaus: {answer['answer_value']}/5")
            click.echo(f"   🎯 Varmuus: {answer['confidence']}/5")
            if answer["explanation"]["fi"]:
                click.echo(f"   💬 Perustelu: {answer['explanation']['fi']}")
            click.echo()
    
    elif question_id:
        # Näytä tietyn kysymyksen vastaukset
        click.echo(f"📝 KYSYMYKSEN {question_id} VASTAUKSET")
        click.echo("=" * 50)
        
        question_text = questions_map.get(question_id, question_id)
        click.echo(f"Kysymys: {question_text}")
        click.echo()
        
        found_answers = False
        for candidate in candidates_data["candidates"]:
            if "answers" in candidate:
                answer = next((a for a in candidate["answers"] if a["question_id"] == question_id), None)
                if answer:
                    found_answers = True
                    click.echo(f"👤 {candidate['basic_info']['name']['fi']} ({candidate['candidate_id']})")
                    click.echo(f"   📊 Vastaus: {answer['answer_value']}/5")
                    click.echo(f"   🎯 Varmuus: {answer['confidence']}/5")
                    if answer["explanation"]["fi"]:
                        click.echo(f"   💬 Perustelu: {answer['explanation']['fi']}")
                    click.echo()
        
        if not found_answers:
            click.echo("❌ Ei vastauksia tähän kysymykseen")
    
    else:
        # Näytä kaikkien ehdokkaiden yhteenveto
        click.echo("📊 EHDOKKAIDEN VASTAUSYHTEENVETO")
        click.echo("=" * 50)
        
        total_answers = 0
        candidates_with_answers = 0
        
        for candidate in candidates_data["candidates"]:
            answer_count = len(candidate.get("answers", []))
            total_answers += answer_count
            if answer_count > 0:
                candidates_with_answers += 1
            
            candidate_name = candidate["basic_info"]["name"]["fi"]
            click.echo(f"👤 {candidate_name} ({candidate['candidate_id']}): {answer_count} vastausta")
        
        click.echo()
        click.echo(f"📈 YHTEENVETO:")
        click.echo(f"   Ehdokkaita: {len(candidates_data['candidates'])}")
        click.echo(f"   Vastanneita: {candidates_with_answers}")
        click.echo(f"   Vastauksia yhteensä: {total_answers}")
        
        if len(candidates_data["candidates"]) > 0:
            coverage = (candidates_with_answers / len(candidates_data["candidates"])) * 100
            click.echo(f"   Vastauskattavuus: {coverage:.1f}%")

@manage_answers.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--candidate-id', required=True, help='Ehdokkaan tunniste')
@click.option('--question-id', required=True, help='Kysymyksen tunniste')
def remove(election, candidate_id, question_id):
    """Poista ehdokkaan vastaus"""
    
    candidates_file = f"data/runtime/candidates.json"
    if not os.path.exists(candidates_file):
        click.echo("❌ Ehdokasrekisteriä ei ole vielä luotu")
        return
    
    with open(candidates_file, 'r', encoding='utf-8') as f:
        candidates_data = json.load(f)
    
    candidate = next((c for c in candidates_data["candidates"] if c["candidate_id"] == candidate_id), None)
    if not candidate:
        click.echo(f"❌ Ehdokasta '{candidate_id}' ei löydy")
        return
    
    if "answers" not in candidate:
        click.echo("❌ Ehdokkaalla ei ole vastauksia")
        return
    
    # Etsi ja poista vastaus
    initial_count = len(candidate["answers"])
    candidate["answers"] = [a for a in candidate["answers"] if a["question_id"] != question_id]
    
    if len(candidate["answers"]) == initial_count:
        click.echo(f"❌ Vastausta ei löytynyt: {candidate_id} → {question_id}")
        return
    
    # Tallenna
    with open(candidates_file, 'w', encoding='utf-8') as f:
        json.dump(candidates_data, f, indent=2, ensure_ascii=False)
    
    click.echo(f"✅ Vastaus poistettu: {candidate_id} → {question_id}")
    click.echo(f"📊 Ehdokkaalla on nyt {len(candidate['answers'])} vastausta")

if __name__ == '__main__':
    manage_answers()
