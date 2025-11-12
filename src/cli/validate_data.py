#!/usr/bin/env python3
"""
Data validointityökalu
"""
import click
import json
import os
from pathlib import Path

@click.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--fix', is_flag=True, help='Korjaa automaattisesti löydetyt ongelmat')
def validate_data(election, fix):
    """Validoi kaikki data-tiedostot"""
    
    click.echo("🔍 DATA VALIDOINTI")
    click.echo("=" * 50)
    
    files_to_check = [
        f"data/runtime/meta.json",
        f"data/runtime/system_chain.json", 
        f"data/runtime/questions.json",
        f"data/runtime/candidates.json",
        f"data/runtime/parties.json"
    ]
    
    issues_found = 0
    fixed_issues = 0
    
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            click.echo(f"❌ Tiedostoa puuttuu: {file_path}")
            issues_found += 1
            continue
        
        try:
            # Yritä lukea JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Tarkista perusrakenteet
            if "metadata" not in data and file_path != "data/runtime/system_chain.json":
                click.echo(f"⚠️  Puuttuu metadata: {file_path}")
                issues_found += 1
                
                if fix and file_path == "data/runtime/questions.json":
                    data["metadata"] = {"election_id": election}
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    click.echo(f"✅ Korjattu: {file_path}")
                    fixed_issues += 1
            
            click.echo(f"✅ {file_path} - OK")
            
        except json.JSONDecodeError as e:
            click.echo(f"❌ Virheellinen JSON: {file_path} - {e}")
            issues_found += 1
    
    click.echo()
    click.echo("📊 VALIDOINTITULOKSET:")
    click.echo(f"   Tarkistetut tiedostot: {len(files_to_check)}")
    click.echo(f"   Ongelmia löydetty: {issues_found}")
    if fix:
        click.echo(f"   Korjattuja ongelmia: {fixed_issues}")
    
    if issues_found == 0:
        click.echo("🎉 Kaikki data-tiedostot ovat validit!")
    else:
        click.echo("💡 Käytä --fix yrittääksesi korjata ongelmat automaattisesti")

if __name__ == '__main__':
    validate_data()
