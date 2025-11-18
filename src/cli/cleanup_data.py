#!/usr/bin/env python3
import click
import json
from datetime import datetime
import os
import sys
from pathlib import Path

# Lisää src hakemisto Python-polkuun
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.file_utils import read_json_file, write_json_file, ensure_directory

@click.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--fix-duplicates', is_flag=True, help='Korjaa duplikaatit')
@click.option('--validate', is_flag=True, help='Tarkista data-eheys')
@click.option('--backup', is_flag=True, help='Tee varmuuskopio ennen korjausta')
@click.option('--dry-run', is_flag=True, help='Näytä mitä korjattaisiin, älä tallenna')
def cleanup_data(election, fix_duplicates, validate, backup, dry_run):
    """Siivoa ja korjaa data-eheysongelmat"""
    
    candidates_file = "data/runtime/candidates.json"
    questions_file = "data/runtime/questions.json"
    
    if backup and not dry_run:
        # Tee varmuuskopiot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"data/backup/{timestamp}"
        ensure_directory(backup_dir)
        
        if os.path.exists(candidates_file):
            backup_candidates = f"{backup_dir}/candidates.json"
            with open(candidates_file, 'r', encoding='utf-8') as src, open(backup_candidates, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
            click.echo(f"✅ Varmuuskopioitu: {backup_candidates}")
        
        if os.path.exists(questions_file):
            backup_questions = f"{backup_dir}/questions.json"
            with open(questions_file, 'r', encoding='utf-8') as src, open(backup_questions, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
            click.echo(f"✅ Varmuuskopioitu: {backup_questions}")
    
    if validate or fix_duplicates:
        click.echo("🔍 TARKISTETAAN DATA-EHEYS")
        click.echo("=" * 50)
        
        # Tarkista ehdokkaat
        if os.path.exists(candidates_file):
            data = read_json_file(candidates_file, {"candidates": []})
            candidates = data.get("candidates", [])
            
            # Etsi duplikaatit
            name_count = {}
            duplicate_candidates = []
            
            for candidate in candidates:
                name = candidate["basic_info"]["name"]["fi"]
                if name in name_count:
                    duplicate_candidates.append(candidate)
                name_count[name] = name_count.get(name, 0) + 1
            
            duplicates = {name: count for name, count in name_count.items() if count > 1}
            
            if duplicates:
                click.echo("❌ DUPLIKAATTI EHDOKKAAT:")
                for name, count in duplicates.items():
                    click.echo(f"   {name}: {count} kappaletta")
                
                # Näytä duplikaattien ID:t
                click.echo("\n📋 DUPLIKAATTIEN ID:T:")
                for name in duplicates:
                    dup_ids = [c["candidate_id"] for c in candidates if c["basic_info"]["name"]["fi"] == name]
                    click.echo(f"   {name}: {', '.join(dup_ids)}")
            else:
                click.echo("✅ Ei duplikaatti ehdokkaita")
            
            click.echo(f"📊 Ehdokkaita yhteensä: {len(candidates)}")
            
            # Korjaa duplikaatit jos pyydetty
            if fix_duplicates and duplicates and not dry_run:
                click.echo("\n🔧 KORJATAAN DUPLIKAATIT...")
                
                # Pidä vain ensimmäinen esiintymä jokaisesta nimestä
                seen_names = set()
                unique_candidates = []
                removed_count = 0
                
                for candidate in candidates:
                    name = candidate["basic_info"]["name"]["fi"]
                    if name not in seen_names:
                        seen_names.add(name)
                        unique_candidates.append(candidate)
                    else:
                        removed_count += 1
                        click.echo(f"🗑️  Poistettu duplikaatti: {name} ({candidate['candidate_id']})")
                
                if removed_count > 0:
                    data["candidates"] = unique_candidates
                    data["metadata"]["last_updated"] = datetime.now().isoformat()
                    data["metadata"]["total_candidates"] = len(unique_candidates)
                    
                    write_json_file(candidates_file, data)
                    click.echo(f"✅ Poistettu {removed_count} duplikaattia ehdokkaista")
                    click.echo(f"📊 Ehdokkaita nyt: {len(unique_candidates)}")
                else:
                    click.echo("✅ Ei duplikaatteja ehdokkaissa")
            
            elif fix_duplicates and dry_run:
                click.echo("\n🔧 DRY RUN - Korjattaisiin duplikaatit:")
                seen_names = set()
                for candidate in candidates:
                    name = candidate["basic_info"]["name"]["fi"]
                    if name in seen_names:
                        click.echo(f"🗑️  Poistettaisiin: {name} ({candidate['candidate_id']})")
                    else:
                        seen_names.add(name)
        
               # Tarkista kysymykset
        if os.path.exists(questions_file):
            data = read_json_file(questions_file, {"questions": []})
            questions = data.get("questions", [])
            
            # Etsi duplikaatit
            question_texts = {}
            for question in questions:
                text = question["content"]["question"]["fi"]
                question_texts[text] = question_texts.get(text, 0) + 1
            
            duplicates_questions = {text: count for text, count in question_texts.items() if count > 1}
            
            if duplicates_questions:
                click.echo("\n❌ DUPLIKAATTI KYSYMYKSET:")
                for text, count in list(duplicates_questions.items())[:5]:  # Näytä vain 5 ensimmäistä
                    click.echo(f"   '{text[:50]}...': {count} kappaletta")
            else:
                click.echo("\n✅ Ei duplikaatti kysymyksiä")
            
            click.echo(f"📊 Kysymyksiä yhteensä: {len(questions)}")
            
            # KORJAA KYSYMYKSET
            if fix_duplicates and duplicates_questions and not dry_run:
                click.echo("\n🔧 KORJATAAN KYSYMYSDUPLIKAATIT...")
                
                # Pidä vain ensimmäinen esiintymä jokaisesta kysymyksestä
                seen_questions = set()
                unique_questions = []
                removed_questions = 0
                
                for question in questions:
                    text = question["content"]["question"]["fi"]
                    if text not in seen_questions:
                        seen_questions.add(text)
                        unique_questions.append(question)
                    else:
                        removed_questions += 1
                        click.echo(f"🗑️  Poistettu duplikaatti kysymys: '{text[:50]}...'")
                
                if removed_questions > 0:
                    data["questions"] = unique_questions
                    data["metadata"]["last_updated"] = datetime.now().isoformat()
                    data["metadata"]["total_questions"] = len(unique_questions)
                    
                    write_json_file(questions_file, data)
                    click.echo(f"✅ Poistettu {removed_questions} duplikaattia kysymyksistä")
                    click.echo(f"📊 Kysymyksiä nyt: {len(unique_questions)}")
                else:
                    click.echo("✅ Ei duplikaatteja kysymyksissä")

if __name__ == '__main__':
    cleanup_data()
