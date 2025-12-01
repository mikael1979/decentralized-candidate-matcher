#!/usr/bin/env python3
"""
QuorumManager detalioitu analyysi - FOKUS: VERIFIKAATIO & ÄÄNESTYS
"""
import ast
import sys
from pathlib import Path

def analyze_quorum_detailed():
    """Analysoi quorum_manager.py:n todellinen toiminnallisuus"""
    
    filepath = Path("src/managers/quorum_manager.py")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.splitlines()
    
    print("🔍 QUORUM_MANAGER DETALIOITU ANALYYSI")
    print("=" * 60)
    
    # Analysoi metodien koot ja sisältö
    tree = ast.parse(content)
    quorum_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "QuorumManager":
            quorum_class = node
            break
    
    if not quorum_class:
        return
    
    methods = [n for n in quorum_class.body if isinstance(n, ast.FunctionDef)]
    
    print("📊 METODIEN KOKOJAKAUMA:")
    for method in methods:
        start_line = method.lineno
        # Etsi metodin loppurivi (yksinkertaistettu)
        end_line = start_line
        for i, line in enumerate(lines[start_line:], start_line):
            if line.strip() and not line.startswith(' ') and not line.startswith('def '):
                end_line = i - 1
                break
        
        line_count = end_line - start_line
        print(f"  {method.name:35} {line_count:3} riviä")
    
    # Analysoi avainsanojen esiintymiset
    keywords = {
        'verification': 0,
        'vote': 0,
        'quorum': 0,
        'taq': 0,
        'config': 0,
        'party': 0,
        'media': 0,
        'consensus': 0
    }
    
    for line in content.lower().splitlines():
        for keyword in keywords:
            if keyword in line:
                keywords[keyword] += 1
    
    print("\n🎯 AVainsanojen Esiintymiset:")
    for keyword, count in sorted(keywords.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  {keyword:15} {count:3} kertaa")

if __name__ == "__main__":
    analyze_quorum_detailed()
