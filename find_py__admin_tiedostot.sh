#!/bin/bash
# find_py_tiedostot.sh - KORJATTU VERSIO

echo "🔍 Python tiedostojen etsintä"
echo "============================="

# Käytä ensimmäistä parametria tai oletusarvoa
directory="${1:-./}"

# Tarkista että hakemisto on olemassa
if [ ! -d "$directory" ]; then
  echo "❌ Hakemistoa '$directory' ei löydy!"
  exit 1
fi

echo "📁 Etsitään Python tiedostoja hakemistosta: $directory"

# Suorita haku
find "$directory" -name "*.py" -not -path "*/venv/*" -exec sh -c '
  for file; do
    echo "=== FILE: $file ==="
    cat "$file"
    echo ""
    echo "=== END OF: $file ==="
    echo ""
  done
' sh {} + > all_admin_based_python_files.txt

# Tulosta tilasto
file_count=$(find "$directory" -name "*.py" -not -path "*/venv/*" | wc -l)
line_count=$(wc -l < all_admin_based_python_files.txt)

echo "✅ VALMIS!"
echo "📊 Löydetty $file_count Python tiedostoa"
echo "📄 Yhteensä $line_count riviä all_python_files.txt tiedostossa"
echo "📁 Tiedosto: $(pwd)/all_admin_based_python_files.txt"
