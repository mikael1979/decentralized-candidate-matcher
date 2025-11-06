#!/bin/bash
# find_core_py_files.sh - Etsii YDIN- ja MODUULItiedostot, ohittaa testit/demo/korjaukset

echo "🔍 YDIN- JA MODUULIEN Python tiedostojen etsintä"
echo "============================================"

# === 1. Whitelist - ydintiedostot (pääohjelmat) ===
core_files=(
  "question_manager.py"
  "complete_elo_calculator.py"
  "elo_manager.py"
  "system_chain_manager.py"
  "enhanced_system_chain_manager.py"
  "ipfs_sync_manager.py"
  "ipfs_block_manager.py"
  "enhanced_integrity_manager.py"
  "production_lock_manager.py"
  "system_bootstrap.py"
  "metadata_manager.py"
  "enhanced_recovery_manager.py"
  "active_questions_manager.py"
  "elections_list_manager.py"
  "install.py"
  "initialization.py"
  "installation_engine.py"
  "manage_questions.py"
  # UUDET CLI-TYÖKALUJEN POHJAT
  "cli/cli_template.py"
  # UNIFIED HANDLERIT
  "managers/unified_question_handler.py"
  "managers/unified_system_chain.py"
)

# === 2. Moduulitiedostot logiikka-kerroksittain ===
domain_files=(
  "domain/entities/question.py"
  "domain/entities/election.py"
  "domain/value_objects.py"
  "domain/events.py"
  "domain/repositories/question_repository.py"
  "domain/repositories/election_repository.py"
  "domain/services/rating_calculation.py"
)

application_files=(
  "application/commands.py"
  "application/queries.py"
  "application/results.py"
  "application/services/question_service.py"
  "application/use_cases/submit_question.py"
  "application/use_cases/sync_questions.py"
  "application/use_cases/process_rating.py"
  "application/query_handlers/question_queries.py"
)

infrastructure_files=(
  "infrastructure/config/config_manager.py"
  "infrastructure/logging/system_logger.py"
  "infrastructure/repositories/json_question_repository.py"
  "infrastructure/repositories/ipfs_question_repository.py"
  "infrastructure/services/legacy_integration.py"
  "infrastructure/adapters/ipfs_client.py"
  "infrastructure/adapters/block_manager_adapter.py"
)

core_files_extra=(
  "core/dependency_container.py"
)

# === 3. UTILITIES - aputyökalut ===
utils_files=(
  "utils/json_utils.py"
  "utils/file_utils.py"
  "utils/ipfs_client.py"
)

# Yhdistetään kaikki tiedostot yhteen listaan
all_files=("${core_files[@]}" "${domain_files[@]}" "${application_files[@]}" "${infrastructure_files[@]}" "${core_files_extra[@]}" "${utils_files[@]}")

directory="${1:-./}"

if [ ! -d "$directory" ]; then
  echo "❌ Hakemistoa '$directory' ei löydy!"
  exit 1
fi

echo "📁 Etsitään ydin- ja moduulitiedostoja hakemistosta: $directory"
echo "🗂️  Hakemistorakenne:"
echo "   - CLI pohjat: cli/"
echo "   - Unified handlers: managers/"
echo "   - Domain logiikka: domain/"
echo "   - Application services: application/"
echo "   - Infrastructure: infrastructure/"
echo "   - Utils: utils/"
echo "   - Core: core/"
echo ""

> core_python_files.txt

found_count=0
total_expected=${#all_files[@]}

for file_spec in "${all_files[@]}"; do
  # Etsi tiedostoa, mutta ohita venv/, tests/, interface/, tmp/
  file_path=$(find "$directory" \
    -name "$(basename "$file_spec")" \
    -not -path "*/venv/*" \
    -not -path "*/tests/*" \
    -not -path "*/interface/*" \
    -not -path "*/__pycache__/*" \
    -not -name "*demo*.py" \
    -not -name "fix_*.py" \
    -not -name "*test*.py" \
    -not -name "*_fixed.py" \
    -not -name "*_old.py" \
    -not -name "*_backup.py" \
    | grep -F "/$(dirname "$file_spec")/" \
    | head -1)
  
  # Fallback: etsi kaikkialta (jos polku ei täsmännyt)
  if [ -z "$file_path" ]; then
    file_path=$(find "$directory" \
      -name "$(basename "$file_spec")" \
      -not -path "*/venv/*" \
      -not -path "*/tests/*" \
      -not -path "*/interface/*" \
      -not -path "*/__pycache__/*" \
      -not -name "*demo*.py" \
      -not -name "fix_*.py" \
      -not -name "*test*.py" \
      -not -name "*_fixed.py" \
      -not -name "*_old.py" \
      -not -name "*_backup.py" \
      | head -1)
  fi
  
  if [ -n "$file_path" ] && [ -f "$file_path" ]; then
    echo "=== FILE: $file_path ===" >> core_python_files.txt
    cat "$file_path" >> core_python_files.txt
    echo "" >> core_python_files.txt
    echo "=== END OF: $file_path ===" >> core_python_files.txt
    echo "" >> core_python_files.txt
    ((found_count++))
    echo "  ✅ $file_spec"
  else
    echo "  ❌ $file_spec (ei löytynyt)"
  fi
done

line_count=$(wc -l < core_python_files.txt)
file_size=$(du -h core_python_files.txt | cut -f1)

echo ""
echo "✅ VALMIS!"
echo "📊 Löydetty $found_count / $total_expected ydin- ja moduulitiedostoa"
echo "📄 Yhteensä $line_count riviä ($file_size) core_python_files.txt tiedostossa"
echo "📁 Tiedosto: $(pwd)/core_python_files.txt"

# Näytä tiedostojen jakauma
echo ""
echo "📈 TIEDOSTOJEN JAKAUMA:"
echo "   CLI & Managers: $(echo "${core_files[@]}" "${utils_files[@]}" | wc -w) tiedostoa"
echo "   Domain: ${#domain_files[@]} tiedostoa"
echo "   Application: ${#application_files[@]} tiedostoa"
echo "   Infrastructure: ${#infrastructure_files[@]} tiedostoa"
echo "   Core: ${#core_files_extra[@]} tiedostoa"
