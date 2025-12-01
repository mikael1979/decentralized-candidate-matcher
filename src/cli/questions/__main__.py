# src/cli/questions/__main__.py
"""
Pääsuoritustiedosto modulaariselle kysymystenhallinnalle.
"""
import sys
from pathlib import Path

# Lisää projektin juuri Python-polkuun
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Nyt tuo moduuli
from src.cli.questions import questions_cli

if __name__ == "__main__":
    questions_cli()
