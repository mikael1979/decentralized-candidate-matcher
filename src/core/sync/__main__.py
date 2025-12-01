# src/core/sync/__main__.py
"""
Pääsuoritustiedosto modulaariselle synkronoinnille.
"""
import sys
from pathlib import Path

# Lisää projektin juuri Python-polkuun
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from core.sync import sync_cli
    if sync_cli:
        if __name__ == "__main__":
            sync_cli()
    else:
        print("❌ Sync CLI not available - check command imports")
except ImportError as e:
    print(f"❌ Failed to import sync_cli: {e}")
