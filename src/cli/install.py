#!/usr/bin/env python3
import click
import json
from datetime import datetime
import os
import sys
from pathlib import Path

# LISÄTTY: Lisää src hakemisto Python-polkuun
sys.path.insert(0, str(Path(__file__).parent.parent))

import click
import json
from datetime import datetime
import os

@click.command()
@click.option('--election-id', required=True, help='Vaalin tunniste')
@click.option('--first-install', is_flag=True, help='Ensimmäinen asennus')
def install_system(election_id, first_install):
    """Asenna vaalijärjestelmä"""
    click.echo(f"🏛️ Asennetaan Jumaltenvaalit: {election_id}")
    
    # Luo data-hakemisto
    os.makedirs("data/runtime", exist_ok=True)
    
    # Luo system_chain.json
    system_chain = {
        "chain_id": f"system_chain_{election_id}",
        "created_at": datetime.now().isoformat(),
        "description": f"Jumaltenvaalit 2026 - {election_id}",
        "version": "2.0.0",
        "blocks": [
            {
                "block_id": 0,
                "timestamp": datetime.now().isoformat(),
                "action_type": "divine_installation",
                "description": f"Jumaltenvaalit asennettu: {election_id}",
                "user_id": "zeus",
                "previous_hash": None,
                "block_hash": "initial_olympus_hash"
            }
        ]
    }
    
    with open("data/runtime/system_chain.json", "w") as f:
        json.dump(system_chain, f, indent=2)
    
    # Luo meta.json
    meta_data = {
        "metadata": {
            "version": "2.0.0", 
            "created": datetime.now().isoformat(),
            "election_id": election_id,
            "node_id": "olympus_master",
            "system_locked": False,
            "mode": "development",
            "divine_council": True
        }
    }
    
    with open("data/runtime/meta.json", "w") as f:
        json.dump(meta_data, f, indent=2)
    
    click.echo("✅ Jumaltenvaalit asennettu onnistuneesti!")
    click.echo("⚡ Olympos on valmis vaaleille!")

if __name__ == '__main__':
    install_system()
