# fix_manage_questions.py
#!/usr/bin/env python3
"""
Korjaa manage_questions.py syntax error
"""

def fix_manage_questions():
    file_path = "manage_questions.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Korjaa toistuva ensure_ascii
    if "ensure_ascii=False, ensure_ascii=False" in content:
        content = content.replace(
            "ensure_ascii=False, ensure_ascii=False", 
            "ensure_ascii=False"
        )
        print("✅ Korjattu toistuva ensure_ascii")
    
    # Tallenna korjattu versio
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ manage_questions.py korjattu!")

if __name__ == "__main__":
    fix_manage_questions()
