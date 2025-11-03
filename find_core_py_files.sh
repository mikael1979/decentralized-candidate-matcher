#!/bin/bash
# find_core_py_files.sh - LUKEE VAIN YDINOHJELMATIEDOSTOT

echo "🔍 YDINOHJELMIEN Python tiedostojen etsintä"
echo "============================================"

# Whitelist - vain nämä tiedostot sisällytetään
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
)

directory="${1:-./}"

if [ ! -d "$directory" ]; then
  echo "❌ Hakemistoa '$directory' ei löydy!"
  exit 1
fi

echo "📁 Etsitään YDINOHJELMATIEDOSTOJA hakemistosta: $directory"

> core_python_files.txt

found_count=0

for core_file in "${core_files[@]}"; do
  file_path=$(find "$directory" -name "$core_file" -not -path "*/venv/*" | head -1)
  
  if [ -n "$file_path" ] && [ -f "$file_path" ]; then
    echo "=== FILE: $file_path ===" >> core_python_files.txt
    cat "$file_path" >> core_python_files.txt
    echo "" >> core_python_files.txt
    echo "=== END OF: $file_path ===" >> core_python_files.txt
    echo "" >> core_python_files.txt
    ((found_count++))
    echo "  ✅ $core_file"
  else
    echo "  ❌ $core_file (ei löytynyt)"
  fi
done

line_count=$(wc -l < core_python_files.txt)

echo ""
echo "✅ VALMIS!"
echo "📊 Löydetty $found_count / ${#core_files[@]} ydinohjelmatiedostoa"
echo "📄 Yhteensä $line_count riviä core_python_files.txt tiedostossa"
echo "📁 Tiedosto: $(pwd)/core_python_files.txt"
