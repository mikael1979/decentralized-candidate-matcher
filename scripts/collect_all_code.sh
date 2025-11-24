#!/bin/bash
# collect_all_code.sh - Master-skripti joka kerää kaiken koodin kerralla

set -e

echo "🏛️ KERÄÄ KAIKKI KOODIT YHTEEN"
echo "============================="
echo ""

TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Funktio skriptin suorittamiseen
run_collector() {
    local collector_script="$1"
    local description="$2"
    
    echo "📚 Suoritetaan: $description"
    if [ -f "$collector_script" ]; then
        ./"$collector_script"
        echo "✅ $description valmis"
    else
        echo "❌ Skriptiä ei löydy: $collector_script"
    fi
    echo ""
}

# Suorita kaikki kerääjät
run_collector "security_code_collector.sh" "Tietoturvakoodin kerääminen"
run_collector "multinode_code_collector.sh" "Multi-node koodin kerääminen"
run_collector "templates_code_collector.sh" "Template-koodin kerääminen"
run_collector "core_voting_code_collector.sh" "Vaalikoneen ydinkoodin kerääminen"

# Yhteenveto
echo "🎉 KAIKKI KOODIT KERÄTTY!"
echo "========================"
echo ""
echo "📁 Tulostiedostot hakemistossa: ../docs/"
echo ""
echo "📊 YHTEENVETO:"
ls -la ../docs/ | grep "code_documentation.*${TIMESTAMP}" | while read line; do
    filename=$(echo "$line" | awk '{print $9}')
    size=$(echo "$line" | awk '{print $5}')
    lines=$(wc -l < "../docs/$filename" 2>/dev/null || echo "0")
    echo "   • $filename: $lines lines, $(echo "scale=1; $size/1024" | bc)KB"
done
echo ""
echo "💡 KÄYTTÖOHJEET:"
echo "   Voit lähettää nämä tiedostot AI:lle analysoitavaksi tai"
echo "   käyttää niitä kattavana dokumentaationa."
echo ""
echo "🚀 SEURAAVAT ASKELEET:"
echo "   • Tarkastele tiedostoja: less ../docs/security_code_documentation_${TIMESTAMP}.txt"
echo "   • Arkistoi: tar -czf code_collection_${TIMESTAMP}.tar.gz ../docs/*_code_documentation_${TIMESTAMP}.txt"
