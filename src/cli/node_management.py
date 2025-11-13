#!/usr/bin/env python3
"""
Multi-node hallinnan CLI-työkalu
"""
import click
import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

@click.group()
def node_management():
    """Multi-node järjestelmän hallinta"""
    pass

@node_management.command()
@click.option('--election', default='Jumaltenvaalit2026', help='Vaalin tunniste')
def list_nodes(election):
    """Listaa kaikki aktiiviset nodet"""
    from nodes.node_manager import NodeManager
    
    manager = NodeManager(election)
    active_nodes = manager.get_active_nodes()
    
    click.echo("🖥️  AKTIIVISET NODET:")
    click.echo("=" * 50)
    
    for node in active_nodes:
        click.echo(f"🏛️  {node['node_name']} ({node['node_id']})")
        click.echo(f"   🌐 Domain: {node['domain']}")
        click.echo(f"   ⭐ Trust: {node['trust_score']}")
        click.echo(f"   📍 Status: {node['status']}")
        click.echo()

@node_management.command()
@click.option('--election', default='Jumaltenvaalit2026', help='Vaalin tunniste')
def quorum_info(election):
    """Näytä kvoorumin tiedot"""
    from nodes.node_manager import NodeManager
    
    manager = NodeManager(election)
    quorum_nodes = manager.get_quorum_nodes()
    threshold = manager.calculate_quorum_threshold()
    
    click.echo("📊 KVOORUMI-TIEDOT:")
    click.echo("=" * 50)
    click.echo(f"🖥️  Kvoorumi-nodeja: {len(quorum_nodes)}")
    click.echo(f"🎯 Vaadittu hyväksymisiä: {threshold}")
    
    click.echo("\n🏛️  KVOORUMI-NODET:")
    for node in quorum_nodes:
        click.echo(f"   ✅ {node['node_name']} (trust: {node['trust_score']})")

if __name__ == '__main__':
    node_management()
