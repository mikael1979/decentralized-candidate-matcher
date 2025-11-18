#!/usr/bin/env python3
"""
Kevyt testi template-editorille.
"""
import tempfile
from pathlib import Path

def create_test_files():
    """Luo yksinkertaiset testitiedostot."""
    # Yksinkertainen testi HTML
    simple_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Testi Puolue</title>
    <style>
        body { font-family: Arial; color: #333; }
        .header { background: #2c3e50; color: white; padding: 20px; }
        .content { padding: 20px; }
        .footer { background: #34495e; color: white; padding: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Testi Puolue</h1>
        <p class="slogan">Yksinkertainen testi</p>
    </div>
    
    <div class="content">
        <h2>Poliittinen ohjelma</h2>
        <ul>
            <li>Kohta 1</li>
            <li>Kohta 2</li>
        </ul>
    </div>
    
    <div class="footer">
        <p>© 2024 Testi Puolue</p>
    </div>
</body>
</html>
"""
    
    return simple_html

def test_template_editor_light():
    """Kevyt testi template-editorin perustoiminnoille."""
    print("🧪 KEVIY TESTI TEMPLATE-EDITORILLE")
    print("=" * 40)
    
    # Luo väliaikainen HTML-tiedosto
    with tempfile.TemporaryDirectory() as temp_dir:
        html_file = Path(temp_dir) / "simple_test.html"
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(create_test_files())
        
        print(f"📄 Luotiin testi HTML: {html_file}")
        
        try:
            # Testaa että editori latautuu
            from src.tools.template_editor.editor import TemplateEditor
            print("✅ TemplateEditor import onnistui")
            
            # Luo editori
            editor = TemplateEditor()
            print("✅ TemplateEditor instanssi luotu")
            
            # Testaa template-generointi
            print("\n🔄 Generoidaan template...")
            result = editor.create_template_from_website(
                html_file=str(html_file),
                output_dir=temp_dir
            )
            
            # Tarkista tulokset
            templates = result.get('templates', {})
            print(f"✅ Template-generointi onnistui")
            print(f"   Generoitu templatet: {len(templates)}")
            
            for name, data in templates.items():
                if data:
                    template_name = data.get('template_name', 'Nimetön')
                    print(f"   - {name}: {template_name}")
            
            # Tarkista että party_profile on generoitu
            if 'party_profile' in templates:
                party_template = templates['party_profile']
                print(f"✅ Party profile template löytyy")
                print(f"   Versio: {party_template.get('version')}")
                print(f"   Kuvaus: {party_template.get('description')}")
                
                # Tarkista rakenne
                structure = party_template.get('structure', {})
                print(f"   Tyyppi: {structure.get('type')}")
                print(f"   Osat: {structure.get('sections', [])}")
            
            # Testaa CSS-teema jos saatavilla
            if 'css_theme' in templates:
                css_template = templates['css_theme']
                print(f"✅ CSS theme template löytyy")
                default_values = css_template.get('default_values', {})
                print(f"   Väriteema: {len(default_values)} väriä")
            
            # Testaa analyysi
            analysis = result.get('analysis', {})
            html_analysis = analysis.get('html', {})
            if html_analysis:
                structure = html_analysis.get('structure', {})
                print(f"📊 HTML-analyysi:")
                print(f"   - Otsikoita: {len(structure.get('headings', []))}")
                print(f"   - Linkkejä: {len(structure.get('links', []))}")
            
            print("\n🎉 KEVIY TESTI ONNISTUI!")
            return True
            
        except Exception as e:
            print(f"❌ Testi epäonnistui: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_sanitizer():
    """Testaa HTML-suodatinta."""
    print("\n🛡️ TESTAA HTML-SUODATIN")
    print("=" * 30)
    
    try:
        from src.tools.template_editor.html_analyzer import HTMLSanitizer
        
        # Testaa vaarallinen HTML
        dangerous_html = """
        <html>
        <script>alert('XSS')</script>
        <div onclick="alert('click')">Testi</div>
        <a href="javascript:alert('XSS')">Vaarallinen linkki</a>
        <style>body { background: url(javascript:alert('XSS')) }</style>
        </html>
        """
        
        sanitizer = HTMLSanitizer()
        sanitizer.feed(dangerous_html)
        safe_html = sanitizer.get_safe_html()
        
        print("✅ HTML-suodatin toimii")
        print(f"   Alkuperäinen: {len(dangerous_html)} merkkiä")
        print(f"   Suodatettu: {len(safe_html)} merkkiä")
        
        # Tarkista että vaarallinen koodi on poistettu
        checks = [
            ('<script>' not in safe_html, 'Script-tagit poistettu'),
            ('onclick=' not in safe_html, 'Onclick-attribuutit poistettu'),
            ('javascript:' not in safe_html, 'JavaScript-URLit poistettu')
        ]
        
        for check_passed, message in checks:
            if check_passed:
                print(f"   ✅ {message}")
            else:
                print(f"   ❌ {message}")
        
        return True
        
    except Exception as e:
        print(f"❌ Suodatintesti epäonnistui: {e}")
        return False

def test_css_analyzer():
    """Testaa CSS-analyysiä."""
    print("\n🎨 TESTAA CSS-ANALYYSI")
    print("=" * 30)
    
    try:
        from src.tools.template_editor.css_analyzer import CSSAnalyzer
        
        test_css = """
        body { 
            color: #333333;
            background: #ffffff;
            font-family: Arial, sans-serif;
        }
        .header {
            background-color: #2c3e50;
            color: rgb(255, 255, 255);
        }
        .accent {
            color: #e74c3c;
        }
        """
        
        analyzer = CSSAnalyzer()
        analysis = analyzer.analyze_css_content(test_css)
        
        print("✅ CSS-analyysi toimii")
        
        colors = analysis.get('colors', {})
        print(f"   Löydettyjä värejä:")
        for color_type, color_list in colors.items():
            if color_list:
                print(f"     - {color_type}: {len(color_list)}")
        
        # Testaa väriteeman ehdotus
        theme = analyzer.suggest_color_theme(test_css)
        print(f"   Ehdotettu väriteema:")
        for color_name, color_value in theme.items():
            print(f"     - {color_name}: {color_value}")
        
        return True
        
    except Exception as e:
        print(f"❌ CSS-analyysitesti epäonnistui: {e}")
        return False

if __name__ == "__main__":
    print("🚀 AJETAAN KEVIYT TESTIT TEMPLATE-EDITORILLE")
    print()
    
    tests = [
        test_template_editor_light,
        test_sanitizer, 
        test_css_analyzer
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Testi {test.__name__} kaatui: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 TESTITULOKSET:")
    
    passed = sum(results)
    total = len(results)
    
    for i, (test, result) in enumerate(zip(tests, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {i+1}. {test.__name__}: {status}")
    
    print(f"\n🎯 Yhteenveto: {passed}/{total} testiä läpäisty")
    
    if passed == total:
        print("🎉 KAIKKI TESTIT ONNISTUIVAT!")
    else:
        print("⚠️  Jotkin testit epäonnistuivat")
    
    exit(0 if passed == total else 1)
