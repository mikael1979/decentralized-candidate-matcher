#!/bin/bash
# find_core_py_files.sh - PÄIVITETTY: Etsii todelliset ydinmoduulit

echo "🔍 YDIN- JA MODUULIEN Python tiedostojen etsintä - TODELLINEN RAKENNE"
echo "=================================================================="

# === 1. Whitelist - todelliset ydintiedostot ===
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
  "ipfs_schedule_manager.py"
  "mock_ipfs.py"
)

# === 2. CLI ja Hallintatyökalut ===
cli_files=(
  "cli/cli_template.py"
)

# === 3. Unified Handlers ===
manager_files=(
  "managers/unified_question_handler.py"
  "managers/unified_system_chain.py"
)

# === 4. Domain moduulit ===
domain_files=(
  "domain/entities/question.py"
  "domain/entities/election.py"
  "domain/value_objects/value_objects.py"
  "domain/repositories/question_repository.py"
  "domain/repositories/election_repository.py"
  "domain/services/rating_calculation.py"
)

# === 5. Application moduulit ===
application_files=(
  "application/commands/commands.py"
  "application/services/question_service.py"
  "application/use_cases/submit_question/submit_question.py"
  "application/use_cases/sync_questions/sync_questions.py"
  "application/use_cases/process_rating/process_rating.py"
  "application/query_handlers/question_queries.py"
  "application/queries/queries.py"
)

# === 6. Infrastructure moduulit ===
infrastructure_files=(
  "infrastructure/config/config_manager.py"
  "infrastructure/logging/system_logger.py"
  "infrastructure/repositories/json_question_repository.py"
  "infrastructure/repositories/ipfs_question_repository.py"
  "infrastructure/services/legacy_integration.py"
  "infrastructure/adapters/ipfs_client.py"
  "infrastructure/adapters/block_manager_adapter.py"
)

# === 7. Core moduulit ===
core_files_extra=(
  "core/dependency_container.py"
)

# === 8. UTILITIES - aputyökalut ===
utils_files=(
  "utils/json_utils.py"
  "utils/file_utils.py"
  "utils/ipfs_client.py"
)

# Yhdistetään kaikki tiedostot yhteen listaan
all_files=(
  "${core_files[@]}" 
  "${cli_files[@]}" 
  "${manager_files[@]}" 
  "${domain_files[@]}" 
  "${application_files[@]}" 
  "${infrastructure_files[@]}" 
  "${core_files_extra[@]}" 
  "${utils_files[@]}"
)

directory="${1:-./community_based}"

if [ ! -d "$directory" ]; then
  echo "❌ Hakemistoa '$directory' ei löydy!"
  exit 1
fi

echo "📁 Etsitään ydin- ja moduulitiedostoja hakemistosta: $directory"
echo "🗂️  TODELLINEN Hakemistorakenne:"
echo "   - Core: $(find "$directory" -name "*.py" -maxdepth 1 | wc -l) tiedostoa"
echo "   - CLI: $(find "$directory/cli" -name "*.py" 2>/dev/null | wc -l) tiedostoa"
echo "   - Managers: $(find "$directory/managers" -name "*.py" 2>/dev/null | wc -l) tiedostoa"
echo "   - Domain: $(find "$directory/domain" -name "*.py" 2>/dev/null | wc -l) tiedostoa"
echo "   - Application: $(find "$directory/application" -name "*.py" 2>/dev/null | wc -l) tiedostoa"
echo "   - Infrastructure: $(find "$directory/infrastructure" -name "*.py" 2>/dev/null | wc -l) tiedostoa"
echo "   - Utils: $(find "$directory/utils" -name "*.py" 2>/dev/null | wc -l) tiedostoa"
echo ""

> core_python_files.txt

found_count=0
total_expected=${#all_files[@]}
not_found_files=()

echo "🔍 ETSTÄÄN TIEDOSTOJA:"

for file_spec in "${all_files[@]}"; do
  file_path="$directory/$file_spec"
  
  if [ -f "$file_path" ]; then
    echo "=== FILE: $file_path ===" >> core_python_files.txt
    cat "$file_path" >> core_python_files.txt
    echo "" >> core_python_files.txt
    echo "=== END OF: $file_path ===" >> core_python_files.txt
    echo "" >> core_python_files.txt
    ((found_count++))
    echo "  ✅ $file_spec"
  else
    echo "  ❌ $file_spec (ei löytynyt)"
    not_found_files+=("$file_spec")
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
echo "   Core: ${#core_files[@]} tiedostoa"
echo "   CLI: ${#cli_files[@]} tiedostoa"
echo "   Managers: ${#manager_files[@]} tiedostoa"
echo "   Domain: ${#domain_files[@]} tiedostoa"
echo "   Application: ${#application_files[@]} tiedostoa"
echo "   Infrastructure: ${#infrastructure_files[@]} tiedostoa"
echo "   Core Extra: ${#core_files_extra[@]} tiedostoa"
echo "   Utils: ${#utils_files[@]} tiedostoa"

# Näytä onnistumisprosentti
success_rate=$((found_count * 100 / total_expected))
echo ""
echo "📊 ONNISTUMISPROSENTTI: $success_rate%"

if [ ${#not_found_files[@]} -gt 0 ]; then
  echo ""
  echo "⚠️  PUUTTUVAT TIEDOSTOT ($((total_expected - found_count)) kpl):"
  for missing_file in "${not_found_files[@]}"; do
    echo "   ❌ $missing_file"
  done
else
  echo ""
  echo "🎉 KAIKKI TIEDOSTOT LÖYDETTY!"
fi

# Näytä tiedostokoko ja rivimäärä
echo ""
echo "📦 TIEDOSTON TIEDOT:"
echo "   Koko: $file_size"
echo "   Rivimäärä: $line_count"
echo "   Tiedostoja: $found_count"
