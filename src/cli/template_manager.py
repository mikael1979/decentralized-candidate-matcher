#!/usr/bin/env python3
"""
Template-hallinnan komentorivityökalu - PARANNETTU VERSIO
"""
import click
import json
from pathlib import Path
from typing import Dict, List
import sys
import os

# Lisää src hakemisto Python-polkuun
sys.path.insert(0, str(Path(__file__).parent.parent))

@click.group()
def template_manager():
    """Template-hallinnan komentorivityökalu"""
    pass

@template_manager.command()
def audit():
    """Auditoi template-laatu"""
    click.echo("🔍 Aloitetaan template-auditointi...")
    
    try:
        # Yksinkertaistettu validointi ilman TemplateValidator-riippuvuutta
        base_dir = Path("base_templates")
        
        if not base_dir.exists():
            click.echo("❌ Template-hakemistoa ei löydy: base_templates/")
            return
            
        template_files = list(base_dir.rglob("*.base.json"))
        valid_count = 0
        invalid_count = 0
        
        for template_file in template_files:
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                
                # Yksinkertainen validointi
                if "metadata" in template_data and "examples" in template_data:
                    valid_count += 1
                else:
                    invalid_count += 1
                    
            except Exception as e:
                invalid_count += 1
        
        click.echo("📊 TEMPLATE AUDIT RAPORTTI")
        click.echo("=" * 50)
        click.echo(f"✅ Validit templatet: {valid_count}")
        click.echo(f"❌ Virheelliset templatet: {invalid_count}")
        click.echo(f"📁 Tarkistetut tiedostot: {len(template_files)}")
        
        click.echo("\n🎉 AUDIT VALMIS!")
        
    except Exception as e:
        click.echo(f"❌ Auditointi epäonnistui: {e}")

@template_manager.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--template-type', required=True, 
              type=click.Choice(['questions', 'candidates', 'parties', 'election_config']))
def generate(election, template_type):
    """Generoi runtime-tiedosto base-templatesta"""
    click.echo(f"🔄 Generoidaan {template_type} templatesta...")
    
    try:
        # Yksinkertaistettu generaattori ilman TemplateGenerator-riippuvuutta
        base_path = Path(f"base_templates/{template_type}/{template_type}.base.json")
        
        # Tarkista että template on olemassa
        if not base_path.exists():
            click.echo(f"❌ Templatea ei löydy: {base_path}")
            click.echo("💡 Käytettävissä olevat templatet:")
            template_files = list(Path("base_templates").rglob("*.base.json"))
            for tf in template_files:
                click.echo(f"  • {tf}")
            return
        
        click.echo(f"📁 Ladataan template: {base_path}")
        
        # Lue template data
        with open(base_path, 'r', encoding='utf-8') as f:
            template_data = json.load(f)
        
        # Korvaa placeholdereit
        from datetime import datetime
        import re
        
        def replace_placeholders(obj):
            if isinstance(obj, dict):
                return {k: replace_placeholders(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_placeholders(item) for item in obj]
            elif isinstance(obj, str):
                # Korvaa perus placeholdereit
                replacements = {
                    r'\{\{ELECTION_ID\}\}': election,
                    r'\{\{TIMESTAMP\}\}': datetime.now().isoformat(),
                }
                
                result = obj
                for pattern, replacement in replacements.items():
                    result = re.sub(pattern, replacement, result)
                return result
            else:
                return obj
        
        runtime_data = replace_placeholders(template_data)
        
        # Tallenna runtime-hakemistoon
        runtime_path = Path(f"data/runtime/{template_type}.json")
        runtime_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(runtime_path, 'w', encoding='utf-8') as f:
            json.dump(runtime_data, f, indent=2, ensure_ascii=False)
        
        click.echo(f"✅ LUOTU: {runtime_path}")
        click.echo(f"📊 Tiedostokoko: {runtime_path.stat().st_size} tavua")
        
        # Näytä luodut rakenteet
        if 'candidates' in runtime_data:
            click.echo(f"📝 Luotiin: {len(runtime_data['candidates'])} ehdokasrakenne")
        elif 'questions' in runtime_data:
            click.echo(f"📝 Luotiin: {len(runtime_data['questions'])} kysymysrakenne")
        elif 'parties' in runtime_data:
            click.echo(f"📝 Luotiin: {len(runtime_data['parties'])} puoluerakenne")
        
        click.echo("🎉 GENEROINTI VALMIS!")
        
    except Exception as e:
        click.echo(f"❌ Generointi epäonnistui: {e}")
        import traceback
        traceback.print_exc()

@template_manager.command()
@click.option('--template-file', required=True, help='Tarkistettavan template-tiedoston polku')
def validate(template_file):
    """Validoi yksittäinen template-tiedosto"""
    click.echo(f"🔍 Validoidaan templatea: {template_file}")
    
    try:
        template_path = Path(template_file)
        
        if not template_path.exists():
            click.echo(f"❌ Templatea ei löydy: {template_path}")
            return
            
        with open(template_path, 'r', encoding='utf-8') as f:
            template_data = json.load(f)
        
        click.echo("📊 VALIDAATIOTULOKSET")
        click.echo("=" * 40)
        click.echo(f"📁 Tiedosto: {template_path.name}")
        
        # Yksinkertainen validointi
        errors = []
        if "metadata" not in template_data:
            errors.append("Puuttuva metadata-osio")
        if "examples" not in template_data:
            errors.append("Puuttuvat esimerkit")
        
        # Tarkista placeholdereit
        import re
        template_str = json.dumps(template_data)
        placeholders = re.findall(r'\{\{.*?\}\}', template_str)
        
        click.echo(f"✅ Tila: {'VALIDI' if not errors else 'VIRHEELLINEN'}")
        click.echo(f"🔢 Placeholdereita: {len(placeholders)}")
        
        if errors:
            click.echo("\n🚨 LÖYDETYT VIRHEET:")
            for error in errors:
                click.echo(f"  • {error}")
        else:
            click.echo("\n✅ Ei virheitä löydetty!")
            
        if placeholders:
            click.echo("\n📋 LÖYDETYT PLACEHOLDERIT:")
            for i, placeholder in enumerate(set(placeholders[:10])):  # Näytä 10 ensimmäistä
                click.echo(f"  {i+1}. {placeholder}")
            if len(placeholders) > 10:
                click.echo(f"  ... ja {len(placeholders) - 10} muuta")
            
        click.echo("\n🎉 VALIDAATIO VALMIS!")
        
    except json.JSONDecodeError as e:
        click.echo(f"❌ Virheellinen JSON: {e}")
    except Exception as e:
        click.echo(f"❌ Validointi epäonnistui: {e}")

@template_manager.command()
def list_templates():
    """Listaa kaikki saatavilla olevat templatet"""
    click.echo("📋 KÄYTTÖSSÄ OLEVAT TEMPLATET")
    click.echo("=" * 40)
    
    base_dir = Path("base_templates")
    if not base_dir.exists():
        click.echo("❌ Template-hakemistoa ei löydy")
        return
        
    template_files = list(base_dir.rglob("*.base.json"))
    
    if not template_files:
        click.echo("ℹ️ Ei template-tiedostoja")
        return
        
    for template_file in sorted(template_files):
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            metadata = template_data.get('metadata', {})
            click.echo(f"📄 {template_file.relative_to(base_dir)}")
            click.echo(f"   🏷️  Versio: {metadata.get('version', 'N/A')}")
            click.echo(f"   📝 {metadata.get('description', {}).get('fi', 'Ei kuvausta')}")
            click.echo()
            
        except Exception as e:
            click.echo(f"❌ {template_file.relative_to(base_dir)} - Virhe: {e}")
            click.echo()

@template_manager.command()
def help():
    """Näytä käyttöohjeet"""
    click.echo("🎯 TEMPLATE-MANAGER KÄYTTÖOHJEET")
    click.echo("=" * 50)
    click.echo("Komennot:")
    click.echo("  generate --election <vaali> --template-type <tyyppi>")
    click.echo("  validate --template-file <polku>")
    click.echo("  audit")
    click.echo("  list-templates")
    click.echo("  help")
    click.echo()
    click.echo("Esimerkkejä:")
    click.echo("  python src/cli/template_manager.py generate --election Jumaltenvaalit2026 --template-type candidates")
    click.echo("  python src/cli/template_manager.py validate --template-file base_templates/candidates/candidates.base.json")
    click.echo("  python src/cli/template_manager.py list-templates")

if __name__ == '__main__':
    template_manager()
