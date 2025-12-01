#!/usr/bin/env python3
"""
Päämoduuli asennukseen - MODULAARINEN VERSIO
"""
import sys
from pathlib import Path

# Lisää projektin juuri Python-polkuun
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from src.cli.install.commands.install_command import install_command
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


if __name__ == '__main__':
    install_command()
