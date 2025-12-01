#!/usr/bin/env python3
"""
Järjestelmän asennus - pääentry point (taaksepäin yhteensopiva wrapper)
"""
import sys
from pathlib import Path

# Lisää polku
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    # Yritä ensin uutta CLI:ta
    from src.cli.install.cli import install_system
    print("✅ Using modular CLI")
except ImportError as e:
    print(f"⚠️  Modular CLI not available: {e}")
    print("💡 Using original implementation")
    
    # Importoi alkuperäinen
    from src.cli.install_original import install_system

if __name__ == "__main__":
    install_system()
