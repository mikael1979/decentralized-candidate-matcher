# 🎨 Template Editor - Käyttöohje

## Yleiskuvaus

Template Editor on työkalu, joka auttaa puolueita siirtämään olemassa olevat verkkosivunsa vaalijärjestelmään. Se analysoi HTML- ja CSS-tiedostoja ja luo automaattisesti JSON-templateja.

## 🔧 Asennus ja käyttö

### 1. Komentorivikäyttö

```bash
# Peruskäyttö
python -m src.tools.template_editor.editor --html polku/verkkosivu.html --css polku/tyylit.css

# Vain HTML (käyttää oletusteemoja)
python -m src.tools.template_editor.editor --html polku/verkkosivu.html

# Mukana esikatselu
python -m src.tools.template_editor.editor --html polku/verkkosivu.html --css polku/tyylit.css --preview

# Muuta output-hakemisto
python -m src.tools.template_editor.editor --html polku/verkkosivu.html --output omat_templatet
