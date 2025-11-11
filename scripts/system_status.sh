#!/bin/bash

echo "🏛️  JUMALTENVAALIT 2026 - JÄRJESTELMÄTILA"
echo "=========================================="

# Tarkista virtuaaliympäristö
if [ -d "venv" ]; then
    echo "✅ Virtuaaliympäristö: AKTIIVINEN"
else
    echo "❌ Virtuaaliympäristö: PUUTTUU"
fi

# Tarkista data-tiedostot
echo ""
echo "📁 DATA-TIEDOSTOT:"
for file in data/runtime/*.json; do
    if [ -f "$file" ]; then
        count=$(jq '.[] | length' "$file" 2>/dev/null || echo "N/A")
        echo "  📄 $(basename $file): $count kpl"
    fi
done

# Kysymysten tilasto
if [ -f "data/runtime/questions.json" ]; then
    total_questions=$(jq '.questions | length' data/runtime/questions.json)
    avg_rating=$(jq '[.questions[].elo_rating.current_rating] | add / length' data/runtime/questions.json)
    echo ""
    echo "❓ KYSYMYKSET:"
    echo "  📊 Yhteensä: $total_questions kysymystä"
    echo "  ⭐ Keskimääräinen luokitus: $avg_rating"
fi

# Ehdokkaiden tilasto
if [ -f "data/runtime/candidates.json" ]; then
    total_candidates=$(jq '.candidates | length' data/runtime/candidates.json)
    echo ""
    echo "👑 EHDOKKAAT:"
    echo "  📊 Yhteensä: $total_candidates ehdokasta"
    jq -r '.candidates[] | "  🏷️  \(.basic_info.name.fi) (\(.basic_info.party))"' data/runtime/candidates.json
fi

echo ""
echo "🎯 SEURAAVAT VAIHEET:"
echo "  python src/cli/compare_questions.py --election Jumaltenvaalit2026"
echo "  python src/cli/manage_questions.py --election Jumaltenvaalit2026 --add"
