#!/bin/bash
# core_voting_code_collector.sh - Kerää kaikki vaalikoneen ydinkoodin yhteen tiedostoon

set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="../docs/core_voting_code_documentation_${TIMESTAMP}.txt"
echo "🗳️ Kerätään VAALIKONEEN YDINKOODI tiedostoon: $OUTPUT_FILE"
echo "Tämä tiedosto sisältää kaikki vaalikoneen ytimen ja ehdokkaiden hallinnan Python- ja JSON-tiedostot" > "$OUTPUT_FILE"
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

echo "🎯 VOTING ENGINE CORE" >> "$OUTPUT_FILE"
echo "=====================" >> "$OUTPUT_FILE"
add_file "../src/cli/voting_engine.py" "VOTING ENGINE - Core voting logic"
add_file "../src/managers/elo_manager.py" "ELO MANAGER - Question rating system"
add_file "../src/managers/question_manager.py" "QUESTION MANAGER - Question lifecycle"

echo "" >> "$OUTPUT_FILE"
echo "📊 ELO RATING SYSTEM" >> "$OUTPUT_FILE"
echo "===================" >> "$OUTPUT_FILE"
add_file "../src/cli/compare_questions.py" "COMPARE QUESTIONS CLI - ELO rating interface"
add_file "../src/cli/elo_admin.py" "ELO ADMIN CLI - ELO system administration"

echo "" >> "$OUTPUT_FILE"
echo "👥 CANDIDATE MANAGEMENT" >> "$OUTPUT_FILE"
echo "=======================" >> "$OUTPUT_FILE"
add_file "../src/cli/manage_candidates.py" "MANAGE CANDIDATES CLI - Candidate administration"
add_file "../src/cli/manage_answers.py" "MANAGE ANSWERS CLI - Answer management"
add_file "../src/cli/answer_validation.py" "ANSWER VALIDATION - Answer integrity checking"
add_file "../src/cli/link_candidate_to_party.py" "LINK CANDIDATE TO PARTY - Candidate-party relationships"

echo "" >> "$OUTPUT_FILE"
echo "❓ QUESTION MANAGEMENT" >> "$OUTPUT_FILE"
echo "=====================" >> "$OUTPUT_FILE"
add_file "../src/cli/manage_questions.py" "MANAGE QUESTIONS CLI - Question administration"

echo "" >> "$OUTPUT_FILE"
echo "📁 RUNTIME DATA STRUCTURES" >> "$OUTPUT_FILE"
echo "==========================" >> "$OUTPUT_FILE"
add_file "../data/runtime/questions.json" "QUESTIONS DATA EXAMPLE - Active questions"
add_file "../data/runtime/candidates.json" "CANDIDATES DATA EXAMPLE - Registered candidates"
add_file "../data/runtime/candidate_answers.json" "CANDIDATE ANSWERS EXAMPLE - Candidate responses"
add_file "../data/runtime/meta.json" "META DATA EXAMPLE - System metadata"
add_file "../data/runtime/system_chain.json" "SYSTEM CHAIN EXAMPLE - Change history"

echo "" >> "$OUTPUT_FILE"
echo "📊 VOTING SYSTEM METRICS" >> "$OUTPUT_FILE"
echo "========================" >> "$OUTPUT_FILE"
echo "Total voting system files: $(grep -c "FILE:" "$OUTPUT_FILE")" >> "$OUTPUT_FILE"
echo "Files found: $(grep -c "FILE:" "$OUTPUT_FILE")" >> "$OUTPUT_FILE"
echo "Files missing: $(grep -c "FILE NOT FOUND" "$OUTPUT_FILE")" >> "$OUTPUT_FILE"

echo "✅ Vaalikoneen ydinkoodi kerätty tiedostoon: $OUTPUT_FILE"
echo "📊 Koot: $(wc -l < "$OUTPUT_FILE") lines, $(du -h "$OUTPUT_FILE" | cut -f1)"
echo "📁 Sisältää: $(grep -c "FILE:" "$OUTPUT_FILE") tiedostoa"
