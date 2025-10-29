find . \                    # Etsi nykyisestä hakemistosta
  -name "*.py" \           # Kaikki .py tiedostot
  -not -path "./venv/*" \  # Älä sisällytä ./venv/ hakemistoa
  -not -path "*/venv/*" \  # Älä sisällytä mitään venv/ hakemistoja
  -exec sh -c '            # Suorita komento jokaiselle tiedostolle
    for file; do           # Käy läpi kaikki tiedostot
      echo "=== FILE: $file ==="    # Tulosta tiedostonimi otsikkona
      cat "$file"                   # Näytä tiedoston sisältö
      echo ""                       # Tyhjä rivi
      echo "=== END OF: $file ==="  # Loppumerkintä
      echo ""                       # Tyhjä rivi tiedostojen väliin
    done
  ' sh {} + \              # Lähetä kaikki tiedostot kerralla
  > all_python_files.txt   # Tallenna kaikki yhteen tiedostoon
