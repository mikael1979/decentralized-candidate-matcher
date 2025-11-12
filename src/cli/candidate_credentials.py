# src/cli/candidate_credentials.py
import click
import json
from datetime import datetime

@click.group()
def candidate_credentials():
    """Ehdokkaiden PKI-valtuutusten hallinta"""
    pass

@candidate_credentials.command()
@click.option('--election', required=True, help='Vaalin tunniste')
@click.option('--party-id', required=True, help='Puolueen tunniste')
@click.option('--candidate-id', required=True, help='Ehdokkaan tunniste')
@click.option('--party-private-key-file', required=True, help='Puolueen yksityisen avaimen tiedosto')
def issue_credentials(election, party_id, candidate_id, party_private_key_file):
    """Luo ehdokkaalle PKI-valtuutus"""
    from src.managers.candidate_key_manager import CandidateKeyManager
    
    # Lataa puolueen avain
    with open(party_private_key_file, 'r') as f:
        party_private_key = f.read()
    
    manager = CandidateKeyManager(election)
    credentials = manager.issue_candidate_credentials(
        party_id, candidate_id, party_private_key
    )
    
    # Tallenna credentialit
    credential_file = f"credentials_{candidate_id}.json"
    with open(credential_file, 'w') as f:
        json.dump(credentials, f, indent=2)
    
    click.echo(f"✅ PKI-valtuutus luotu: {credential_file}")
    click.echo(f"🔑 Julkinen avain: {credentials['candidate_keys']['key_fingerprint']}")
    click.echo(f"⏰ Voimassa: {credentials['delegation_document']['valid_until'][:10]}")
