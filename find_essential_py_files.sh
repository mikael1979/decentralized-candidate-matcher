#!/bin/bash
# find_essential_py_files.sh - LUKEE VAIN OLENNAISET OHJELMATIEDOSTOT

echo "🔍 OLENNAISTEN Python tiedostojen etsintä"
echo "=========================================="

# Käytä ensimmäistä parametria tai oletusarvoa
directory="${1:-./}"

# Tarkista että hakemisto on olemassa
if [ ! -d "$directory" ]; then
  echo "❌ Hakemistoa '$directory' ei löydy!"
  exit 1
fi

echo "📁 Etsitään OLENNAISIA Python tiedostoja hakemistosta: $directory"

# Luettelo tiedostoista jotka SISÄLLYTTÄVÄT (olennaiset)
include_patterns=(
  "manager.py"
  "calculator.py" 
  "sync.py"
  "integrity.py"
  "bootstrap.py"
  "initialization.py"
  "install.py"
  "metadata.py"
  "recovery.py"
  "chain.py"
  "lock.py"
  "enhanced_"
  "complete_"
  "system_"
  "ipfs_"
  "elo_"
  "production"
  "governance"
  "community"
)

# Luettelo tiedostoista jotka OHITETAAN (ei-olennaiset)
exclude_patterns=(
  "test_"
  "_test.py"
  "demo_"
  "mock_"
  "simple_"
  "fix_"
  "clean_"
  "switch_"
  "update_"
  "create_"
  "check_"
  "force_"
  "import_"
  "verify_"
)

# Luo find-komennon ehdot
find_command="find \"$directory\" -name \"*.py\" -not -path \"*/venv/*\""

# Lisää include-ehdot
for pattern in "${include_patterns[@]}"; do
  find_command+=" -o -name \"*${pattern}*\""
done

# Korjaa find-komento (poista ensimmäinen "-o")
find_command=$(echo "$find_command" | sed 's/-name/-name/')

# Lisää exclude-ehdot
for pattern in "${exclude_patterns[@]}"; do
  find_command+=" -not -name \"*${pattern}*\""
done

echo "🔍 Suoritetaan: $find_command"

# Suorita haku ja käsittely
eval $find_command | while read -r file; do
  if [ -f "$file" ]; then
    echo "=== FILE: $file ==="
    cat "$file"
    echo ""
    echo "=== END OF: $file ==="
    echo ""
  fi
done > essential_python_files.txt

# Tulosta tilasto
file_count=$(eval $find_command | wc -l)
line_count=$(wc -l < essential_python_files.txt)

echo "✅ VALMIS!"
echo "📊 Löydetty $file_count OLENNAISTA Python tiedostoa"
echo "📄 Yhteensä $line_count riviä essential_python_files.txt tiedostossa"
echo "📁 Tiedosto: $(pwd)/essential_python_files.txt"

# Näytä löydetyt tiedostot
echo ""
echo "📋 LÖYDETYT TIEDOSTOT:"
eval $find_command | while read -r file; do
  filename=$(basename "$file")
  echo "  ✅ $filename"
done
