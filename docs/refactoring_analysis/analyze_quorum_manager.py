#!/usr/bin/env python3
"""
QuorumManager syväanalyysi refaktorointia varten
"""
import ast
import sys
from pathlib import Path

def analyze_quorum_manager():
    """Analysoi quorum_manager.py rakenne"""
    
    filepath = Path("src/managers/quorum_manager.py")
    if not filepath.exists():
        print("❌ quorum_manager.py ei löydy")
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Analysoi AST:lla
    tree = ast.parse(content)
    
    # Etsi QuorumManager luokka
    quorum_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "QuorumManager":
            quorum_class = node
            break
    
    if not quorum_class:
        print("❌ QuorumManager-luokkaa ei löydy")
        return
    
    print("🔍 QUORUM_MANAGER SYVÄANALYYSI")
    print("=" * 60)
    
    # Laske metodit
    methods = [n for n in quorum_class.body if isinstance(n, ast.FunctionDef)]
    public_methods = [m for m in methods if not m.name.startswith('_')]
    private_methods = [m for m in methods if m.name.startswith('_')]
    
    print(f"📊 Luokan koko: {len(content.splitlines())} riviä")
    print(f"📊 Metodeja yhteensä: {len(methods)}")
    print(f"📊 Julkisia metodeja: {len(public_methods)}")
    print(f"📊 Yksityisiä metodeja: {len(private_methods)}")
    
    # Ryhmitä metodit toiminnallisuuden mukaan
    print("\n🎯 METODIEN TOIMINNALLISUUSRYHMIT:")
    
    method_groups = {
        "Konsensus": [],
        "Äänestys": [],
        "Verkkoyhteys": [],
        "Data-käsittely": [],
        "Apumetodit": []
    }
    
    for method in methods:
        name = method.name
        if any(word in name for word in ['consensus', 'agree', 'decide']):
            method_groups["Konsensus"].append(name)
        elif any(word in name for word in ['vote', 'ballot', 'poll']):
            method_groups["Äänestys"].append(name)
        elif any(word in name for word in ['network', 'node', 'peer', 'connect']):
            method_groups["Verkkoyhteys"].append(name)
        elif any(word in name for word in ['process', 'handle', 'manage', 'update']):
            method_groups["Data-käsittely"].append(name)
        else:
            method_groups["Apumetodit"].append(name)
    
    for group, methods in method_groups.items():
        if methods:
            print(f"  {group}: {len(methods)} metodia")
            for method in sorted(methods):
                print(f"    - {method}()")
    
    # Analysoi riippuvuudet
    print("\n🔗 RIIPPUVUUDET:")
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imports.append(f"{module}.{alias.name}")
    
    unique_imports = sorted(set(imports))
    for imp in unique_imports[:10]:  # Näytä vain 10 ensimmäistä
        print(f"  - {imp}")
    
    if len(unique_imports) > 10:
        print(f"  - ... ja {len(unique_imports) - 10} muuta")

if __name__ == "__main__":
    analyze_quorum_manager()
