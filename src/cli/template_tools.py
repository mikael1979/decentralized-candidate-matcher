#!/usr/bin/env python3
import click
import json
from datetime import datetime
import os
import sys
from pathlib import Path

# LISÄTTY: Lisää src hakemisto Python-polkuun
sys.path.insert(0, str(Path(__file__).parent.parent))

# src/cli/template_tools.py
@click.group()
def template_tools():
    """Template-hallinnan työkalut"""
    pass

@template_tools.command()
def audit():
    """Auditoi kaikki template-tiedostot"""
    auditor = TemplateAuditor()
    report = auditor.audit_all_templates()
    
    click.echo("📊 TEMPLATE AUDIT RAPORTTI")
    click.echo(f"📁 Templatet löydetty: {report['template_count']}")
    click.echo(f"⚠️  Ongelmia: {len(report['issues'])}")
    click.echo(f"🎯 Laatupisteet: {report['quality_score']}/100")

@template_tools.command()
@click.option('--election', required=True)
def setup(election):
    """Luo uuden vaalin template-konfiguraation"""
    setup_manager = ElectionSetupManager(election)
    setup_manager.initialize_from_templates()
    
    click.echo(f"✅ Vaali {election} alustettu")
    click.echo("📁 Luodut tiedostot:")
    for file in setup_manager.created_files:
        click.echo(f"  • {file}")
