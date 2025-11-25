#!/bin/bash
# module_splitting_analyzer.sh - PÄIVITETTY: Analysoi Python-tiedostot modulaarista hajautusta varten

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
cat > "$REPORT_FILE" << DOC_EOF
# 📊 Modulaarisen Hajautuksen Analyysi
## 📅 Generoitu: $(date)

## 🏆 REFAKTOROIDUT TIEDOSTOT

DOC_EOF

# Listaa ensin refaktroidut tiedostot
REFACTORED_FILES=("manage_config.py" "manage_candidates.py")
for refactored in "${REFACTORED_FILES[@]}"; do
    if find "$PROJECT_ROOT/src" -name "$refactored" | grep -q .; then
        file=$(find "$PROJECT_ROOT/src" -name "$refactored" | head -1)
        line_count=$(wc -l < "$file" 2>/dev/null || echo "0")
        rel_path="${file#$PROJECT_ROOT/}"
        echo "### ✅ $rel_path ($line_count riviä) - REFAKTOROITU" >> "$REPORT_FILE"
        
        case "$refactored" in
            "manage_config.py")
                echo "- **Toteutettu**: 15 moduulia src/cli/config/ -kansiossa" >> "$REPORT_FILE"
                echo "- **Reduktio**: 311 → 24 riviä (92% pienempi)" >> "$REPORT_FILE"
                ;;
            "manage_candidates.py")
                echo "- **Toteutettu**: 7 moduulia src/cli/candidates/ -kansiossa" >> "$REPORT_FILE"
                echo "- **Reduktio**: 576 → 65 riviä (89% pienempi)" >> "$REPORT_FILE"
                ;;
        esac
        echo "" >> "$REPORT_FILE"
    fi
done

cat >> "$REPORT_FILE" << DOC_EOF
## 🚨 SUOSITELLUT TIEDOSTOT HAJAUTETTAVAKSI

DOC_EOF

# Analysoi jokainen tiedosto
for file in $PYTHON_FILES; do
    if [ -f "$file" ] && [ -s "$file" ]; then
        line_count=$(wc -l < "$file" 2>/dev/null || echo "0")
        filename=$(basename "$file")
        rel_path="${file#$PROJECT_ROOT/}"
        
        # Ohita jo refaktroidut tiedostot
        if [[ " ${REFACTORED_FILES[@]} " =~ " ${filename} " ]]; then
            continue
        fi
        
        # Tarkista onko tiedosto suuri
        if [ "$line_count" -gt 300 ]; then
            echo "### 🔴 $rel_path ($line_count riviä)" >> "$REPORT_FILE"
            
            # Ehdota hajautusta todistetuilla rakennemalleilla
            case "$filename" in
                "voting_engine.py")
                    echo "- **Ehdotus**: Hajauta core/voting/ -rakenteeseen" >> "$REPORT_FILE"
                    echo "  - managers/session_manager.py (VotingSessionManager)" >> "$REPORT_FILE"
                    echo "  - calculators/result_calculator.py (calculate_results)" >> "$REPORT_FILE"
                    echo "  - validators/vote_validator.py (validate_answer_value)" >> "$REPORT_FILE"
                    ;;
                "manage_questions.py")
                    echo "- **Ehdotus**: Hajauta src/cli/questions/ -rakenteeseen" >> "$REPORT_FILE"
                    echo "  - commands/add_command.py, list_command.py, update_command.py" >> "$REPORT_FILE"
                    echo "  - utils/question_manager.py (QuestionManager-luokka)" >> "$REPORT_FILE"
                    ;;
                "manage_answers.py")
                    echo "- **Ehdotus**: Hajauta src/cli/answers/ -rakenteeseen" >> "$REPORT_FILE"
                    echo "  - commands/submit_command.py, validate_command.py, list_command.py" >> "$REPORT_FILE"
                    echo "  - utils/answer_manager.py (AnswerManager-luokka)" >> "$REPORT_FILE"
                    ;;
                "sync_coordinator.py")
                    echo "- **Ehdotus**: Hajauta core/sync/ -rakenteeseen" >> "$REPORT_FILE"
                    echo "  - managers/sync_manager.py (SyncManager)" >> "$REPORT_FILE"
                    echo "  - orchestrators/coordinator.py (sync-toiminnallisuus)" >> "$REPORT_FILE"
                    ;;
                "install.py")
                    echo "- **Ehdotus**: Hajauta src/cli/install/ -rakenteeseen" >> "$REPORT_FILE"
                    echo "  - commands/setup_command.py, verify_command.py, init_command.py" >> "$REPORT_FILE"
                    echo "  - utils/install_manager.py (InstallManager-luokka)" >> "$REPORT_FILE"
                    ;;
                "quorum_manager.py")
                    echo "- **Ehdotus**: Hajauta src/managers/quorum/ -rakenteeseen" >> "$REPORT_FILE"
                    echo "  - consensus_manager.py, vote_tracker.py, result_calculator.py" >> "$REPORT_FILE"
                    ;;
                *)
                    echo "- **Ehdotus**: Hajauta loogisesti toiminnallisuuksien mukaan" >> "$REPORT_FILE"
                    echo "  - commands/ - CLI-komennot" >> "$REPORT_FILE"
                    echo "  - utils/ - Apufunktiot ja manager-luokat" >> "$REPORT_FILE"
                    echo "  - core/ - Ydinlogiikka (jos soveltuu)" >> "$REPORT_FILE"
                    ;;
            esac
            
            # Lisää tilastot ja arvio
            class_count=$(grep -c "^class " "$file" 2>/dev/null || echo "0")
            function_count=$(grep -c "^def " "$file" 2>/dev/null || echo "0")
            echo "- **Luokat**: $class_count, **Funktiot**: $function_count" >> "$REPORT_FILE"
            
            # Arvioi refaktoroinnin kesto
            if [ "$line_count" -gt 500 ]; then
                echo "- **Arvioitu aika**: 12-18 tuntia" >> "$REPORT_FILE"
            elif [ "$line_count" -gt 400 ]; then
                echo "- **Arvioitu aika**: 8-12 tuntia" >> "$REPORT_FILE"
            elif [ "$line_count" -gt 300 ]; then
                echo "- **Arvioitu aika**: 4-8 tuntia" >> "$REPORT_FILE"
            fi
            
            echo "" >> "$REPORT_FILE"
            
            echo "✅ $rel_path: $line_count riviä"
        fi
    fi
done

# Lisää loppuun parannetut ohjeet
cat >> "$REPORT_FILE" << DOC_EOF

## 💡 TODISTETUT HAJAUTUSSTRATEGIAT

### Malli 1: CLI-komennot (manage_*.py)
\`\`\`
src/cli/modulename/
├── __init__.py              # Päämoduuli (Click-komennot)
├── commands/
│   ├── add_command.py       # add-toiminto
│   ├── list_command.py      # list-toiminto
│   └── ...                  # Muut komennot
└── utils/
    ├── module_manager.py    # Manager-luokka
    └── validators.py        # Validointifunktiot
\`\`\`

### Malli 2: Core-logiikka (engine/*.py)  
\`\`\`
src/core/modulename/
├── managers/                # Manager-luokat
├── calculators/             # Laskentalogiikka
├── validators/              # Validointi
└── utils/                   # Apufunktiot
\`\`\`

### Malli 3: Manager-luokat (managers/*.py)
\`\`\`
src/managers/modulename/
├── core_manager.py          # Päälogiikka
├── data_manager.py          # Data-käsittely
└── network_manager.py       # Verkkotoiminnot
\`\`\`

## 🎯 SEURAAVAT ASKELEET

1. **Valitse kohde** - Aloita pienimmästä tai tärkeimmästä
2. **Luo rakenne** - commands/, utils/, core/ kansiot
3. **Testaa importit** - Ennen koodin siirtoa
4. **Siirrä funktiot** - Yksi kerrallaan, testaa jokainen
5. **Testaa kokonaisuus** - Varmista että CLI toimii
6. **Commitoi** - Pienet, hallittavat commitit

---

*Generoitu automaattisesti skriptillä \`module_splitting_analyzer.sh\`*
*Päivitetty: $(date +%d.%m.%Y) - Refaktoroinnin jälkeen*
DOC_EOF

echo ""
echo "✅ ANALYYSI VALMIS!"
echo "📄 Raportti: $REPORT_FILE"
echo ""
echo "🚀 SEURAAVAT VAIHEET:"
echo "1. Tarkastele raporttia"
echo "2. Valitse seuraava refaktoroitava tiedosto"
echo "3. Käytä todistettuja rakennemalleja"
echo "4. Aloita refaktorointi uudella branchilla"
