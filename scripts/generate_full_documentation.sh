#!/bin/bash

# Master-skripti joka generoi sekä koodin että templatejen dokumentaation
# Käyttö: ./scripts/generate_full_documentation.sh

set -e

echo "📚 GENEROI KOKO DOKUMENTAATIO"
echo "=============================="

# Varmista että olet oikeassa hakemistossa
if [ ! -d "src" ] || [ ! -d "base_templates" ]; then
    echo "❌ Virhe: Suorita skripti projektin juurihakemistosta"
    exit 1
fi

# Tarkista riippuvuudet
if ! command -v jq &> /dev/null; then
    echo "❌ Asenna jq: sudo apt-get install jq"
    exit 1
fi

# Luo docs-hakemisto
mkdir -p docs

# Generoi koodin dokumentaatio
echo ""
echo "🔍 Generoidaan koodin yleiskuva..."
chmod +x scripts/generate_code_overview.sh
./scripts/generate_code_overview.sh

# Generoi template dokumentaatio  
echo ""
echo "📋 Generoidaan template-listaus..."
chmod +x scripts/generate_template_overview.sh
./scripts/generate_template_overview.sh

# Luo yhteinen index
echo ""
echo "📇 Luodaan pääindeksi..."

INDEX_FILE="docs/documentation_index_$(date +%Y%m%d_%H%M%S).md"

cat > "$INDEX_FILE" << EOF
# 🏛️ Hajautetun Vaalikoneen Dokumentaatio

## 📅 Generoitu: $(date)

## 🔗 Linkit

- [Koodin Yleiskuva](./$(basename $(ls -t docs/code_overview_*.txt | head -1)))
- [Template Listaus](./$(basename $(ls -t docs/template_overview_*.json | head -1)))

## 📊 Yhteenveto

### Koodikanta
\`\`\`
$(find src -name "*.py" | wc -l) Python-tiedostoa
$(find src -name "*.py" -exec wc -l {} + | tail -1 | awk '{print $1}') koodiriviä
\`\`\`

### Templatet
\`\`\`
$(find base_templates -name "*.json" | wc -l) JSON-templatea
$(ls -d base_templates/*/ | wc -l) kategoriaa
\`\`\`

## 🗂️ Hakemistorakenne

\`\`\`
$(tree -I '__pycache__|*.pyc|docs' --dirsfirst)
\`\`\`

## 🚪 Nopeat Linkit

- [Asenna Järjestelmä](./scripts/setup_jumaltenvaalit.sh)
- [Hallitse Kysymyksiä](./src/cli/manage_questions.py) 
- [Hallitse Ehdokkaita](./src/cli/manage_candidates.py)
EOF

echo "✅ Kaikki dokumentaatio generoitu!"
echo ""
echo "📁 Luodut tiedostot:"
ls -la docs/*_$(date +%Y%m%d)*
echo ""
echo "🌐 Pääindeksi: $INDEX_FILE"
