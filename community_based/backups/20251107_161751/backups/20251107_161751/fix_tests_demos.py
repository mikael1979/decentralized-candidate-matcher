# fix_tests_demos.py
#!/usr/bin/env python3
"""
Korjaa tests-hakemiston demo-skriptit
"""

import os

def fix_demo_comparisons():
    """Korjaa tests/demo_comparisons.py"""
    file_path = "tests/demo_comparisons.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Korvaa importit
    if "from complete_elo_calculator import" in content:
        # Korvaa import polulla
        content = content.replace(
            "from complete_elo_calculator import CompleteELOCalculator, ComparisonResult, UserTrustLevel",
            "import sys\nimport os\nsys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))\nfrom complete_elo_calculator import CompleteELOCalculator, ComparisonResult, UserTrustLevel"
        )
        print("✅ Korjattu demo_comparisons.py importit")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_demo_voting():
    """Korjaa tests/demo_voting.py"""
    file_path = "tests/demo_voting.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Korvaa importit
    if "from complete_elo_calculator import" in content:
        # Korvaa import polulla
        content = content.replace(
            "from complete_elo_calculator import VoteType, UserTrustLevel",
            "import sys\nimport os\nsys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))\nfrom complete_elo_calculator import VoteType, UserTrustLevel"
        )
        print("✅ Korjattu demo_voting.py importit")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    fix_demo_comparisons()
    fix_demo_voting()
    print("🎯 Demo-skriptit korjattu!")
