#!/usr/bin/env python3
"""
File Utilities - Tiedostojen käsittelyapuja
"""

from pathlib import Path
import hashlib

def ensure_directory(path: str) -> bool:
    """Varmista että hakemisto on olemassa"""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"❌ Virhe luotaessa hakemistoa {path}: {e}")
        return False

def calculate_file_hash(file_path: str) -> str:
    """Laske tiedoston SHA-256 hash"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Poista kommentit ja tyhjät rivit consistenssin vuoksi
        lines = []
        for line in content.split('\n'):
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                lines.append(stripped)
        
        clean_content = '\n'.join(lines)
        return hashlib.sha256(clean_content.encode('utf-8')).hexdigest()
        
    except Exception as e:
        print(f"❌ Virhe laskettaessa hashia {file_path}: {e}")
        return "error"

def backup_file(file_path: str) -> bool:
    """Tee varmuuskopio tiedostosta"""
    path = Path(file_path)
    if not path.exists():
        return False
    
    backup_path = path.with_suffix(f'.backup_{path.suffix}')
    
    try:
        import shutil
        shutil.copy2(path, backup_path)
        print(f"✅ Varmuuskopio luotu: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Varmuuskopion luonti epäonnistui: {e}")
        return False
