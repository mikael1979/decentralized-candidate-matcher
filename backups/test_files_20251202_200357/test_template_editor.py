#!/usr/bin/env python3
"""
Testaa template-editorin toimintaa.
"""
import os
import tempfile
from pathlib import Path

# Luo testi HTML ja CSS tiedostot
test_html = """
<!DOCTYPE html>
<html lang="fi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Testi Puolue - Kotisivu</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header class="site-header">
        <div class="container">
            <h1 class="party-title">Testi Puolue</h1>
            <p class="slogan">Parempaa politiikkaa kaikille</p>
        </div>
    </header>
    
    <main class="main-content">
        <section class="platform">
            <h2>Poliittinen ohjelma</h2>
            <ul class="platform-list">
                <li>Koulutuksen kehittäminen</li>
                <li>Terveydenhuollon parantaminen</li>
                <li>Ympäristönsuojelu</li>
            </ul>
        </section>
        
        <section class="candidates">
            <h2>Ehdokkaat</h2>
            <div class="candidate-grid">
                <div class="candidate-card">
                    <h3>Matti Meikäläinen</h3>
                    <p class="profession">Opettaja</p>
                    <p class="theme">Koulutus kaikille</p>
                </div>
            </div>
        </section>
    </main>
    
    <footer class="site-footer">
        <div class="container">
            <p>&copy; 2024 Testi Puolue. Kaikki oikeudet pidätetään.</p>
        </div>
    </footer>
</body>
</html>
"""

test_css = """
/* Perustyylit */
:root {
    --primary-color: #2c3e50;
    --secondary-color: #3498db;
    --accent-color: #e74c3c;
    --background-color: #ecf0f1;
    --text-color: #2c3e50;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: var(--text-color);
    background-color: var(--background-color);
    margin: 0;
    padding: 0;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* Header */
.site-header {
    background-color: var(--primary-color);
    color: white;
    padding: 2rem 0;
    text-align: center;
}

.party-title {
    font-size: 2.5rem;
    margin: 0;
    color: white;
}

.slogan {
    font-size: 1.2rem;
    font-style: italic;
    margin: 0.5rem 0 0 0;
    color: #bdc3c7;
}

/* Main content */
.main-content {
    padding: 2rem 0;
}

.platform h2,
.candidates h2 {
    color: var(--primary-color);
    border-bottom: 2px solid var(--secondary-color);
    padding-bottom: 0.5rem;
}

.platform-list {
    list-style: none;
    padding: 0;
}

.platform-list li {
    background: white;
    margin: 0.5rem 0;
    padding: 1rem;
    border-radius: 5px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

/* Candidate cards */
.candidate-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1rem;
}

.candidate-card {
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    border-left: 4px solid var(--accent-color);
}

.candidate-card h3 {
    margin: 0 0 0.5rem 0;
    color: var(--primary-color);
}

.profession {
    font-weight: bold;
    color: var(--secondary-color);
    margin: 0;
}

.theme {
    font-style: italic;
    margin: 0.5rem 0 0 0;
}

/* Footer */
.site-footer {
    background-color: var(--primary-color);
    color: white;
    padding: 1rem 0;
    text-align: center;
    margin-top: 2rem;
}

/* Responsiivisuus */
@media (max-width: 768px) {
    .container {
        padding: 0 10px;
    }
    
    .party-title {
        font-size: 2rem;
    }
    
    .candidate-grid {
        grid-template-columns: 1fr;
    }
}
"""

def test_template_editor():
    """Testaa template-editorin perustoimintoja."""
    print("🧪 TESTAA TEMPLATE-EDITORIA")
    print("=" * 50)
    
    # Luo väliaikaiset tiedostot
    with tempfile.TemporaryDirectory() as temp_dir:
        html_file = Path(temp_dir) / "test_site.html"
        css_file = Path(temp_dir) / "styles.css"
        
        # Kirjoita testitiedostot
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(test_html)
        
        with open(css_file, 'w', encoding='utf-8') as f:
            f.write(test_css)
        
        print(f"📁 Luotiin testitiedostot: {temp_dir}")
        
        # Testaa template-editoria
        try:
            from src.tools.template_editor.editor import TemplateEditor
            
            editor = TemplateEditor()
            
            print("\n🎨 LUODAAN TEMPLATE TESTIVERKKOSIVUSTA...")
            result = editor.create_template_from_website(
                html_file=str(html_file),
                css_file=str(css_file),
                output_dir=temp_dir
            )
            
            # Tarkista tulokset
            templates = result.get('templates', {})
            analysis = result.get('analysis', {})
            
            print(f"\n📊 TULOKSET:")
            print(f"✅ Generoitu templatet: {len(templates)}")
            
            for template_name, template_data in templates.items():
                if template_data:
                    print(f"  - {template_name}: {template_data.get('template_name')}")
            
            # Tarkista HTML-analyysi
            html_analysis = analysis.get('html', {})
            if html_analysis:
                structure = html_analysis.get('structure', {})
                print(f"📄 HTML-analyysi:")
                print(f"  - Otsikoita: {len(structure.get('headings', []))}")
                print(f"  - Osia: {len(html_analysis.get('sections', {}))}")
            
            # Tarkista CSS-analyysi
            css_analysis = analysis.get('css', {})
            if css_analysis:
                colors = css_analysis.get('colors', {})
                print(f"🎨 CSS-analyysi:")
                print(f"  - Värejä: {sum(len(v) for v in colors.values())}")
            
            # Testaa esikatselu
            if 'party_profile' in templates:
                print(f"\n👁️  TESTAA ESIKATSELU:")
                preview = editor.preview_template(templates['party_profile'])
                print(f"Esikatselu pituus: {len(preview)} merkkiä")
                print("Ensimmäiset 200 merkkiä:")
                print(preview[:200] + "...")
            
            print("\n🎉 TEMPLATE-EDITORI TOIMII!")
            return True
            
        except Exception as e:
            print(f"❌ Template-editor testi epäonnistui: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = test_template_editor()
    exit(0 if success else 1)
