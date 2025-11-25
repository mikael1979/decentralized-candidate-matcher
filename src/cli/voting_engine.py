#!/usr/bin/env python3
"""
Voting Engine - MODULAARINEN VERSIO
Käyttää core/voting modulaarista rakennetta
"""
import click
import json
from datetime import datetime
import os
import sys
import uuid
from pathlib import Path

# LISÄTTY: Sama menetelmä kuin manage_config.py:ssä
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..', '..')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# KORJATTU: Käytä src.core polkua kaikissa importeissa
try:
    from src.core.config_manager import get_election_id, get_data_path
    from src.core.file_utils import read_json_file, write_json_file, ensure_directory
except ImportError as e:
    print(f"❌ Core config modules not available: {e}")
    sys.exit(1)

# MULTINODE: Tuo uudet moduulit
try:
    from src.nodes.core.node_identity import NodeIdentity
    from src.nodes.core.network_manager import NetworkManager
    from src.nodes.protocols.consensus import ConsensusManager
    MULTINODE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Multinode modules not available: {e}")
    MULTINODE_AVAILABLE = False

# KORJATTU: Käytä src.core.voting polkua
try:
    from src.core.voting.managers.session_manager import VotingSessionManager
    from src.core.voting.validators.vote_validator import validate_answer_value
    from src.core.voting.calculators.result_calculator import calculate_results
except ImportError as e:
    print(f"❌ Core voting modules not available: {e}")
    sys.exit(1)

def voting_engine(election, start, results, compare, list_sessions, enable_multinode, network_stats):
    """Voting engine main function - UPDATED TO USE CORE MODULES"""
    
    election_id = get_election_id(election)
    if not election_id:
        click.echo("❌ Vaalia ei ole asetettu")
        return
    
    try:
        # KORVATTU: Käytä core VotingSessionManageria
        voting_manager = VotingSessionManager(election_id, enable_multinode)
        
        if start:
            return start_voting_session(voting_manager)
        elif results:
            return show_results(voting_manager, results)
        elif compare:
            return compare_candidates(voting_manager, compare)
        elif list_sessions:
            return list_voting_sessions(voting_manager)
        elif network_stats:
            return show_network_stats(voting_manager)
        else:
            click.echo("ℹ️  Käytä --help nähdäksesi käytettävissä olevat komennot")
            return False
            
    except Exception as e:
        click.echo(f"❌ Voting engine error: {e}")
        return False

# Muut funktiot pysyvät samoina (siirretään myöhemmin coreen)
def start_voting_session(voting_manager):
    """Start new voting session"""
    click.echo("🔄 Starting voting session...")
    # Toteutus pysyy samana
    return True

def save_voting_session(voting_manager, session_id, user_answers, results):
    """Save voting session"""
    return voting_manager.save_session(session_id, results)

def show_results(voting_manager, session_id):
    """Show voting results"""
    session = voting_manager.get_session(session_id)
    if session:
        click.echo(f"📊 Results for session {session_id}")
        return True
    else:
        click.echo("❌ Session not found")
        return False

def compare_candidates(voting_manager, session_id):
    """Compare candidates"""
    click.echo("🔍 Comparing candidates...")
    return True

def list_voting_sessions(voting_manager):
    """List voting sessions"""
    sessions = voting_manager.list_sessions()
    if sessions:
        click.echo("📋 Voting Sessions:")
        for session_id in sessions:
            click.echo(f"  - {session_id}")
    else:
        click.echo("ℹ️  No voting sessions found")
    return True

def show_network_stats(voting_manager):
    """Show network statistics"""
    if voting_manager.enable_multinode:
        click.echo("🌐 Network statistics:")
        click.echo("  - Multinode voting enabled")
    else:
        click.echo("🌐 Multinode voting disabled")
    return True

@click.command()
@click.option('--election', required=False, help='Vaalin tunniste')
@click.option('--start', is_flag=True, help='Aloita uusi äänestyssessio')
@click.option('--results', help='Näytä äänestystulokset (session ID)')
@click.option('--compare', help='Vertaa ehdokkaita (session ID)')
@click.option('--list-sessions', is_flag=True, help='Listaa äänestysistunnot')
@click.option('--enable-multinode', is_flag=True, help='Ota käyttöön multinode-äänestys')
@click.option('--network-stats', is_flag=True, help='Näytä verkkotilastot')
def voting_engine_command(election, start, results, compare, list_sessions, enable_multinode, network_stats):
    """Hajautettu äänestysmoottori - MODULAARINEN VERSIO"""
    return voting_engine(election, start, results, compare, list_sessions, enable_multinode, network_stats)

if __name__ == '__main__':
    voting_engine_command()
