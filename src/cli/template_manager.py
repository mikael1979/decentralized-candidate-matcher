# src/cli/template_manager.py
@click.group()
def template_manager():
    """Template-hallinnan komentorivityökalu"""
    pass

@template_manager.command()
def audit():
    """Auditoi template-laatu"""
    validator = TemplateValidator()
    results = validator.validate_template_directory(Path("base_templates"))
    
    click.echo("📊 TEMPLATE AUDIT RAPORTTI")
    click.echo(f"✅ Validit templatet: {len(results['valid_templates'])}")
    click.echo(f"❌ Virheelliset templatet: {len(results['invalid_templates'])}")
    
    for invalid in results['invalid_templates']:
        click.echo(f"  • {invalid['file']}: {', '.join(invalid['errors'])}")

@template_manager.command()
def enhance():
    """Paranna kaikki templatet uuteen standardiin"""
    enhancer = TemplateEnhancer()
    enhancer.enhance_all_templates()
    click.echo("🎉 Kaikki templatet parannettu!")

@template_manager.command()
@click.option('--election', required=True)
@click.option('--template-type', required=True, 
              type=click.Choice(['questions', 'candidates', 'parties', 'election_config']))
def generate(election, template_type):
    """Generoi runtime-tiedosto base-templatesta"""
    generator = TemplateGenerator()
    
    base_path = Path(f"base_templates/{template_type}/{template_type}.base.json")
    runtime_data = generator.create_runtime_from_base(base_path, election)
    
    # Tallenna runtime-hakemistoon
    runtime_path = Path(f"data/runtime/{election}/{template_type}.json")
    runtime_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(runtime_path, 'w', encoding='utf-8') as f:
        json.dump(runtime_data, f, indent=2, ensure_ascii=False)
    
    click.echo(f"✅ Luotu: {runtime_path}")

