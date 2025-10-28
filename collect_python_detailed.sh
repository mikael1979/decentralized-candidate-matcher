[file name]: collect_python_detailed.sh
[file content begin]
#!/bin/bash

# Yksityiskohtainen Python-koodin kerääjä
# Luo siistin raportin kaikista Python-tiedostoista

OUTPUT_FILE="${1:-python_code_detailed.txt}"
SEARCH_DIR="."

# Värikoodit (valinnainen)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐍 PYTHON-KOODIN KERÄÄJÄ${NC}"
echo -e "${BLUE}========================${NC}"
echo "Hakemisto: $SEARCH_DIR"
echo "Tulostus: $OUTPUT_FILE"
echo ""

# Alusta tulostustiedosto
echo "🐍 PYTHON-KOODIKOKOELMA" > "$OUTPUT_FILE"
echo "======================" >> "$OUTPUT_FILE"
echo "Luotu: $(date)" >> "$OUTPUT_FILE"
echo "Hakemisto: $(pwd)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Etsi ja käsittele Python-tiedostot
file_count=0
total_lines=0

while IFS= read -r -d '' file; do
    # Ohita virtuaaliympäristöt
    if [[ "$file" == *"/env/"* ]] || [[ "$file" == *"/venv/"* ]] || [[ "$file" == *"/.venv/"* ]]; then
        continue
    fi
    
    ((file_count++))
    lines=$(wc -l < "$file")
    ((total_lines+=lines))
    
    echo -e "${GREEN}✅ Käsitellään:${NC} $file (${lines} riviä)"
    
    # Lisää tiedoston otsikko
    {
        echo "┌──────────────────────────────────────────────────────────────┐"
        echo "│ Tiedosto: $(printf "%-52s" "$file") │"
        echo "│ Koko: $(printf "%-6d" $lines) riviä                                        │"
        echo "└──────────────────────────────────────────────────────────────┘"
        echo ""
        
        # Näytä tiedoston sisältö numeroiduilla riveillä
        echo "```python"
        cat -n "$file"
        echo "```"
        echo ""
        echo ""
        
    } >> "$OUTPUT_FILE"
    
done < <(find "$SEARCH_DIR" -name "*.py" -type f -print0)

# Lisää yhteenveto
{
    echo "┌──────────────────────────────────────────────────────────────┐"
    echo "│                          YHTEENVETO                          │"
    echo "├──────────────────────────────────────────────────────────────┤"
    echo "│ Tiedostoja: $(printf "%-8d" $file_count)                                    │"
    echo "│ Rivejä yhteensä: $(printf "%-6d" $total_lines)                                  │"
    echo "│ Keskimäärin: $(printf "%-6.1f" $(echo "scale=1; $total_lines/$file_count" | bc)) riviä/tiedosto                          │"
    echo "│ Luotu: $(date +"%Y-%m-%d %H:%M:%S")                                      │"
    echo "└──────────────────────────────────────────────────────────────┘"
} >> "$OUTPUT_FILE"

echo ""
echo -e "${GREEN}🎉 KERÄYS VALMIS!${NC}"
echo -e "📊 Yhteenveto:"
echo -e "   📁 Tiedostoja: ${YELLOW}$file_count${NC}"
echo -e "   📝 Rivejä: ${YELLOW}$total_lines${NC}"
echo -e "   💾 Tulostiedosto: ${YELLOW}$OUTPUT_FILE${NC}"
echo -e "   📏 Koko: ${YELLOW}$(du -h "$OUTPUT_FILE" | cut -f1)${NC}"
[file content end]
