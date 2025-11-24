#!/bin/bash
# templates_code_collector.sh - Kerää kaikki template-järjestelmän koodin yhteen tiedostoon

set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="../docs/templates_code_documentation_${TIMESTAMP}.txt"
echo "🎨 Kerätään TEMPLATE-KOODI tiedostoon: $OUTPUT_FILE"
echo "Tämä tiedosto sisältää kaikki template-järjestelmään liittyvät Python- ja JSON-tiedostot" > "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "==========================================" >> "$OUTPUT_FILE"
echo "GENERATION TIMESTAMP: $(date)" >> "$OUTPUT_FILE"
echo "GIT BRANCH: $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')" >> "$OUTPUT_FILE"
echo "PROJECT: Hajautettu Vaalikone - Jumaltenvaalit2026" >> "$OUTPUT_FILE"
echo "==========================================" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Funktio tiedoston lisäämiseen tulostiedostoon
add_file() {
    local file_path="$1"
    local title="$2"
    
    echo "" >> "$OUTPUT_FILE"
    echo "==========================================" >> "$OUTPUT_FILE"
    echo "FILE: $title" >> "$OUTPUT_FILE"
    echo "PATH: $file_path" >> "$OUTPUT_FILE"
    if [ -f "$file_path" ]; then
        echo "SIZE: $(wc -l < "$file_path") lines, $(du -h "$file_path" | cut -f1)" >> "$OUTPUT_FILE"
        echo "MODIFIED: $(date -r "$file_path" +%Y-%m-%d\ %H:%M:%S)" >> "$OUTPUT_FILE"
    else
        echo "STATUS: ⚠️  FILE NOT FOUND" >> "$OUTPUT_FILE"
    fi
    echo "==========================================" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    if [ -f "$file_path" ]; then
        cat "$file_path" >> "$OUTPUT_FILE"
    else
        echo "⚠️  FILE NOT FOUND: $file_path" >> "$OUTPUT_FILE"
        echo "This file is referenced in documentation but doesn't exist in current project structure." >> "$OUTPUT_FILE"
    fi
    echo "" >> "$OUTPUT_FILE"
}

echo "🔄 TEMPLATE ENGINE CORE" >> "$OUTPUT_FILE"
echo "======================" >> "$OUTPUT_FILE"
add_file "../src/templates/html_generator.py" "HTML GENERATOR - Dynamic HTML profile generation"
add_file "../src/templates/css_generator.py" "CSS GENERATOR - Theme-based CSS generation"
add_file "../src/templates/template_manager.py" "TEMPLATE MANAGER - Template lifecycle management"
add_file "../src/templates/template_utils.py" "TEMPLATE UTILS - Template helper functions"

echo "" >> "$OUTPUT_FILE"
echo "📄 BASE TEMPLATES (JSON STRUCTURES)" >> "$OUTPUT_FILE"
echo "==================================" >> "$OUTPUT_FILE"
add_file "../base_templates/questions/questions.base.json" "QUESTIONS TEMPLATE - Question data structure"
add_file "../base_templates/candidates/candidates.base.json" "CANDIDATES TEMPLATE - Candidate data structure"
add_file "../base_templates/parties/parties.base.json" "PARTIES TEMPLATE - Party data structure"
add_file "../base_templates/elections/install_config.base.json" "INSTALL CONFIG TEMPLATE - Election configuration"
add_file "../base_templates/system/system_chain.base.json" "SYSTEM CHAIN TEMPLATE - Change history structure"
add_file "../base_templates/system/trusted_sources.base.json" "TRUSTED SOURCES TEMPLATE - Media verification sources"

echo "" >> "$OUTPUT_FILE"
echo "🛠️ TEMPLATE MANAGEMENT CLI" >> "$OUTPUT_FILE"
echo "==========================" >> "$OUTPUT_FILE"
add_file "../src/cli/template_manager.py" "TEMPLATE MANAGER CLI - Template administration"
add_file "../src/cli/generate_profiles.py" "PROFILE GENERATOR - Candidate profile generation"

echo "" >> "$OUTPUT_FILE"
echo "🔧 TEMPLATE TOOLS & UTILITIES" >> "$OUTPUT_FILE"
echo "=============================" >> "$OUTPUT_FILE"
add_file "../src/templates/json_template_manager.py" "JSON TEMPLATE MANAGER - JSON template handling"
add_file "../src/templates/base_templates.py" "BASE TEMPLATES - Core template definitions"

echo "" >> "$OUTPUT_FILE"
echo "📊 TEMPLATE METRICS" >> "$OUTPUT_FILE"
echo "==================" >> "$OUTPUT_FILE"
echo "Total template files: $(grep -c "FILE:" "$OUTPUT_FILE")" >> "$OUTPUT_FILE"
echo "Files found: $(grep -c "FILE:" "$OUTPUT_FILE")" >> "$OUTPUT_FILE"
echo "Files missing: $(grep -c "FILE NOT FOUND" "$OUTPUT_FILE")" >> "$OUTPUT_FILE"
echo "Base templates: $(find ../base_templates -name "*.base.json" | wc -l) JSON templates" >> "$OUTPUT_FILE"

echo "✅ Template-koodi kerätty tiedostoon: $OUTPUT_FILE"
echo "📊 Koot: $(wc -l < "$OUTPUT_FILE") lines, $(du -h "$OUTPUT_FILE" | cut -f1)"
echo "📁 Sisältää: $(grep -c "FILE:" "$OUTPUT_FILE") tiedostoa"
