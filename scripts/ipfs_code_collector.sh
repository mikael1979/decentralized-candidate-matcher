#!/bin/bash
# ipfs_code_collector.sh - Kerää kaikki IPFS-integroinnin koodin yhteen tiedostoon

set -e

OUTPUT_FILE="ipfs_code_documentation.txt"
echo "🌐 Kerätään IPFS-KOODI tiedostoon: $OUTPUT_FILE"
echo "Tämä tiedosto sisältää kaikki IPFS-integrointiin liittyvät Python- ja JSON-tiedostot" > "$OUTPUT_FILE"
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

# IPFS core moduulit
add_file "src/core/ipfs/client.py" "IPFS CLIENT"
add_file "src/core/ipfs/archive_manager.py" "ARCHIVE MANAGER"
add_file "src/core/ipfs/delta_manager.py" "DELTA MANAGER"
add_file "src/core/ipfs/sync_orchestrator.py" "SYNC ORCHESTRATOR"
add_file "src/managers/ipfs_manager.py" "IPFS MANAGER"
add_file "src/managers/ipfs_sync_manager.py" "IPFS SYNC MANAGER"
add_file "src/managers/auto_publisher.py" "AUTO PUBLISHER"

# IPFS CLI-työkalut
add_file "src/cli/ipfs_sync.py" "IPFS SYNC CLI"
add_file "src/cli/generate_profiles.py" "PROFILE GENERATOR"
add_file "src/templates/ipfs_publisher.py" "IPFS PUBLISHER"

# IPFS-testit
add_file "tests/test_ipfs.py" "IPFS TESTS"
add_file "tests/test_ipfs_modular.py" "MODULAR IPFS TESTS"

# IPFS-configuraatiot
add_file "config/system/default_colors.json" "DEFAULT COLORS"
add_file "data/runtime/ipfs_sync.json" "IPFS SYNC STATUS EXAMPLE"

echo "✅ IPFS-koodi kerätty tiedostoon: $OUTPUT_FILE"
echo "📊 Koot: $(du -h "$OUTPUT_FILE" | cut -f1)"
