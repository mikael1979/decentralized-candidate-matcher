#!/bin/bash
# module_splitting_analyzer.sh - Analysoi Python-tiedostot ja suosittelee modulaarista hajautusta

set -e

echo "🔍 ANALYSOIDAAN PYTHON-TIEDOSTOJA MODUULAARISEKSI HAJAUTUKSEKSI"
echo "==============================================================="

PROJECT_ROOT="${1:-$(pwd)}"

if [ ! -d "$PROJECT_ROOT/src" ]; then
    echo "❌ Virhe: src-hakemistoa ei löydy polusta: $PROJECT_ROOT"
    echo "Käyttö: $0 [projektin_polku]"
    exit 1
fi

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="$PROJECT_ROOT/docs/module_splitting_analysis_${TIMESTAMP}.md"

echo "📁 Projektin juuri: $PROJECT_ROOT"
echo "📄 Raportti: $REPORT_FILE"

mkdir -p "$PROJECT_ROOT/docs"

# Etsi Python-tiedostot
PYTHON_FILES=$(find "$PROJECT_ROOT/src" -name "*.py" -type f)

if [ -z "$PYTHON_FILES" ]; then
    echo "❌ Yhtään Python-tiedostoa ei löytynyt src-hakemistosta!"
    exit 1
fi

echo "📊 Löydetty $(echo "$PYTHON_FILES" | wc -l) Python-tiedostoa"

# Luo raportti
cat > "$REPORT_FILE" << EOF
# 📊 Modulaarisen Hajautuksen Analyysi
## 📅 Generoitu: $(date)

## 🚨 SUOSITELLUT TIEDOSTOT HAJAUTETTAVAKSI

EOF

# Analysoi jokainen tiedosto
for file in $PYTHON_FILES; do
    if [ -f "$file" ] && [ -s "$file" ]; then
        line_count=$(wc -l < "$file" 2>/dev/null || echo "0")
        filename=$(basename "$file")
        rel_path="${file#$PROJECT_ROOT/}"
        
        # Tarkista onko tiedosto suuri
        if [ "$line_count" -gt 300 ]; then
            echo "### 🔴 $rel_path ($line_count riviä)" >> "$REPORT_FILE"
            
            # Ehdota hajautusta tiedoston nimen perusteella
            case "$filename" in
                "manage_config.py")
                    echo "- **Ehdotus**: Hajauta config_proposals.py, config_voting.py, config_display.py" >> "$REPORT_FILE"
                    ;;
                "manage_parties.py")
                    echo "- **Ehdotus**: Hajauta party_commands.py, party_verification.py, party_analytics.py" >> "$REPORT_FILE"
                    ;;
                "manage_questions.py")
                    echo "- **Ehdotus**: Hajauta question_commands.py, question_manager.py, question_validation.py" >> "$REPORT_FILE"
                    ;;
                "manage_candidates.py")
                    echo "- **Ehdotus**: Hajauta candidate_commands.py, candidate_manager.py, candidate_verification.py" >> "$REPORT_FILE"
                    ;;
                "manage_answers.py")
                    echo "- **Ehdotus**: Hajauta answer_commands.py, answer_manager.py, answer_validation.py" >> "$REPORT_FILE"
                    ;;
                "voting_engine.py")
                    echo "- **Ehdotus**: Hajauta voting_core.py, session_manager.py, results_calculator.py" >> "$REPORT_FILE"
                    ;;
                "ipfs_sync.py")
                    echo "- **Ehdotus**: Hajauta sync_orchestrator.py, delta_manager.py, archive_manager.py" >> "$REPORT_FILE"
                    ;;
                "template_manager.py")
                    echo "- **Ehdotus**: Hajauta template_commands.py, template_generator.py, template_validator.py" >> "$REPORT_FILE"
                    ;;
                *)
                    echo "- **Ehdotus**: Hajauta loogisesti toiminnallisuuksien mukaan" >> "$REPORT_FILE"
                    ;;
            esac
            
            # Lisää tilastot
            class_count=$(grep -c "^class " "$file" 2>/dev/null || echo "0")
            function_count=$(grep -c "^def " "$file" 2>/dev/null || echo "0")
            echo "- **Luokat**: $class_count, **Funktiot**: $function_count" >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
            
            echo "✅ $rel_path: $line_count riviä"
        fi
    fi
done

# Lisää loppuun yleiset ohjeet
cat >> "$REPORT_FILE" << EOF

## 💡 HAJAUTUSSTRATEGIA

### Esimerkki: manage_config.py → modulaarinen rakenne
\`\`\`
src/cli/config_commands.py      # Peruskomennot (propose, vote, status)
src/cli/config_voting.py        # Äänestyslogiikka
src/cli/config_display.py       # Tulostusten formatointi
src/managers/config_manager.py  # Ydinlogiikka
\`\`\`

## 🎯 SEURAAVAT ASKELEET

1. Valitse ensimmäinen tiedosto hajautettavaksi
2. Toteuta hajautus moduuli kerrallaan
3. Testaa että kaikki toimii
4. Päivitä dokumentaatio

---

*Generoitu automaattisesti skriptillä \`module_splitting_analyzer.sh\`*
EOF

echo ""
echo "✅ ANALYYSI VALMIS!"
echo "📄 Raportti: $REPORT_FILE"
echo ""
echo "🚀 SEURAAVAT VAIHEET:"
echo "1. Tarkastele raporttia"
echo "2. Aloita manage_config.py hajautuksesta"
echo "3. Toteuta moduuli kerrallaan"
