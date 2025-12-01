#!/usr/bin/env python3
"""
Järjestelmän asennus - yksinkertainen wrapper
"""
import sys
from pathlib import Path

# Lisää polku
sys.path.insert(0, str(Path(__file__).parent.parent))

# Käytä joko uutta tai vanhaa
try:
    # Kokeile uutta modulaarista
    from cli.install.cli import install_system
    print("🔧 Using modular installation system")
except ImportError as e:
    print(f"⚠️  Modular system not available: {e}")
    print("📋 Using original implementation")
    
    # Importoi alkuperäinen suoraan
    exec(open('src/cli/install_original.py').read())
    sys.exit(0)

if __name__ == "__main__":
    install_system()
