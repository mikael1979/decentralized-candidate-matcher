# scripts/migrate_hardcoded_data.py
#!/usr/bin/env python3
"""
Migraatiotyökalu kovakoodatun datan siirtämiseksi konfiguraatioihin
"""
import re
from pathlib import Path

class HardcodedDataMigrator:
    def __init__(self):
        self.migration_report = {
            "migrated_files": [],
            "remaining_hardcoded": [],
            "errors": []
        }
    
    def migrate_css_generator(self):
        """Siirrä CSS-generaattorin kovakoodattu data"""
        css_file = Path("src/templates/css_generator.py")
        
        print(f"🔧 Siirretään: {css_file}")
        
        try:
            with open(css_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Etsi PARTY_COLOR_THEMES lohko
            pattern = r'PARTY_COLOR_THEMES = \{.*?\}'
            match = re.search(pattern, content, re.DOTALL)
            
            if match:
                # Korvaa kovakoodattu data configuration-kutsulla
                new_content = re.sub(
                    pattern,
                    '# PARTY_COLOR_THEMES korvattu configuration-systemillä\nPARTY_COLOR_THEMES = CSSGenerator.get_color_themes()',
                    content,
                    flags=re.DOTALL
                )
                
                # Tallenna muutettu tiedosto
                with open(css_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                self.migration_report["migrated_files"].append(str(css_file))
                print("✅ CSS-generaattori siirretty")
            else:
                print("ℹ️  Ei kovakoodattua dataa löytynyt")
                
        except Exception as e:
            self.migration_report["errors"].append(f"{css_file}: {e}")
            print(f"❌ Virhe: {e}")
    
    def update_imports(self):
        """Päivitä importit käyttämään uutta CSSGeneratoria"""
        files_to_update = [
            "src/templates/candidate_templates.py",
            "src/templates/html_generator.py", 
            "src/templates/html_templates.py",
            "src/templates/party_templates.py",
            "src/templates/__init__.py",
            "src/cli/generate_profiles.py"
        ]
        
        for file_path in files_to_update:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Korvaa import
                new_content = content.replace(
                    'from .css_generator import CSSGenerator, PARTY_COLOR_THEMES',
                    'from .css_generator import CSSGenerator'
                )
                
                if new_content != content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"✅ Import päivitetty: {file_path}")
                    
            except Exception as e:
                self.migration_report["errors"].append(f"{file_path}: {e}")
                print(f"❌ Virhe: {file_path}: {e}")
    
    def generate_report(self):
        """Generoi migraatioraportti"""
        print("\n📊 MIGRAATION RAPORTTI")
        print("=" * 50)
        print(f"✅ Siirretyt tiedostot: {len(self.migration_report['migrated_files'])}")
        print(f"❌ Virheet: {len(self.migration_report['errors'])}")
        
        if self.migration_report['migrated_files']:
            print("\n📁 Siirretyt tiedostot:")
            for file in self.migration_report['migrated_files']:
                print(f"  • {file}")
        
        if self.migration_report['errors']:
            print("\n💥 Virheet:")
            for error in self.migration_report['errors']:
                print(f"  • {error}")

def main():
    """Pääfunktio"""
    print("🎯 KOVAKOODATUN DATAN MIGRAATIO")
    print("=" * 40)
    
    migrator = HardcodedDataMigrator()
    
    # Suorita migraatiot
    migrator.migrate_css_generator()
    migrator.update_imports()
    
    # Tulosta raportti
    migrator.generate_report()

if __name__ == "__main__":
    main()
