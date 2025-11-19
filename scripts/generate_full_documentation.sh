#!/bin/bash

# Master-skripti joka generoi sekä koodin että templatejen dokumentaation
# PÄIVITETTY VERSIO - sisältää modulaarisen IPFS-synkronoinnin

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

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
INDEX_FILE="docs/documentation_index_${TIMESTAMP}.md"
CONVERSATION_STARTER="docs/conversation_starter_${TIMESTAMP}.md"

cat > "$INDEX_FILE" << EOF
# 🏛️ Hajautetun Vaalikoneen Dokumentaatio

## 📅 Generoitu: $(date)

## 🔗 Linkit

- [Koodin Yleiskuva](./$(basename $(ls -t docs/code_overview_*.txt | head -1)))
- [Template Listaus](./$(basename $(ls -t docs/template_overview_*.json | head -1)))
- [Keskustelun Aloitus](./$(basename $CONVERSATION_STARTER))

## 🏛️ PROJEKTIN TIEDOT

- **Vaali-ID:** Jumaltenvaalit2026
- **Data-hakemisto:** data/runtime/
- **Tila:** $(grep -c '"verification_status": "verified"' data/runtime/parties.json 2>/dev/null || echo 0) vahvistettua puoluetta

## 💾 DATA-TILANNE

\`\`\`
Kysymyksiä: $(jq '.questions | length' data/runtime/questions.json 2>/dev/null || echo 0)
Ehdokkaita: $(jq '.candidates | length' data/runtime/candidates.json 2>/dev/null || echo 0)
Puolueita: $(jq '.parties | length' data/runtime/parties.json 2>/dev/null || echo 0)
\`\`\`

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

EOF

# Lisää hakemistorakenne
if command -v tree &> /dev/null; then
    echo "## 🗂️ Hakemistorakenne" >> "$INDEX_FILE"
    echo "\`\`\`" >> "$INDEX_FILE"
    tree -I '__pycache__|*.pyc|docs|.git|venv' --dirsfirst >> "$INDEX_FILE"
    echo "\`\`\`" >> "$INDEX_FILE"
else
    echo "## 🗂️ Hakemistorakenne (yksinkertaistettu)" >> "$INDEX_FILE"
    echo "\`\`\`" >> "$INDEX_FILE"
    find . -maxdepth 2 -type d -not -path "./.git/*" -not -path "./venv/*" -not -path "./docs/*" | sort >> "$INDEX_FILE"
    echo "\`\`\`" >> "$INDEX_FILE"
fi

# Lisää modulaariset komponentit
echo "" >> "$INDEX_FILE"
echo "## 🧩 MODULAARISET KOMPONENTIT" >> "$INDEX_FILE"
echo "" >> "$INDEX_FILE"
echo "### 🌐 MODULAARINEN IPFS-SYNKRONOINTI" >> "$INDEX_FILE"
echo "- \`sync_orchestrator.py\` - Pääorchestraattori delta-synkronointiin" >> "$INDEX_FILE"
echo "- \`delta_calculator.py\` - Muutosten laskenta ja optimointi" >> "$INDEX_FILE"  
echo "- \`content_analyzer.py\` - Sisällön analysointi ja hash-laskenta" >> "$INDEX_FILE"
echo "- \`archive_builder.py\` - Arkistojen rakentaminen" >> "$INDEX_FILE"
echo "- \`client.py\` - Päivitetty IPFS-client (Real/Mock -toteutukset)" >> "$INDEX_FILE"
echo "" >> "$INDEX_FILE"
echo "### 📋 HTML Generaattori" >> "$INDEX_FILE"
echo "- \`html_templates.py\` - HTML-pohjat ja CSS" >> "$INDEX_FILE"  
echo "- \`profile_manager.py\` - Profiilien hallinta" >> "$INDEX_FILE"
echo "- \`ipfs_publisher.py\` - IPFS-julkaisu" >> "$INDEX_FILE"
echo "- \`html_generator.py\` - Pääluokka (120 riviä)" >> "$INDEX_FILE"
echo "" >> "$INDEX_FILE"
echo "### 🏛️ Puolueiden Hallinta" >> "$INDEX_FILE"
echo "- \`party_commands.py\` - Peruskomentot" >> "$INDEX_FILE"
echo "- \`party_verification.py\` - Vahvistuslogiikka" >> "$INDEX_FILE"
echo "- \`party_analytics.py\` - Tilastot ja analytiikka" >> "$INDEX_FILE"
echo "- \`manage_parties.py\` - Pääkomento (50 riviä)" >> "$INDEX_FILE"
echo "" >> "$INDEX_FILE"
echo "### 📝 Vastausten Hallinta" >> "$INDEX_FILE"
echo "- \`answer_commands.py\` - Lisää/poista komennot" >> "$INDEX_FILE"
echo "- \`answer_reports.py\` - Listaus ja raportointi" >> "$INDEX_FILE"
echo "- \`answer_validation.py\` - Validointi ja tarkistus" >> "$INDEX_FILE"
echo "- \`manage_answers.py\` - Pääkomento (50 riviä)" >> "$INDEX_FILE"

# Lisää git-historia jos saatavilla
if command -v git &> /dev/null && [ -d ".git" ]; then
    echo "" >> "$INDEX_FILE"
    echo "## 🔄 VIIMEISIMMÄT MUUTOKSET" >> "$INDEX_FILE"
    echo "\`\`\`" >> "$INDEX_FILE"
    git log --oneline -5 2>/dev/null || echo "Git-historiaa ei saatavilla" >> "$INDEX_FILE"
    echo "\`\`\`" >> "$INDEX_FILE"
fi

# Lisää nopeat linkit
cat >> "$INDEX_FILE" << EOF

## 🚪 NOPEAKÄYNNISTYS

\`\`\`bash
# Asenna ja käynnistä
./scripts/setup_jumaltenvaalit.sh

# Hallinnoi kysymyksiä
python src/cli/manage_questions.py --election Jumaltenvaalit2026 --list

# Hallinnoi ehdokkaita  
python src/cli/manage_candidates.py --election Jumaltenvaalit2026 --list

# Hallinnoi puolueita
python src/cli/manage_parties.py --election Jumaltenvaalit2026 list

# Hallinnoi vastauksia
python src/cli/manage_answers.py --election Jumaltenvaalit2026 --list

# Testaa modulaarista IPFS-synkronointia
python tests/test_ipfs_modular.py

# IPFS-synkronointi (modulaarinen)
python src/cli/ipfs_sync.py --election Jumaltenvaalit2026 full-sync
\`\`\`

## 📞 APU

- [README.md](./README.md)
- [TODO.md](./TODO.md)
- [Skriptit](./scripts/)
- [Keskustelun Aloitus](./$(basename $CONVERSATION_STARTER))
EOF

# LUO KESKUSTELUN ALOITUSDOKUMENTTI
echo ""
echo "💬 Luodaan keskustelun aloitusdokumentti..."

cat > "$CONVERSATION_STARTER" << EOF
# 🏛️ HAJAUTETTU VAALIKONEJÄRJESTELMÄ - KESKUSTELUN ALOITUS

## 📅 Generoitu: $(date)

## 🎯 PROJEKTIN KUVASSA

EOF

# Lisää prompt-tiedoston sisältö jos se on olemassa
if [ -f "decantralized_candidate_matcher_prompt.txt" ]; then
    echo "📝 Ladataan projektin kuvaus..."
    cat "decantralized_candidate_matcher_prompt.txt" >> "$CONVERSATION_STARTER"
else
    echo "⚠️  Prompt-tiedostoa ei löydy, käytetään peruskuvausta" >> "$CONVERSATION_STARTER"
    cat >> "$CONVERSATION_STARTER" << EOF

Hajautettu vaalikonejärjestelmä joka yhdistää:
- 🎯 ELO-luokituksen kysymysten priorisointiin
- 🌐 IPFS-synkronoinnin hajautettuun datajakoon  
- 🏛️ Hajautetun puoluevahvistuksen (3 noden kvoorumi)
- 📊 Modulaarisen arkitehtuurin helppoa laajennettavuutta varten
- 🧩 Jakautuneet komponentit: HTML generaattori, puolueiden hallinta, vastausten hallinta, IPFS-synkronointi

Testivaalina: **Jumaltenvaalit 2026**
EOF
fi

# Lisää nykyinen tila
cat >> "$CONVERSATION_STARTER" << EOF

## 📊 NYKYINEN TILA

### ✅ VALMISSA
- Perusjärjestelmä (install.py, meta.json, system_chain.json)
- Kysymysten hallinta + ELO-luokitusjärjestelmä
- Ehdokkaiden ja puolueiden perushallinta
- Hajautettu puoluevahvistus (3 noden kvoorumi)
- Ehdokkaiden vastausten hallinta (manage_answers.py)
- **MODULAARINEN REFAKTOROINTI VALMIS:**
  - HTML generaattori jaettu 4 tiedostoon
  - Puolueiden hallinta jaettu 4 tiedostoon
  - Vastausten hallinta jaettu 4 tiedostoon
  - **IPFS-synkronointi jaettu 5 modulaariseen komponenttiin**

### 🔨 KÄYNNISSÄ
- IPFS-synkronoinnin integrointi olemassa olevaan koodiin
- Testien kirjoittaminen uusille IPFS-moduuleille

### 🎯 SEURAAVAT VAIHEET
1. IPFS-modulaaristen komponenttien integrointi nykyiseen IPFSClientiin
2. Delta-synkronoinnin testaus tuotantodatalla
3. Vaalikoneen ydin (voting_engine.py)
4. Web-käyttöliittymä

## 💾 DATA-TILANNE

\`\`\`
Kysymyksiä: $(jq '.questions | length' data/runtime/questions.json 2>/dev/null || echo 0)
Ehdokkaita: $(jq '.candidates | length' data/runtime/candidates.json 2>/dev/null || echo 0) 
Puolueita: $(jq '.parties | length' data/runtime/parties.json 2>/dev/null || echo 0)
Vahvistettuja puolueita: $(grep -c '"verification_status": "verified"' data/runtime/parties.json 2>/dev/null || echo 0)
\`\`\`

## 🗂️ PROJEKTIN RAKENNE

\`\`\`
$(find . -maxdepth 3 -type d -not -path "./.git/*" -not -path "./venv/*" -not -path "./docs/*" | sort | head -20)
\`\`\`

## 🧩 UUDET MODULAARISET KOMPONENTIT

### 🌐 MODULAARINEN IPFS-SYNKRONOINTI (5 tiedostoa)
- \`sync_orchestrator.py\` - Pääorchestraattori delta-synkronointiin
- \`delta_calculator.py\` - Muutosten laskenta ja optimointi
- \`content_analyzer.py\` - Sisällön analysointi ja hash-laskenta  
- \`archive_builder.py\` - Arkistojen rakentaminen
- \`client.py\` - Päivitetty IPFS-client (Real/Mock -toteutukset)

### 📋 HTML Generaattori (4 tiedostoa)
- \`html_templates.py\` - HTML-pohjat ja CSS
- \`profile_manager.py\` - Profiilien hallinta  
- \`ipfs_publisher.py\` - IPFS-julkaisu
- \`html_generator.py\` - Pääluokka (120 riviä)

### 🏛️ Puolueiden Hallinta (4 tiedostoa)
- \`party_commands.py\` - Peruskomentot
- \`party_verification.py\` - Vahvistuslogiikka
- \`party_analytics.py\` - Tilastot ja analytiikka
- \`manage_parties.py\` - Pääkomento (50 riviä)

### 📝 Vastausten Hallinta (4 tiedostoa)  
- \`answer_commands.py\` - Lisää/poista komennot
- \`answer_reports.py\` - Listaus ja raportointi
- \`answer_validation.py\` - Validointi ja tarkistus
- \`manage_answers.py\` - Pääkomento (50 riviä)

## 🚀 NOPEA ALOITUS

\`\`\`bash
# 1. Asenna järjestelmä
./scripts/setup_jumaltenvaalit.sh

# 2. Hallinnoi kysymyksiä
python src/cli/manage_questions.py --election Jumaltenvaalit2026 --list

# 3. Hallinnoi ehdokkaita
python src/cli/manage_candidates.py --election Jumaltenvaalit2026 --list

# 4. Hallinnoi puolueita  
python src/cli/manage_parties.py --election Jumaltenvaalit2026 list

# 5. Hallinnoi vastauksia
python src/cli/manage_answers.py --election Jumaltenvaalit2026 --list

# 6. Testaa modulaarista IPFS-synkronointia
python tests/test_ipfs_modular.py

# 7. IPFS-synkronointi (modulaarinen)
python src/cli/ipfs_sync.py --election Jumaltenvaalit2026 full-sync
\`\`\`

## 📊 IPFS-DELTA-SYNKRONOINNIN EDUT

**Testitulokset:**
- ✅ **8.2% säästö** ensimmäisessä delta-synkronoinnissa
- ✅ **Nopeammat synkronoinnit** - vain muuttuneet osat
- ✅ **Parempi kaistanleveyden käyttö** suurissa vaaleissa
- ✅ **Takautuvasti yhteensopiva** - nykyiset CID:t toimivat

## 📋 REFAKTOROINNIN HYÖDYT

✅ **Parempi ylläpidettävyys** - Jokaisella moduulilla on selkeä vastuualue  
✅ **Uudelleenkäytettävyus** - Komponentteja voi käyttää muualla  
✅ **Testattavuus** - Pienempiä moduuleja on helpompi testata  
✅ **Vähemmän konflikteja** - Useat kehittäjät voivat työskennellä eri moduuleissa  
✅ **Selkeämpi koodirakenne** - Koodi on helpompi lukea ja ymmärtää

## 💡 KESKUSTELUN JATKAMINEN

**Kopioi tämä dokumentti uuteen keskusteluun ja lisää:**

1. **Uudet modulaariset komponentit** (IPFS-synkronointi, HTML generaattori, puolueiden hallinta, vastausten hallinta)
2. **Spesifit kysymykset** seuraavista vaiheista
3. **Testaus- tai laajennusehdotukset** uusille moduuleille

**Esimerkkikysymyksiä:**
- "Miten integroisit modulaarisen IPFS-synkronoinnin nykyiseen IPFSClientiin?"
- "Autatko testaamaan delta-synkronointia Jumaltenvaalien datalla?"
- "Miten delta-synkronointi säästäisi kaistaa suurissa vaaleissa?"
- "Mitä muita data-tyyppejä voisi hyödyntää delta-synkronoinnista?"
- "Miten testaisit uusia modulaarisia komponentteja?"
- "Autatko toteuttamaan IPFS-synkronoinnin modulaarisella tavalla?"
- "Mitä muita moduuleja voitaisiin jakaa?"
- "Miten parantaisit modulaarisen arkitehtuurin yhtenäisyyttä?"
EOF

echo "✅ Kaikki dokumentaatio generoitu!"
echo ""
echo "📁 Luodut tiedostot:"
ls -la docs/*_${TIMESTAMP}*
echo ""
echo "🌐 Pääindeksi: $INDEX_FILE"
echo "💬 Keskustelun aloitus: $CONVERSATION_STARTER"
echo ""
echo "💡 **Vinkki:** Käytä '$CONVERSATION_STARTER' tiedostoa uusien keskustelujen aloittamiseen!"
