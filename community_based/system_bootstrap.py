# fix_syntax_error.py
#!/usr/bin/env python3
"""
Check and fix syntax error in system_bootstrap.py
"""

def check_syntax_error():
    try:
        with open('system_bootstrap.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print("🔍 ETSITÄÄN SYNTAX ERRORIA...")
        
        # Check around line 580
        start_line = max(0, 575)
        end_line = min(len(lines), 585)
        
        print(f"📄 Tarkistetaan rivit {start_line+1}-{end_line+1}:")
        print("-" * 40)
        
        for i in range(start_line, end_line):
            print(f"{i+1:4d}: {lines[i].rstrip()}")
        
        print("-" * 40)
        
        # Common syntax issues to check
        line_580 = lines[579] if len(lines) > 579 else ""
        if "print(" in line_580 and line_580.count('"') % 2 != 0:
            print("❌ Löytyi: Sulkeematon lainausmerkki print-komennossa")
            return 580, "sulkeematon_lainausmerkki"
        elif "=" in line_580 and "==" not in line_580 and line_580.count('=') == 1:
            print("❌ Löytyi: Yksittäinen = vertailussa")
            return 580, "yksittainen_vertailu"
        
        print("✅ Ei ilmeisiä syntax ongelmia löytynyt")
        return None, None
        
    except Exception as e:
        print(f"❌ Tarkistus epäonnistui: {e}")
        return None, None

def fix_syntax_error():
    line_num, error_type = check_syntax_error()
    
    if not line_num:
        print("💡 Kokeile suorittaa: python -m py_compile system_bootstrap.py")
        return False
    
    try:
        with open('system_bootstrap.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        original_line = lines[line_num-1]
        print(f"\n🔧 KORJATAAN RIVI {line_num}:")
        print(f"   ENNEN: {original_line.rstrip()}")
        
        if error_type == "sulkeematon_lainausmerkki":
            # Add missing quote
            if original_line.count('"') % 2 != 0:
                lines[line_num-1] = original_line.rstrip() + '"\n'
        elif error_type == "yksittainen_vertailu":
            # Fix comparison
            lines[line_num-1] = original_line.replace(' = ', ' == ')
        
        print(f"   JÄLKEEN: {lines[line_num-1].rstrip()}")
        
        # Backup original file
        import shutil
        shutil.copy2('system_bootstrap.py', 'system_bootstrap.py.backup')
        
        # Write fixed file
        with open('system_bootstrap.py', 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print("✅ Tiedosto korjattu! Vanha versio tallennettuna: system_bootstrap.py.backup")
        return True
        
    except Exception as e:
        print(f"❌ Korjaus epäonnistui: {e}")
        return False

if __name__ == "__main__":
    fix_syntax_error()
