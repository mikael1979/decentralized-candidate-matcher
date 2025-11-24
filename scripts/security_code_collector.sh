#!/bin/bash
# security_code_collector.sh - Kerää kaikki tietoturvaan liittyvän koodin yhteen tiedostoon

set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="../docs/security_code_documentation_${TIMESTAMP}.txt"
echo "🔒 Kerätään TURVAKOODI tiedostoon: $OUTPUT_FILE"
echo "Tämä tiedosto sisältää kaikki tietoturvaan liittyvät Python- ja JSON-tiedostot" > "$OUTPUT_FILE"
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

echo "🧩 CRYPTOGRAPHY & PKI MODULES" >> "$OUTPUT_FILE"
echo "=============================" >> "$OUTPUT_FILE"
add_file "../src/managers/crypto_manager.py" "CRYPTOGRAPHY MANAGER - PKI key management and digital signatures"
add_file "../src/managers/candidate_key_manager.py" "CANDIDATE KEY MANAGER - Candidate credential management"

echo "" >> "$OUTPUT_FILE"
echo "🔐 DATA VALIDATION & INTEGRITY" >> "$OUTPUT_FILE"
echo "==============================" >> "$OUTPUT_FILE"
add_file "../src/core/data_validator.py" "DATA VALIDATOR - Data integrity and validation"
add_file "../src/core/error_handling.py" "ERROR HANDLING - Security error handling"

echo "" >> "$OUTPUT_FILE"
echo "🛡️ SECURE ANSWER MANAGEMENT" >> "$OUTPUT_FILE"
echo "===========================" >> "$OUTPUT_FILE"
add_file "../src/managers/secure_answer_manager.py" "SECURE ANSWER MANAGER - Protected answer storage"
add_file "../src/managers/enhanced_party_verification.py" "ENHANCED PARTY VERIFICATION - Media-based verification"

echo "" >> "$OUTPUT_FILE"
echo "📜 SECURITY TEMPLATES & CONFIG" >> "$OUTPUT_FILE"
echo "==============================" >> "$OUTPUT_FILE"
add_file "../base_templates/system/trusted_sources.base.json" "TRUSTED SOURCES TEMPLATE - Media verification sources"
add_file "../config/system/default_colors.json" "DEFAULT COLORS CONFIG - System color scheme"
add_file "../config/install_config.example.json" "INSTALL CONFIG EXAMPLE - Security configuration template"

echo "" >> "$OUTPUT_FILE"
echo "🔍 SECURITY TESTING" >> "$OUTPUT_FILE"
echo "==================" >> "$OUTPUT_FILE"
add_file "../tests/unit/test_crypto_manager.py" "CRYPTO MANAGER TESTS"
add_file "../tests/unit/test_data_validator.py" "DATA VALIDATOR TESTS"

echo "" >> "$OUTPUT_FILE"
echo "📊 SECURITY METRICS" >> "$OUTPUT_FILE"
echo "===================" >> "$OUTPUT_FILE"
echo "Total security-related files: $(grep -c "FILE:" "$OUTPUT_FILE")" >> "$OUTPUT_FILE"
echo "Files found: $(grep -c "FILE:" "$OUTPUT_FILE")" >> "$OUTPUT_FILE"
echo "Files missing: $(grep -c "FILE NOT FOUND" "$OUTPUT_FILE")" >> "$OUTPUT_FILE"

echo "✅ Tietoturvakoodi kerätty tiedostoon: $OUTPUT_FILE"
echo "📊 Koot: $(wc -l < "$OUTPUT_FILE") lines, $(du -h "$OUTPUT_FILE" | cut -f1)"
echo "📁 Sisältää: $(grep -c "FILE:" "$OUTPUT_FILE") tiedostoa"
