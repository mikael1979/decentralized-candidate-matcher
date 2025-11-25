#!/usr/bin/env python3
"""
MODULAARINEN CONFIG-HALLINTA - LYHENNETTY VERSIO
Käyttää modulaarista rakennetta src/cli/config/ alla
"""
import sys
import os
import click

# Lisää src hakemisto Python-polkuun
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..', '..')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

try:
    from src.cli.config import manage_config
except ImportError as e:
    print(f"❌ Import-virhe: {e}")
    print("💡 Varmista että olet projektin juuressa")
    sys.exit(1)

if __name__ == '__main__':
    manage_config()
