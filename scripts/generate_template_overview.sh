#!/bin/bash

# Skripti joka kerää kaikki JSON-template tiedostot JSON-muotoiseen listaukseen
# Käyttö: ./scripts/generate_template_overview.sh

set -e

echo "📋 Generoidaan template-listaus..."

OUTPUT_JSON="docs/template_overview_$(date +%Y%m%d_%H%M%S).json"
TEMPLATE_DIR="base_templates"

mkdir -p "$(dirname "$OUTPUT_JSON")"

# Alusta JSON-rakenne
cat > "$OUTPUT_JSON" << EOF
{
  "metadata": {
    "generated": "$(date -Iseconds)",
    "system": "Hajautettu Vaalikone",
    "election": "Jumaltenvaalit2026",
    "total_templates": 0,
    "purpose": "JSON-templatejen kattava listaus ja dokumentaatio"
  },
  "categories": {},
  "templates": []
}
EOF

# Funktio JSONin päivittämiseen
update_json() {
    local temp_file="/tmp/temp_json_$$.json"
    jq "$1" "$OUTPUT_JSON" > "$temp_file" && mv "$temp_file" "$OUTPUT_JSON"
}

# Etsi kaikki JSON-template tiedostot
template_count=0
declare -A categories

find "$TEMPLATE_DIR" -name "*.json" | while read -r template_file; do
    if [ -f "$template_file" ]; then
        echo "📄 Käsitellään: $template_file"
        
        relative_path="${template_file#$TEMPLATE_DIR/}"
        category=$(dirname "$relative_path")
        filename=$(basename "$template_file")
        
        # Päivitä kategoriat
        categories["$category"]=1
        
        # Lue template sisältö (ilmeisesti placeholder dataa)
        file_size=$(stat -c%s "$template_file")
        line_count=$(wc -l < "$template_file")
        
        # Päivitä JSON
        update_json ".templates += [{
          \"file_path\": \"$relative_path\",
          \"category\": \"$category\",
          \"filename\": \"$filename\", 
          \"file_size_bytes\": $file_size,
          \"line_count\": $line_count,
          \"last_modified\": \"$(date -r "$template_file" -Iseconds)\",
          \"placeholder_count\": $(grep -o '{{[^}]*}}' "$template_file" | wc -l),
          \"purpose\": \"$(grep -A2 '\"description\"' "$template_file" | grep -o '\"[^\"]*\"' | head -1 | tr -d '\"' || echo "Template for $category")\"
        }]"
        
        ((template_count++))
    fi
done

# Päivitä metadata
update_json ".metadata.total_templates = $template_count"
update_json ".metadata.categories_count = $(printf '%s\n' "${!categories[@]}" | wc -l)"

# Lisää kategoriat
for category in "${!categories[@]}"; do
    if [ -n "$category" ] && [ "$category" != "." ]; then
        update_json ".categories[\"$category\"] = {}"
    fi
done

# Lisää templatejen käyttötarkoitukset
update_json '.template_purposes = {
  "core": "Järjestelmän ydinmoduulit",
  "system": "Järjestelmän hallinta ja ketju",
  "elections": "Vaali- ja asennuskonfiguraatiot", 
  "questions": "Kysymysten hallinta ja ELO-luokitus",
  "candidates": "Ehdokkaiden tiedot ja profiilit",
  "sync": "IPFS-synkronointi ja aikavaraus",
  "governance": "Hallinto- ja yhteisömallit"
}'

echo "✅ Template-listaus luotu: $OUTPUT_JSON"
echo "📊 Templateja löydetty: $template_count kpl"
