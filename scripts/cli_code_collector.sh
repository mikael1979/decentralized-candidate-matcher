#!/bin/bash
# cli_code_collector.sh - Kerää kaikki CLI-käyttöliittymän koodin yhteen tiedostoon

set -e

OUTPUT_FILE="cli_code_documentation.txt"
echo "📟 Kerätään CLI-KOODI tiedostoon: $OUTPUT_FILE"
echo "Tämä tiedosto sisältää kaikki CLI-käyttöliittymän Python- ja JSON-tiedostot" > "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "==========================================" >> "$OUTPUT_FILE"
echo "GENERATION TIMESTAMP: $(date)" >> "$OUTPUT_FILE"
echo "GIT BRANCH: $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')" >> "$OUTPUT_FILE"
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
    echo "SIZE: $(du -h "$file_path" 2>/dev/null | cut -f1)" >> "$OUTPUT_FILE"
    echo "MODIFIED: $(date -r "$file_path" 2>/dev/null +%Y-%m-%d\ %H:%M:%S || echo 'unknown')" >> "$OUTPUT_FILE"
    echo "==========================================" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    if [ -f "$file_path" ]; then
        cat "$file_path" >> "$OUTPUT_FILE"
    else
        echo "⚠️  FILE NOT FOUND: $file_path" >> "$OUTPUT_FILE"
    fi
    echo "" >> "$OUTPUT_FILE"
}

# CLI päämoduulit
add_file "src/cli/base_cli.py" "BASE CLI"
add_file "src/cli/install.py" "INSTALL CLI"
add_file "src/cli/template_manager.py" "TEMPLATE MANAGER CLI"
add_file "src/cli/validate_data.py" "VALIDATE DATA CLI"
add_file "src/cli/cleanup_data.py" "CLEANUP DATA CLI"
add_file "src/cli/publish_election_configs.py" "PUBLISH ELECTION CONFIGS CLI"
add_file "src/cli/system_status.sh" "SYSTEM STATUS SCRIPT"

# Analytics ja raportointi
add_file "src/cli/analytics.py" "ANALYTICS CLI"
add_file "src/cli/party_analytics.py" "PARTY ANALYTICS CLI"
add_file "src/cli/party_stats.py" "PARTY STATS CLI"
add_file "src/managers/analytics_manager.py" "ANALYTICS MANAGER"

# Help ja dokumentaatio
add_file "scripts/generate_code_overview.sh" "CODE OVERVIEW GENERATOR"
add_file "scripts/generate_template_overview.sh" "TEMPLATE OVERVIEW GENERATOR"
add_file "scripts/generate_full_documentation.sh" "FULL DOCUMENTATION GENERATOR"
add_file "scripts/setup_jumaltenvaalit.sh" "SETUP SCRIPT"

# Testit
add_file "tests/run_tests.py" "TEST RUNNER"
add_file "tests/unit/test_cli_commands.py" "CLI COMMANDS TESTS"
add_file "tests/integration/test_analytics_simple.py" "ANALYTICS TESTS"

echo "✅ CLI-koodi kerätty tiedostoon: $OUTPUT_FILE"
echo "📊 Koot: $(du -h "$OUTPUT_FILE" | cut -f1)"
