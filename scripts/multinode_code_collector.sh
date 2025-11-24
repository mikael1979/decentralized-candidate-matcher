#!/bin/bash
# multinode_code_collector.sh - Kerää kaikki multi-node toiminnallisuuden koodin yhteen tiedostoon

set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="../docs/multinode_code_documentation_${TIMESTAMP}.txt"
echo "🔗 Kerätään MONINODE-KOODI tiedostoon: $OUTPUT_FILE"
echo "Tämä tiedosto sisältää kaikki multi-node toiminnallisuuteen liittyvät Python- ja JSON-tiedostot" > "$OUTPUT_FILE"
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

echo "🏗️ NODE CORE ARCHITECTURE" >> "$OUTPUT_FILE"
echo "=========================" >> "$OUTPUT_FILE"
add_file "../src/managers/quorum_manager.py" "QUORUM MANAGER - Distributed consensus and voting"
add_file "../src/nodes/node_manager.py" "NODE MANAGER - Node lifecycle management"
add_file "../src/nodes/network_sync.py" "NETWORK SYNC - Node synchronization"

echo "" >> "$OUTPUT_FILE"
echo "🆔 NODE IDENTITY & DISCOVERY" >> "$OUTPUT_FILE"
echo "============================" >> "$OUTPUT_FILE"
add_file "../src/nodes/core/node_identity.py" "NODE IDENTITY - Unique node identification"
add_file "../src/nodes/discovery/peer_discovery.py" "PEER DISCOVERY - Network node discovery"

echo "" >> "$OUTPUT_FILE"
echo "🗳️ QUORUM & CONSENSUS" >> "$OUTPUT_FILE"
echo "====================" >> "$OUTPUT_FILE"
add_file "../src/nodes/quorum_voting.py" "QUORUM VOTING - Distributed voting mechanism"
add_file "../src/nodes/protocols/consensus.py" "CONSENSUS PROTOCOL - Agreement protocols"
add_file "../src/nodes/protocols/message_protocol.py" "MESSAGE PROTOCOL - Inter-node communication"

echo "" >> "$OUTPUT_FILE"
echo "🛠️ NODE MANAGEMENT CLI" >> "$OUTPUT_FILE"
echo "======================" >> "$OUTPUT_FILE"
add_file "../src/cli/node_management.py" "NODE MANAGEMENT CLI - Node administration tools"
add_file "../src/cli/enhanced_party_verification.py" "ENHANCED PARTY VERIFICATION - Media-based party verification"
add_file "../src/cli/manage_parties.py" "PARTY MANAGEMENT CLI - Party administration"

echo "" >> "$OUTPUT_FILE"
echo "⚙️ NODE CONFIGURATION" >> "$OUTPUT_FILE"
echo "====================" >> "$OUTPUT_FILE"
add_file "../config/worker_config.json" "WORKER NODE CONFIG - Worker node settings"
add_file "../base_templates/elections/elections_list.base.json" "ELECTIONS LIST TEMPLATE - Multi-election support"
add_file "../data/nodes/Jumaltenvaalit2026_nodes.json" "NODE REGISTRY EXAMPLE - Active nodes registry"

echo "" >> "$OUTPUT_FILE"
echo "📊 MULTI-NODE METRICS" >> "$OUTPUT_FILE"
echo "====================" >> "$OUTPUT_FILE"
echo "Total multi-node files: $(grep -c "FILE:" "$OUTPUT_FILE")" >> "$OUTPUT_FILE"
echo "Files found: $(grep -c "FILE:" "$OUTPUT_FILE")" >> "$OUTPUT_FILE"
echo "Files missing: $(grep -c "FILE NOT FOUND" "$OUTPUT_FILE")" >> "$OUTPUT_FILE"

echo "✅ Multi-node koodi kerätty tiedostoon: $OUTPUT_FILE"
echo "📊 Koot: $(wc -l < "$OUTPUT_FILE") lines, $(du -h "$OUTPUT_FILE" | cut -f1)"
echo "📁 Sisältää: $(grep -c "FILE:" "$OUTPUT_FILE") tiedostoa"
