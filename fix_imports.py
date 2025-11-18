#!/usr/bin/env python3
"""
Korjaa kaikkien CLI-tiedostojen import-ongelmat
"""
import os
import re
from pathlib import Path

def fix_cli_imports():
    cli_dir = Path("src/cli")
    
    for py_file in cli_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
            
        print(f"Korjataan: {py_file}")
        
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Korvaa importit
        new_content = content
        
        # Lisää sys.path-korjaus jos ei ole
        if "sys.path.insert" not in content:
            import_section = """#!/usr/bin/env python3
import click
import json
from datetime import datetime
import os
import sys
from pathlib import Path

# LISÄTTY: Lisää src hakemisto Python-polkuun
sys.path.insert(0, str(Path(__file__).parent.parent))

"""
            # Poista mahdollinen duplikaatti shebang
            lines = content.split('\n')
            if lines[0].startswith('#!/usr/bin/env python3'):
                lines = lines[1:]
            content_without_shebang = '\n'.join(lines)
            
            new_content = import_section + content_without_shebang
        
        # Korjaa import-virheet
        new_content = new_content.replace(
            "from src.core.file_utils import", 
            "from core.file_utils import"
        )
        new_content = new_content.replace(
            "from src.core.", 
            "from core."
        )
        new_content = new_content.replace(
            "from src.managers.", 
            "from managers."
        )
        
        # Tallenna korjattu tiedosto
        with open(py_file, 'w', encoding='utf-8') as f:
            f.write(new_content)

if __name__ == '__main__':
    fix_cli_imports()
    print("✅ Kaikki CLI-tiedostot korjattu!")
