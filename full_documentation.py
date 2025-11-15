# full_documentation.py
import os
import json
from datetime import datetime
from pathlib import Path

def generate_full_documentation():
    """Generoi täydellisen dokumentaation merge-jälkeisestä tilasta"""
    
    doc = {
        "generated_at": datetime.now().isoformat(),
        "git_status": "Post-merge analysis",
        "codebase_overview": {},
        "module_structure": {},
        "test_coverage": {},
        "largest_files": [],
        "recommendations": []
    }
    
    # 1. Analysoi koodikanta
    analyze_codebase(doc)
    
    # 2. Tarkista moduulirakenne
    analyze_module_structure(doc)
    
    # 3. Testikattavuus
    analyze_test_coverage(doc)
    
    # 4. Generoi suositukset
    generate_recommendations(doc)
    
    # Tallenna dokumentaatio
    output_file = f"docs/full_documentation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Täydellinen dokumentaatio luotu: {output_file}")
    return doc

def analyze_codebase(doc):
    """Analysoi koko koodikannan"""
    python_files = list(Path("src").rglob("*.py"))
    total_lines = 0
    file_stats = []
    
    for file_path in python_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            line_count = len(lines)
            total_lines += line_count
            
            file_stats.append({
                "path": str(file_path),
                "lines": line_count,
                "module": file_path.parent.name
            })
    
    doc["codebase_overview"] = {
        "total_python_files": len(python_files),
        "total_lines_of_code": total_lines,
        "average_file_size": total_lines / len(python_files) if python_files else 0
    }
    
    # Etsi suurimmat tiedostot
    doc["largest_files"] = sorted(file_stats, key=lambda x: x["lines"], reverse=True)[:15]

def analyze_module_structure(doc):
    """Analysoi moduulirakennetta"""
    modules = {}
    
    for root, dirs, files in os.walk("src"):
        module_name = root.replace("src/", "").replace("/", ".")
        if module_name:
            py_files = [f for f in files if f.endswith('.py') and f != '__init__.py']
            if py_files:
                modules[module_name] = {
                    "files": py_files,
                    "file_count": len(py_files)
                }
    
    doc["module_structure"] = modules

def analyze_test_coverage(doc):
    """Analysoi testikattavuutta"""
    test_files = list(Path("tests").rglob("*.py"))
    test_stats = {
        "total_test_files": len(test_files),
        "unit_tests": 0,
        "integration_tests": 0,
        "test_files": []
    }
    
    for file_path in test_files:
        test_type = "unit" if "unit" in str(file_path) else "integration"
        if test_type == "unit":
            test_stats["unit_tests"] += 1
        else:
            test_stats["integration_tests"] += 1
            
        test_stats["test_files"].append({
            "path": str(file_path),
            "type": test_type
        })
    
    doc["test_coverage"] = test_stats

def generate_recommendations(doc):
    """Generoi kehityssuosituksia"""
    recommendations = []
    
    # Analysoi suurimmat tiedostot
    large_files = [f for f in doc["largest_files"] if f["lines"] > 300]
    if large_files:
        recommendations.append({
            "type": "refactoring",
            "priority": "high",
            "description": f"{len(large_files)} tiedostoa yli 300 riviä - harkitse jakamista",
            "files": [f["path"] for f in large_files[:5]]
        })
    
    # Tarkista moduulitasapaino
    modules = doc["module_structure"]
    if "managers" in modules and modules["managers"]["file_count"] > 10:
        recommendations.append({
            "type": "organization", 
            "priority": "medium",
            "description": "managers-moduuli sisältää yli 10 tiedostoa - harkitse alimoduuleja",
            "details": f"Tiedostoja: {modules['managers']['file_count']}"
        })
    
    doc["recommendations"] = recommendations

# Suorita dokumentaation generointi
if __name__ == "__main__":
    documentation = generate_full_documentation()
    
    # Tulosta yhteenveto
    print("\n📊 DOKUMENTAATION YHTEENVETO")
    print("=" * 50)
    print(f"Kooditiedostoja: {documentation['codebase_overview']['total_python_files']}")
    print(f"Koodirivejä: {documentation['codebase_overview']['total_lines_of_code']}")
    print(f"Testitiedostoja: {documentation['test_coverage']['total_test_files']}")
    
    print("\n🔧 KEHITYSSUOSITUKSET:")
    for rec in documentation['recommendations']:
        print(f"  {rec['priority'].upper()}: {rec['description']}")

