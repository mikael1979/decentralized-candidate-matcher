#!/bin/bash

echo "🏛️  Asennetaan Jumaltenvaalit 2026 -järjestelmää..."

# Tarkista ympäristö
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 tarvitaan"
    exit 1
fi

# Luo virtuaaliympäristö
echo "📦 Luodaan virtuaaliympäristö..."
python3 -m venv venv
source venv/bin/activate

# Asenna riippuvuudet
echo "📚 Asennetaan riippuvuudet..."
pip install click

# Luo data-hakemistot
echo "📁 Luodaan hakemistorakenne..."
mkdir -p data/{tmp,runtime,backup} logs

# Asenna Jumaltenvaalit
echo "⚡ Asennetaan Jumaltenvaalit 2026..."
python src/cli/install.py --election-id Jumaltenvaalit2026 --first-install

# Lisää esimerkkidataa
echo "🎯 Lisätään esimerkkidataa..."
python src/cli/manage_questions.py --election Jumaltenvaalit2026 --add --category "hallinto" --question-fi "Pitäisikö Zeusin salamaniskuoikeuksia rajoittaa?"
python src/cli/manage_candidates.py --election Jumaltenvaalit2026 --add --name "Zeus" --party "Olympolaiset"

echo ""
echo "✅ Jumaltenvaalit 2026 asennettu!"
echo ""
echo "🎯 Järjestelmä valmis! Seuraavat komennot:"
echo "   source venv/bin/activate"
echo "   python src/cli/manage_questions.py --election Jumaltenvaalit2026 --add --category 'aihe' --question-fi 'Kysymys?'"
echo "   python src/cli/manage_candidates.py --election Jumaltenvaalit2026 --add --name 'Nimi' --party 'Puolue'"
echo ""
echo "🏛️  May the gods be with you!"
