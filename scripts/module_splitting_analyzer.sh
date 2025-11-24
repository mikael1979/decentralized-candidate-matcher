#!/bin/bash
# module_splitting_analyzer.sh - Analysoi Python-tiedostot ja suosittelee modulaarista hajautusta

set -euo pipefail

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
SUMMARY_FILE="$PROJECT_ROOT/docs/module_splitting_summary_${TIMESTAMP}.txt"

echo "📁 Projektin juuri: $PROJECT_ROOT"
echo "📄 Raportti: $REPORT_FILE"

mkdir -p "$PROJECT_ROOT/docs"

cat > "$REPORT_FILE" << EOF
# 📊 Modulaarisen Hajautuksen Analyysi

## 📅 Generoitu: $(date)
## 🏛️ Projekti: Hajautettu Vaalikone

Tämä analyysi tunnistaa Python-tiedostot, jotka ovat:
- Liian pitkiä (>300 riviä)
- Sisältävät useita luokkia tai toiminnallisuuksia
- Voisivat hyötyä modulaarisesta hajautuksesta

## 📈 YHTEENVETO TILASTOJA

| Metriikka | Arvo |
|-----------|------|
EOF

PYTHON_FILES=$(find "$PROJECT_ROOT/src" -name "*.py" -type f | sort)

if [ -z "$PYTHON_FILES" ]; then
    echo "❌ Yhtään Python-tiedostoa ei löytynyt src-hakemistosta!"
    exit 1
fi

TOTAL_FILES=0
TOTAL_LINES=0
FILES_OVER_300=0
FILES_OVER_500=0
FILES_OVER_700=0
COMPLEX_FILES=0

TEMP_FILE=$(mktemp)

while IFS= read -r file; do
    if [ -f "$file" ] && [ -s "$file" ]; then
        # Turvallinen rivimäärän laskenta
        line_count=$(wc -l < "$file" | tr -d ' ')
        line_count=${line_count:-0}
        
        # Turvallinen luokkien ja funktioiden laskenta
        class_count=$(grep -c "^class " "$file" 2>/dev/null || echo 0)
        class_count=${class_count:-0}
        function_count=$(grep -c "^def " "$file" 2>/dev/null || echo 0)
        function_count=${function_count:-0}
        total_functions=$((class_count + function_count))
        
        # Importtien laskenta
        import_count=$(grep -E "^(import|from)" "$file" 2>/dev/null | wc -l)
        import_count=${import_count:-0}
        
        # Monimutkaisuusarvio
        complexity_score=0
        if [ "$line_count" -gt 300 ]; then
            complexity_score=$((complexity_score + 2))
            FILES_OVER_300=$((FILES_OVER_300 + 1))
        fi
        if [ "$line_count" -gt 500 ]; then
            complexity_score=$((complexity_score + 3))
            FILES_OVER_500=$((FILES_OVER_500 + 1))
        fi
        if [ "$line_count" -gt 700 ]; then
            complexity_score=$((complexity_score + 5))
            FILES_OVER_700=$((FILES_OVER_700 + 1))
        fi
        if [ "$total_functions" -gt 10 ]; then
            complexity_score=$((complexity_score + 2))
        fi
        if [ "$import_count" -gt 8 ]; then
            complexity_score=$((complexity_score + 1))
        fi
        
        echo "$file|$line_count|$class_count|$function_count|$import_count|$complexity_score" >> "$TEMP_FILE"
        
        TOTAL_FILES=$((TOTAL_FILES + 1))
        TOTAL_LINES=$((TOTAL_LINES + line_count))
        
        if [ "$complexity_score" -ge 4 ]; then
            COMPLEX_FILES=$((COMPLEX_FILES + 1))
        fi
    fi
done <<< "$PYTHON_FILES"

if [ "$TOTAL_FILES" -eq 0 ]; then
    echo "❌ Ei käsiteltäviä Python-tiedostoja löytynyt!"
    rm -f "$TEMP_FILE"
    exit 1
fi

sort -t'|' -k6,6nr -k2,2nr "$TEMP_FILE" > "${TEMP_FILE}.sorted"
mv "${TEMP_FILE}.sorted" "$TEMP_FILE"

AVG_FILE_SIZE=$((TOTAL_LINES / TOTAL_FILES))

cat >> "$REPORT_FILE" << EOF
| Analyysitiedostoja | $TOTAL_FILES |
| Yhteensä rivejä | $TOTAL_LINES |
| Tiedostoja yli 300 riviä | $FILES_OVER_300 |
| Tiedostoja yli 500 riviä | $FILES_OVER_500 |
| Tiedostoja yli 700 riviä | $FILES_OVER_700 |
| Monimutkaisia tiedostoja | $COMPLEX_FILES |
| Keskimääräinen tiedoston koko | $AVG_FILE_SIZE riviä |

## 🚨 SUOSITELLUT TIEDOSTOT HAJAUTETTAVAKSI

Seuraavat tiedostot ovat erityisen monimutkaisia ja niiden hajauttaminen parantaisi ylläpidettävyyttä:
EOF

cat > "$SUMMARY_FILE" << EOF
Modulaarisen Hajautuksen Analyysi - Yhteenveto
$(date)

Suositellut tiedostot hajautettavaksi:
EOF

count=0
while IFS='|' read -r file line_count class_count function_count import_count complexity_score && [ $count -lt 15 ]; do
    if [ "$complexity_score" -ge 4 ]; then
        count=$((count + 1))
        rel_path="${file#$PROJECT_ROOT/}"
        filename=$(basename "$file")
        
        if [ "$line_count" -gt 700 ]; then
            priority="🔴 KORKEA"
            action="Hajauta välittömästi useisiin moduuleihin"
        elif [ "$line_count" -gt 500 ]; then
            priority="🟠 KESKIKORKEA"
            action="Suunnittele hajautus seuraavaksi"
        else
            priority="🟡 MEDIUM"
            action="Harkitse hajautusta tulevaisuudessa"
        fi
        
        case "$filename" in
            "manage_parties.py")
                suggestion="Hajauta: party_commands.py, party_verification.py, party_analytics.py"
                ;;
            "manage_questions.py")
                suggestion="Hajauta: question_commands.py, question_manager.py, question_validation.py"
                ;;
            "manage_candidates.py")
                suggestion="Hajauta: candidate_commands.py, candidate_manager.py, candidate_verification.py"
                ;;
            "manage_answers.py")
                suggestion="Hajauta: answer_commands.py, answer_manager.py, answer_validation.py"
                ;;
            "voting_engine.py")
                suggestion="Hajauta: voting_core.py, session_manager.py, results_calculator.py"
                ;;
            "ipfs_sync.py")
                suggestion="Hajauta: sync_orchestrator.py, delta_manager.py, archive_manager.py"
                ;;
            "template_manager.py")
                suggestion="Hajauta: template_commands.py, template_generator.py, template_validator.py"
                ;;
            *)
                suggestion="Hajauta loogisesti toiminnallisuuksien mukaan"
                ;;
        esac
        
        cat >> "$REPORT_FILE" << EOF

### $priority - $rel_path

- **Rivit**: $line_count
- **Luokat**: $class_count
- **Funktiot**: $function_count  
- **Importit**: $import_count
- **Monimutkaisuuspisteet**: $complexity_score/10
- **Toiminta**: $action
- **Ehdotus**: $suggestion

EOF

        echo "$count. $rel_path ($line_count riviä) - $action" >> "$SUMMARY_FILE"
    fi
done < "$TEMP_FILE"

cat >> "$REPORT_FILE" << EOF

## 💡 HAJAUTUSSTRATEGIA

### Yleiset periaatteet
1. **Single Responsibility**: Jokaisella moduulilla yksi vastuualue
2. **Looginen ryhmittely**: Saman toiminnallisuuden funktiot samaan tiedostoon
3. **Minimaaliset riippuvuudet**: Vähennä riippuvuuksia muiden moduulien välillä
4. **Yhteensopivuus**: Säilytä takaisin yhteensopivat rajapinnat

### Hajautuksen vaiheet
1. **Analysoi**: Tunnista toiminnalliset kokonaisuudet tiedostossa
2. **Erota**: Luo uudet moduulit eri toiminnallisuuksille
3. **Refaktoroi**: Siirrä koodi uusien moduulien alle
4. **Testaa**: Varmista että kaikki testit menevät läpi
5. **Dokumentoi**: Päivitä dokumentaatio uusista moduuleista

### Esimerkki: manage_parties.py → modulaarinen rakenne
\`\`\`
src/cli/party_commands.py      # Peruskomennot (add, remove, list)
src/cli/party_verification.py  # Hajautettu vahvistuslogiikka
src/cli/party_analytics.py     # Tilastot ja analytiikka
src/managers/party_manager.py  # Ydinlogiikka (jos ei CLI-pohjainen)
\`\`\`

## 📊 NYKYISEN TILANTEEN ANALYYSI

- **Liian pitkät tiedostot** hidastavat kehitystä ja lisäävät virhealttiutta
- **Monitoiminnallisuus** yhdessä tiedostossa vaikeuttaa ymmärtämistä
- **Riippuvuuksien hallinta** on haastavaa suurissa tiedostoissa
- **Testattavuus** kärsii, kun yksi tiedosto tekee liikaa

## 🎯 SEURAAVAT ASKELEET

1. **Aloita korkean prioriteetin tiedostoista** (700+ riviä)
2. **Toteuta yksi hajautus kerrallaan** ja varmista testien läpimeno
3. **Päivitä dokumentaatio** jokaisen hajautuksen jälkeen
4. **Pidä rajapinnat yhteensopivia** vanhan koodin kanssa
5. **Mittaa vaikutus** koodin laatuun ja kehitysnopeuteen

## 📈 ODOTETUT HYÖDYT

- ✅ **Parantunut ylläpidettävyys** - Pienemmät tiedostot on helpompi ylläpitää
- ✅ **Parantunut testattavuus** - Yksittäisiä toiminnallisuuksia on helpompi testata
- ✅ **Vähemmän konflikteja** - Useat kehittäjät voivat työskennellä eri moduuleissa
- ✅ **Selkeämpi arkkitehtuuri** - Koodi on helpompi lukea ja ymmärtää
- ✅ **Nopeampi kehitys** - Fokusoidut moduulit nopeuttavat toiminnallisuuden lisäämistä

---

*Generoitu automaattisesti skriptillä \`module_splitting_analyzer.sh\`*
*Analyysin perusteella $FILES_OVER_300 tiedostoa yli 300 rivin rajan, $FILES_OVER_500 tiedostoa yli 500 rivin rajan*
EOF

rm -f "$TEMP_FILE"

echo ""
echo "✅ ANALYYSI VALMIS!"
echo "=================="
echo ""
echo "📈 TILASTOT:"
echo "   • Tiedostoja yli 300 riviä: $FILES_OVER_300"
echo "   • Tiedostoja yli 500 riviä: $FILES_OVER_500" 
echo "   • Tiedostoja yli 700 riviä: $FILES_OVER_700"
echo "   • Monimutkaisia tiedostoja: $COMPLEX_FILES"
echo ""
echo "📄 TULOKSET:"
echo "   • Yksityiskohtainen raportti: $REPORT_FILE"
echo "   • Tiivis yhteenveto: $SUMMARY_FILE"
echo ""
echo "💡 SUOSITUS:"
if [ "$FILES_OVER_700" -gt 0 ]; then
    echo "   Aloita välittömästi tiedostoista, joissa on yli 700 riviä"
elif [ "$FILES_OVER_500" -gt 0 ]; then
    echo "   Suunnittele hajautus seuraavaksi tiedostoille yli 500 rivin"
else
    echo "   Projektisi on jo hyvin modulaarinen - hienoa työtä!"
fi
echo ""
echo "🚀 SEURAAVAT VAIHEET:"
echo "   1. Tarkastele $REPORT_FILE"
echo "   2. Valitse ensimmäinen tiedosto hajautettavaksi"
echo "   3. Toteuta hajautus ja testaa minuutti kerrallaan"
